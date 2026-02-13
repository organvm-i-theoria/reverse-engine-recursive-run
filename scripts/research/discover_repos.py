#!/usr/bin/env python3
"""
Repository Discovery Engine

Discovers similar repositories using:
1. GitHub search API
2. Topic-based discovery
3. Organization discovery
4. Similarity scoring and ranking
"""

import os
import json
import argparse
import yaml
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path

try:
    from github import Github, RateLimitExceededException
    from github.GithubException import GithubException
    HAS_PYGITHUB = True
except ImportError:
    HAS_PYGITHUB = False
    print("[DISCOVERY] WARNING: PyGithub not installed. Install with: pip install PyGithub")


class RepositoryDiscovery:
    """Discovers similar repositories based on org profile."""

    def __init__(self, config_path: str, org_profile_path: str, github_token: Optional[str] = None):
        """Initialize discovery engine."""
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        # Load org profile
        with open(org_profile_path, 'r') as f:
            self.org_profile = json.load(f)

        # Initialize GitHub client
        if HAS_PYGITHUB:
            token = github_token or os.environ.get('GITHUB_TOKEN')
            if not token:
                print("[DISCOVERY] WARNING: No GitHub token provided. Rate limits will be very restrictive.")
                print("[DISCOVERY] Set GITHUB_TOKEN environment variable or pass --token")

            self.github = Github(token) if token else Github()
            self.rate_limit_checked = False
        else:
            self.github = None

        self.discovered_repos = []
        self.search_metadata = {
            'queries_executed': 0,
            'total_results': 0,
            'api_calls': 0
        }

    def check_rate_limit(self):
        """Check GitHub API rate limit."""
        if not HAS_PYGITHUB or not self.github:
            return

        rate_limit = self.github.get_rate_limit()
        core = rate_limit.core

        print(f"[DISCOVERY] GitHub API Rate Limit: {core.remaining}/{core.limit}")
        print(f"[DISCOVERY] Resets at: {core.reset}")

        if core.remaining < 100:
            print("[DISCOVERY] WARNING: Low rate limit remaining!")

        self.rate_limit_checked = True

    def build_search_queries(self) -> List[str]:
        """Build search queries from org profile and config."""
        queries = []

        # Add manual queries from config
        manual_queries = self.config.get('search_queries', {}).get('manual', [])
        queries.extend(manual_queries)

        # Build queries from tech stack
        languages = self.org_profile.get('technology', {}).get('languages', {})
        frameworks = self.org_profile.get('technology', {}).get('frameworks', {})

        # Language-based queries
        for lang in list(languages.keys())[:3]:  # Top 3 languages
            queries.append(f"language:{lang} topic:best-practices stars:>100")
            queries.append(f"language:{lang} topic:architecture stars:>50")

        # Framework-based queries
        for lang, fw_list in frameworks.items():
            for fw in fw_list[:2]:  # Top 2 frameworks per language
                # Extract framework name (before @)
                fw_name = fw.split('@')[0].lower()
                queries.append(f"{fw_name} stars:>50")

        # Research area queries
        research_areas = self.org_profile.get('challenges', {}).get('research_areas', [])
        for area in research_areas[:5]:  # Top 5 research areas
            queries.append(f"topic:{area} stars:>100")

        # Deduplicate
        queries = list(set(queries))

        print(f"[DISCOVERY] Built {len(queries)} search queries")
        return queries

    def search_github(self, query: str, max_results: int = 30) -> List[Dict[str, Any]]:
        """Search GitHub repositories."""
        if not HAS_PYGITHUB or not self.github:
            print("[DISCOVERY] Skipping GitHub search (PyGithub not available)")
            return []

        results = []

        try:
            # Add filters from config
            filters = []
            min_stars = self.config.get('github', {}).get('min_stars', 10)
            filters.append(f"stars:>={min_stars}")

            # Updated date filter
            min_updated_days = self.config.get('github', {}).get('min_updated_days_ago', 365)
            min_date = datetime.now() - timedelta(days=min_updated_days)
            filters.append(f"pushed:>={min_date.strftime('%Y-%m-%d')}")

            # Combine query with filters
            full_query = f"{query} {' '.join(filters)}"

            print(f"[DISCOVERY] Searching: {full_query}")

            # Search
            repos = self.github.search_repositories(query=full_query, sort='stars', order='desc')

            self.search_metadata['queries_executed'] += 1
            self.search_metadata['api_calls'] += 1

            # Collect results
            count = 0
            for repo in repos:
                if count >= max_results:
                    break

                # Skip archived repos if configured
                if repo.archived and not self.config.get('filters', {}).get('include_archived', False):
                    continue

                # Skip forks if configured
                if repo.fork and not self.config.get('filters', {}).get('include_forks', False):
                    continue

                repo_data = {
                    'id': repo.id,
                    'full_name': repo.full_name,
                    'name': repo.name,
                    'owner': repo.owner.login,
                    'url': repo.html_url,
                    'description': repo.description,
                    'stars': repo.stargazers_count,
                    'forks': repo.forks_count,
                    'language': repo.language,
                    'topics': repo.get_topics(),
                    'created_at': repo.created_at.isoformat() if repo.created_at else None,
                    'updated_at': repo.updated_at.isoformat() if repo.updated_at else None,
                    'size': repo.size,
                    'is_fork': repo.fork,
                    'is_archived': repo.archived,
                    'has_wiki': repo.has_wiki,
                    'has_issues': repo.has_issues,
                    'open_issues': repo.open_issues_count,
                    'default_branch': repo.default_branch,
                }

                results.append(repo_data)
                count += 1

                # Rate limit check
                if count % 10 == 0:
                    time.sleep(0.5)  # Be nice to API

            self.search_metadata['total_results'] += len(results)
            print(f"[DISCOVERY] Found {len(results)} repositories")

        except RateLimitExceededException:
            print("[DISCOVERY] ERROR: GitHub API rate limit exceeded!")
        except GithubException as e:
            print(f"[DISCOVERY] GitHub API error: {e}")
        except Exception as e:
            print(f"[DISCOVERY] Unexpected error: {e}")

        return results

    def discover_from_all_sources(self) -> List[Dict[str, Any]]:
        """Discover repositories from all configured sources."""
        all_repos = []

        # Check rate limit before starting
        if not self.rate_limit_checked:
            self.check_rate_limit()

        # 1. GitHub search
        if self.config.get('sources', {}).get('github_search', {}).get('enabled', True):
            queries = self.build_search_queries()
            max_per_query = self.config.get('github', {}).get('max_results_per_query', 30)

            for query in queries[:10]:  # Limit to first 10 queries for now
                results = self.search_github(query, max_per_query)
                all_repos.extend(results)

                # Rate limiting
                time.sleep(1)

        # 2. TODO: Add other sources (trending, awesome lists, etc.)

        return all_repos

    def deduplicate_repos(self, repos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate repositories."""
        seen_ids = set()
        unique_repos = []

        for repo in repos:
            repo_id = repo.get('id') or repo.get('full_name')
            if repo_id not in seen_ids:
                seen_ids.add(repo_id)
                unique_repos.append(repo)

        print(f"[DISCOVERY] Deduplicated: {len(repos)} -> {len(unique_repos)} repositories")
        return unique_repos

    def filter_blocklist(self, repos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter out blocklisted repositories."""
        blocklist_orgs = set(self.config.get('blocklist', {}).get('organizations', []))
        blocklist_repos = set(self.config.get('blocklist', {}).get('repositories', []))

        filtered = []
        for repo in repos:
            if repo.get('owner') in blocklist_orgs:
                continue
            if repo.get('full_name') in blocklist_repos:
                continue
            filtered.append(repo)

        if len(filtered) < len(repos):
            print(f"[DISCOVERY] Filtered out {len(repos) - len(filtered)} blocklisted repositories")

        return filtered

    def discover(self, output_path: str):
        """Main discovery orchestration."""
        print("[DISCOVERY] Starting repository discovery...")

        # Discover from all sources
        repos = self.discover_from_all_sources()

        # Deduplicate
        repos = self.deduplicate_repos(repos)

        # Filter blocklist
        repos = self.filter_blocklist(repos)

        # Store discovered repos
        self.discovered_repos = repos

        # Create output
        output = {
            'discovery_metadata': {
                'generated_at': datetime.utcnow().isoformat() + 'Z',
                'org_profile_fingerprint': self.org_profile.get('fingerprint'),
                'queries_executed': self.search_metadata['queries_executed'],
                'total_discovered': len(repos),
                'api_calls': self.search_metadata['api_calls']
            },
            'repositories': repos
        }

        # Write output
        with open(output_path, 'w') as f:
            json.dump(output, f, indent=2)

        print(f"[DISCOVERY] Discovered {len(repos)} repositories")
        print(f"[DISCOVERY] Results saved to: {output_path}")

        return output


def main():
    parser = argparse.ArgumentParser(description='Discover similar repositories')
    parser.add_argument('--config', default='config/research/discovery_config.yaml',
                        help='Discovery configuration file')
    parser.add_argument('--profile', required=True,
                        help='Organization profile JSON file')
    parser.add_argument('--out', required=True,
                        help='Output JSON file path')
    parser.add_argument('--token', help='GitHub token (or set GITHUB_TOKEN env var)')

    args = parser.parse_args()

    discovery = RepositoryDiscovery(args.config, args.profile, args.token)
    discovery.discover(args.out)


if __name__ == '__main__':
    main()
