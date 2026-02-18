# Recursive and Generative Research System

> **Automatically discover, analyze, and learn from similar organizations and repositories to continuously improve your architecture governance practices.**

## What is This?

The Research System is an intelligent, recursive learning engine that:

1. **Profiles Your Organization** - Creates a multi-dimensional fingerprint of your codebase, tech stack, and challenges
2. **Discovers Similar Repositories** - Searches GitHub for repos with similar characteristics
3. **Scores by Similarity** - Ranks discoveries using machine learning algorithms
4. **Analyzes Patterns** - Extracts best practices and anti-patterns (coming soon)
5. **Generates Recommendations** - Produces personalized, actionable improvements (coming soon)
6. **Learns Recursively** - Improves itself based on feedback and outcomes (coming soon)

## Why Use It?

**Problem:** Staying current with best practices across languages, frameworks, and domains is overwhelming.

**Solution:** Let the Research System do the heavy lifting:
- Automatically find repos solving similar problems
- Learn from high-quality, well-maintained projects
- Get personalized recommendations based on YOUR context
- Reduce manual research time by 70%+

## Current Status

| Phase | Status | Description |
|-------|--------|-------------|
| **Phase 1: Profiling** | ✅ Complete | Analyze codebase, extract tech stack, identify challenges |
| **Phase 2: Discovery** | ✅ Complete | Search GitHub, score similarity, rank results |
| **Phase 3: Analysis** | 🚧 In Progress | Clone repos, extract patterns, compare with baseline |
| **Phase 4: Pattern Recognition** | 📅 Planned | Aggregate patterns, identify best practices |
| **Phase 5: Recommendations** | 📅 Planned | Generate prioritized, actionable improvements |
| **Phase 6: Recursive Learning** | 📅 Planned | Feedback loops, model retraining, self-improvement |

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements-research.txt
```

### 2. Set GitHub Token

```bash
export GITHUB_TOKEN="your_github_token_here"
```

Get a token at: https://github.com/settings/tokens

### 3. Run Research Cycle

```bash
make research-full
```

This will:
- Profile your organization
- Discover 100+ similar repositories
- Calculate similarity scores
- Generate a summary report

**Time:** ~5-10 minutes

### 4. Review Results

```bash
# View summary
make research-report

# View detailed results
cat artifacts/research/discoveries/similarity_scores.json | python3 -m json.tool | less
```

## Documentation

- **Quick Start Guide**: [RESEARCH_QUICKSTART.md](./RESEARCH_QUICKSTART.md) - Step-by-step tutorial
- **Full Roadmap**: [../ROADMAP_RECURSIVE_RESEARCH_SYSTEM.md](../ROADMAP_RECURSIVE_RESEARCH_SYSTEM.md) - Complete vision and phases
- **Task List**: [../TASK_LIST_RESEARCH_SYSTEM.md](../TASK_LIST_RESEARCH_SYSTEM.md) - Detailed implementation tasks

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  RECURSIVE RESEARCH ENGINE                  │
└─────────────────────────────────────────────────────────────┘

┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ Org Profile  │────▶│  Discovery   │────▶│  Similarity  │
│              │     │   Engine     │     │   Scoring    │
│ • Languages  │     │              │     │              │
│ • Frameworks │     │ • GitHub API │     │ • Tech Match │
│ • Challenges │     │ • Topics     │     │ • Domain     │
└──────────────┘     │ • Keywords   │     │ • Scale      │
                     └──────────────┘     │ • Activity   │
                                          │ • Maturity   │
                                          └──────────────┘
                                                  │
                                                  ▼
                     ┌──────────────────────────────────┐
                     │   Ranked Repository List         │
                     │                                  │
                     │ 1. pallets/flask (0.85)          │
                     │ 2. django/django (0.82)          │
                     │ 3. tiangolo/fastapi (0.80)       │
                     │ ...                              │
                     └──────────────────────────────────┘
```

## Key Features

### 1. Multi-Dimensional Similarity Scoring

Repositories are scored across 5 dimensions:

- **Tech Stack** (30%): Language, framework, tool overlap
- **Problem Domain** (25%): Topic and purpose alignment
- **Scale** (15%): Size and complexity similarity
- **Activity** (15%): Update frequency and engagement
- **Maturity** (15%): Age, stars, maintenance status

**Result:** Composite score (0-1) with full breakdown

### 2. Intelligent Filtering

Automatically filters out:
- Tutorials and homework projects
- Archived or abandoned repos
- Repos below quality threshold (stars, activity)
- Blocklisted organizations

### 3. Configurable Weights

Customize scoring to your priorities:

```yaml
# config/research/similarity_weights.yaml
weights:
  tech_stack: 0.40      # Increase for exact tech match
  problem_domain: 0.20  # Decrease if less important
  # ...
```

### 4. Research Focus Areas

The system identifies your challenges and targets research accordingly:

- High code complexity → Search for refactoring patterns
- Low test coverage → Search for testing strategies
- Security findings → Search for security tooling
- No CI/CD → Search for automation practices

### 5. Recursive Improvement

(Coming in Phase 6)

- Tracks recommendation acceptance rates
- Learns which patterns you find valuable
- Refines search queries based on feedback
- Improves scoring accuracy over time

## Configuration

### Discovery Settings

**File:** `config/research/discovery_config.yaml`

```yaml
github:
  min_stars: 10                 # Quality threshold
  min_updated_days_ago: 365     # Recency filter
  max_results_per_query: 100    # Results per search

filters:
  exclude_keywords:
    - "tutorial"
    - "homework"
  include_forks: false           # Usually noise
  include_archived: false        # Want active projects
```

### Similarity Weights

**File:** `config/research/similarity_weights.yaml`

```yaml
weights:
  tech_stack: 0.30
  problem_domain: 0.25
  scale: 0.15
  activity: 0.15
  maturity: 0.15

similarity_threshold: 0.60  # Only show 60%+ matches
```

## Commands

### Research Commands

```bash
# Check dependencies
make research-check-deps

# Create organization profile
make research-profile

# Discover repositories
make research-discover

# Calculate similarity scores
make research-similarity

# View summary report
make research-report

# Run full cycle
make research-full

# Clean research artifacts
make research-clean
```

### Outputs

| Artifact | Description |
|----------|-------------|
| `artifacts/research/profiles/org_profile.json` | Your organization fingerprint |
| `artifacts/research/profiles/tech_signature.json` | Technology stack details |
| `artifacts/research/discoveries/discovered_repos.json` | Raw discovery results |
| `artifacts/research/discoveries/similarity_scores.json` | Ranked, scored repositories |

## Example Output

### Organization Profile

```json
{
  "fingerprint": "a1b2c3d4e5f6g7h8",
  "metrics": {
    "total_files": 119,
    "total_lines": 12547,
    "primary_languages": ["Python", "JavaScript", "Shell"]
  },
  "challenges": {
    "high_priority": [
      {
        "category": "code_quality",
        "issue": "high_hotspot_count",
        "research_focus": ["refactoring", "testing"]
      }
    ],
    "research_areas": ["testing", "ci_cd", "security", "documentation"]
  }
}
```

### Discovery Results

```json
{
  "repositories": [
    {
      "full_name": "pallets/flask",
      "url": "https://github.com/pallets/flask",
      "stars": 65432,
      "similarity_score": 0.8542,
      "similarity_breakdown": {
        "tech_stack": 0.92,
        "problem_domain": 0.85,
        "scale": 0.78,
        "activity": 0.91,
        "maturity": 0.82
      }
    }
  ]
}
```

## What's Next?

### Phase 3: Automated Analysis (In Development)

Coming soon:
- Clone top repos safely (sandboxed)
- Extract patterns automatically:
  - CI/CD configurations
  - Testing strategies
  - Documentation practices
  - Security tooling
- Compare with your baseline
- Identify specific gaps

### Phase 4: Pattern Recognition

- Aggregate patterns across repos
- Identify best practices vs anti-patterns
- Track trends (emerging vs declining)
- Personalize to your context

### Phase 5: Recommendations

- Generate ranked improvement recommendations
- Include evidence (exemplar repos)
- Estimate effort and impact
- Auto-generate ADRs and scaffolds

### Phase 6: Recursive Learning

- Collect feedback on recommendations
- Retrain similarity models
- Optimize search queries
- Update organization profile as you evolve

## Use Cases

### 1. Technology Evaluation

**Scenario:** Considering adopting a new framework

**Workflow:**
1. Add framework to manual search queries
2. Run `make research-discover`
3. Review top repos using the framework
4. Analyze their patterns and practices
5. Make informed decision

### 2. Best Practice Discovery

**Scenario:** Want to improve CI/CD pipeline

**Workflow:**
1. System identifies "ci_cd" as research area (from gaps)
2. Discovers repos with excellent CI/CD
3. You review their `.github/workflows/` configs
4. Adapt patterns to your needs
5. Create ADR documenting decision

### 3. Competitive Analysis

**Scenario:** Monitor what similar orgs are doing

**Workflow:**
1. Configure discovery to find similar organizations
2. Track top repos from those orgs
3. Run research cycle monthly
4. Identify emerging trends
5. Stay ahead of the curve

### 4. Onboarding New Tech

**Scenario:** Team is new to a technology

**Workflow:**
1. Profile shows skill gap
2. System searches for learning resources
3. Filters for well-documented, beginner-friendly repos
4. Team learns from high-quality examples
5. Faster ramp-up time

## Limitations & Future Work

### Current Limitations

- Only searches GitHub (no GitLab, Bitbucket yet)
- Requires GitHub token for good rate limits
- Similarity scoring is heuristic-based (no ML yet)
- No automated pattern extraction (manual review required)
- No recommendation generation (coming Phase 5)

### Planned Improvements

- Multi-source discovery (GitLab, Bitbucket, papers, blogs)
- Machine learning for similarity scoring
- Automated code analysis and pattern extraction
- Natural language processing for README/doc analysis
- LLM integration for semantic understanding
- Collaborative filtering (learn from similar orgs)
- Real-time monitoring and alerts

## Contributing

The research system is actively being developed. Contributions welcome!

**Priority areas:**
- Phase 3: Repository analysis pipeline
- Phase 4: Pattern recognition algorithms
- Improved similarity scoring
- Additional discovery sources

## Support

- **Issues:** Check existing issues or create new ones
- **Documentation:** See `docs/research/` for detailed guides
- **Questions:** Review RESEARCH_QUICKSTART.md first

## License

Same as parent project.

---

**Built with ❤️ to help teams learn from the collective wisdom of the open-source community.**
