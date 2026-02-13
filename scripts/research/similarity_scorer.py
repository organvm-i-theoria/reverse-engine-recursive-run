#!/usr/bin/env python3
"""
Similarity Scorer

Calculates similarity scores between discovered repositories
and our organization profile using multiple dimensions:
- Tech stack similarity (Jaccard)
- Problem domain similarity (topics, keywords)
- Scale similarity (size, team, complexity)
- Activity pattern similarity
- Maturity alignment
"""

import json
import argparse
import yaml
import math
from typing import Dict, List, Any, Set
from datetime import datetime


def jaccard_similarity(set1: Set, set2: Set) -> float:
    """Calculate Jaccard similarity between two sets."""
    if not set1 and not set2:
        return 1.0
    if not set1 or not set2:
        return 0.0

    intersection = len(set1 & set2)
    union = len(set1 | set2)

    return intersection / union if union > 0 else 0.0


def normalize_value(value: float, min_val: float, max_val: float) -> float:
    """Normalize value to 0-1 range."""
    if max_val == min_val:
        return 0.5
    return max(0.0, min(1.0, (value - min_val) / (max_val - min_val)))


def calculate_tech_stack_similarity(org_profile: Dict, repo: Dict, weights: Dict) -> float:
    """Calculate technology stack similarity."""
    score = 0.0
    w = weights.get('tech_stack', {})

    # Language similarity
    org_languages = set(org_profile.get('technology', {}).get('languages', {}).keys())
    repo_language = repo.get('language')

    if repo_language and repo_language in org_languages:
        lang_score = 1.0
    else:
        lang_score = 0.0

    score += lang_score * w.get('language_weight', 0.4)

    # Framework similarity (from topics)
    org_frameworks = set()
    for fw_list in org_profile.get('technology', {}).get('frameworks', {}).values():
        for fw in fw_list:
            org_frameworks.add(fw.split('@')[0].lower())

    repo_topics = set([t.lower() for t in repo.get('topics', [])])
    framework_overlap = jaccard_similarity(org_frameworks, repo_topics)
    score += framework_overlap * w.get('framework_weight', 0.35)

    # Tool similarity
    org_tools = set([t.lower() for t in org_profile.get('technology', {}).get('tools', [])])
    tool_overlap = jaccard_similarity(org_tools, repo_topics)
    score += tool_overlap * w.get('tool_weight', 0.25)

    return score


def calculate_domain_similarity(org_profile: Dict, repo: Dict, weights: Dict) -> float:
    """Calculate problem domain similarity."""
    score = 0.0
    w = weights.get('problem_domain', {})

    # Topic similarity
    org_research_areas = set(org_profile.get('challenges', {}).get('research_areas', []))
    repo_topics = set(repo.get('topics', []))

    topic_overlap = jaccard_similarity(org_research_areas, repo_topics)
    score += topic_overlap * w.get('topic_weight', 0.5)

    # Description keyword similarity (simple approach)
    repo_desc = (repo.get('description') or '').lower()
    research_keywords = org_research_areas

    keyword_matches = sum(1 for keyword in research_keywords if keyword in repo_desc)
    keyword_score = min(1.0, keyword_matches / len(research_keywords)) if research_keywords else 0.0

    score += keyword_score * w.get('description_weight', 0.2)

    # README similarity would go here (requires fetching README)
    # For now, use topics as proxy
    score += topic_overlap * w.get('readme_weight', 0.3)

    return score


def calculate_scale_similarity(org_profile: Dict, repo: Dict, weights: Dict) -> float:
    """Calculate scale/size similarity."""
    score = 0.0
    w = weights.get('scale', {})

    # Repository size similarity
    org_loc = org_profile.get('metrics', {}).get('total_lines', 0)
    repo_size_kb = repo.get('size', 0)

    # Rough approximation: 1 KB ≈ 30 lines of code
    repo_loc_estimate = repo_size_kb * 30

    if org_loc > 0:
        size_tolerance = w.get('size_tolerance', 0.5)
        size_ratio = repo_loc_estimate / org_loc

        # Score is 1.0 if within tolerance, decreases outside tolerance
        if size_ratio < 1 - size_tolerance or size_ratio > 1 + size_tolerance:
            size_score = 1.0 - min(1.0, abs(1.0 - size_ratio))
        else:
            size_score = 1.0

        score += size_score * w.get('size_weight', 0.35)
    else:
        score += 0.5 * w.get('size_weight', 0.35)

    # Team size similarity (use stars as proxy for team size)
    # This is a rough approximation
    repo_stars = repo.get('stars', 0)
    if repo_stars > 0:
        # Logarithmic scaling for team size
        team_score = min(1.0, math.log10(repo_stars + 1) / 4)  # Normalize around 10k stars
        score += team_score * w.get('team_size_weight', 0.35)
    else:
        score += 0.2 * w.get('team_size_weight', 0.35)

    # Complexity similarity (hard to estimate without cloning)
    # Use number of topics and size as proxy
    complexity_proxy = min(1.0, (len(repo.get('topics', [])) * repo.get('size', 0)) / 1000)
    score += complexity_proxy * w.get('complexity_weight', 0.3)

    return score


def calculate_activity_similarity(org_profile: Dict, repo: Dict, weights: Dict) -> float:
    """Calculate activity pattern similarity."""
    score = 0.0
    w = weights.get('activity', {})

    # Recent activity (days since last update)
    updated_at = repo.get('updated_at')
    if updated_at:
        try:
            last_update = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
            days_since_update = (datetime.now(last_update.tzinfo) - last_update).days

            # Score higher for recently updated repos
            if days_since_update < 30:
                activity_score = 1.0
            elif days_since_update < 90:
                activity_score = 0.8
            elif days_since_update < 180:
                activity_score = 0.5
            else:
                activity_score = 0.2

            score += activity_score * w.get('commit_frequency_weight', 0.4)
        except:
            score += 0.5 * w.get('commit_frequency_weight', 0.4)

    # Contributor pattern (use forks as proxy)
    forks = repo.get('forks', 0)
    contributor_score = min(1.0, math.log10(forks + 1) / 3)  # Normalize around 1k forks
    score += contributor_score * w.get('contributor_pattern_weight', 0.3)

    # Engagement (issues, PRs)
    open_issues = repo.get('open_issues', 0)
    engagement_score = min(1.0, math.log10(open_issues + 1) / 3)  # Normalize around 1k issues
    score += engagement_score * w.get('engagement_weight', 0.3)

    return score


def calculate_maturity_alignment(org_profile: Dict, repo: Dict, weights: Dict) -> float:
    """Calculate maturity alignment score."""
    score = 0.0
    w = weights.get('maturity', {})

    # Repository age
    created_at = repo.get('created_at')
    if created_at:
        try:
            created = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            age_years = (datetime.now(created.tzinfo) - created).days / 365.25

            age_tolerance = w.get('age_tolerance_years', 2)

            # Prefer repos that are mature but not ancient
            if 1 <= age_years <= 5:
                age_score = 1.0
            elif age_years < 1:
                age_score = 0.6
            else:
                age_score = max(0.2, 1.0 - (age_years - 5) / 10)

            score += age_score * w.get('age_weight', 0.25)
        except:
            score += 0.5 * w.get('age_weight', 0.25)

    # Star count (popularity)
    stars = repo.get('stars', 0)
    if w.get('stars_log_scale', True):
        stars_score = min(1.0, math.log10(stars + 1) / 4)  # Normalize around 10k stars
    else:
        stars_score = min(1.0, stars / 10000)

    score += stars_score * w.get('stars_weight', 0.25)

    # Maintenance status (days since last commit)
    updated_at = repo.get('updated_at')
    if updated_at:
        try:
            last_update = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
            days_since_update = (datetime.now(last_update.tzinfo) - last_update).days

            max_days = w.get('max_days_since_commit', 90)
            if days_since_update <= max_days:
                maintenance_score = 1.0
            else:
                maintenance_score = max(0.0, 1.0 - (days_since_update - max_days) / 365)

            score += maintenance_score * w.get('maintenance_weight', 0.3)
        except:
            score += 0.5 * w.get('maintenance_weight', 0.3)

    # Release cadence (hard to estimate without API calls)
    # Use has_wiki as proxy for project maturity
    if repo.get('has_wiki'):
        release_score = 0.7
    else:
        release_score = 0.4

    score += release_score * w.get('release_weight', 0.2)

    return score


def calculate_similarity_score(org_profile: Dict, repo: Dict, weights_config: Dict) -> Dict[str, Any]:
    """Calculate overall similarity score with breakdown."""
    weights = weights_config.get('weights', {})

    # Calculate dimension scores
    tech_stack_score = calculate_tech_stack_similarity(org_profile, repo, weights_config)
    domain_score = calculate_domain_similarity(org_profile, repo, weights_config)
    scale_score = calculate_scale_similarity(org_profile, repo, weights_config)
    activity_score = calculate_activity_similarity(org_profile, repo, weights_config)
    maturity_score = calculate_maturity_alignment(org_profile, repo, weights_config)

    # Calculate weighted overall score
    overall = (
        tech_stack_score * weights.get('tech_stack', 0.3) +
        domain_score * weights.get('problem_domain', 0.25) +
        scale_score * weights.get('scale', 0.15) +
        activity_score * weights.get('activity', 0.15) +
        maturity_score * weights.get('maturity', 0.15)
    )

    # Apply boosts and penalties
    boosts = weights_config.get('boosts', {})
    penalties = weights_config.get('penalties', {})

    # Quality org boost
    if repo.get('owner') in boosts.get('quality_orgs', []):
        overall *= boosts.get('quality_org_multiplier', 1.2)

    # Stale penalty
    updated_at = repo.get('updated_at')
    if updated_at:
        try:
            last_update = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
            days_since_update = (datetime.now(last_update.tzinfo) - last_update).days
            stale_threshold = penalties.get('stale_threshold_days', 180)

            if days_since_update > stale_threshold:
                overall *= penalties.get('stale_penalty', 0.7)
        except:
            pass

    # Ensure score is in 0-1 range
    overall = max(0.0, min(1.0, overall))

    return {
        'overall_similarity': round(overall, 4),
        'breakdown': {
            'tech_stack': round(tech_stack_score, 4),
            'problem_domain': round(domain_score, 4),
            'scale': round(scale_score, 4),
            'activity': round(activity_score, 4),
            'maturity': round(maturity_score, 4)
        }
    }


def score_repositories(discovered_repos_path: str, org_profile_path: str,
                       weights_config_path: str, output_path: str):
    """Score and rank discovered repositories."""
    print("[SIMILARITY] Loading data...")

    # Load discovered repos
    with open(discovered_repos_path, 'r') as f:
        discovered_data = json.load(f)
        repos = discovered_data.get('repositories', [])

    # Load org profile
    with open(org_profile_path, 'r') as f:
        org_profile = json.load(f)

    # Load weights config
    with open(weights_config_path, 'r') as f:
        weights_config = yaml.safe_load(f)

    print(f"[SIMILARITY] Scoring {len(repos)} repositories...")

    # Score each repository
    scored_repos = []
    for repo in repos:
        score_data = calculate_similarity_score(org_profile, repo, weights_config)

        scored_repo = {
            **repo,
            'similarity_score': score_data['overall_similarity'],
            'similarity_breakdown': score_data['breakdown']
        }

        scored_repos.append(scored_repo)

    # Sort by similarity score (descending)
    scored_repos.sort(key=lambda r: r['similarity_score'], reverse=True)

    # Filter by threshold
    threshold = weights_config.get('similarity_threshold', 0.6)
    filtered_repos = [r for r in scored_repos if r['similarity_score'] >= threshold]

    print(f"[SIMILARITY] Scored repositories: {len(scored_repos)}")
    print(f"[SIMILARITY] Above threshold ({threshold}): {len(filtered_repos)}")

    if filtered_repos:
        print(f"[SIMILARITY] Top similarity score: {filtered_repos[0]['similarity_score']:.4f}")
        print(f"[SIMILARITY] Top repository: {filtered_repos[0]['full_name']}")

    # Create output
    output = {
        'similarity_metadata': {
            'generated_at': datetime.utcnow().isoformat() + 'Z',
            'org_profile_fingerprint': org_profile.get('fingerprint'),
            'total_scored': len(scored_repos),
            'above_threshold': len(filtered_repos),
            'threshold': threshold
        },
        'repositories': filtered_repos[:100]  # Top 100
    }

    # Write output
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"[SIMILARITY] Results saved to: {output_path}")

    return output


def main():
    parser = argparse.ArgumentParser(description='Calculate similarity scores for discovered repositories')
    parser.add_argument('--discovered', required=True,
                        help='Discovered repositories JSON file')
    parser.add_argument('--profile', required=True,
                        help='Organization profile JSON file')
    parser.add_argument('--weights', default='config/research/similarity_weights.yaml',
                        help='Similarity weights configuration')
    parser.add_argument('--out', required=True,
                        help='Output JSON file path')

    args = parser.parse_args()

    score_repositories(args.discovered, args.profile, args.weights, args.out)


if __name__ == '__main__':
    main()
