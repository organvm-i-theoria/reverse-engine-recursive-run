# Research System Quick Start Guide

Welcome to the **Recursive and Generative Research System** for architecture governance!

This system automatically discovers, analyzes, and learns from similar organizations and repositories to help you continuously improve your software architecture and development practices.

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Understanding the Results](#understanding-the-results)
5. [Configuration](#configuration)
6. [Troubleshooting](#troubleshooting)

---

## Overview

The Research System operates in phases:

1. **Profile Your Organization** - Analyze your codebase to create a fingerprint
2. **Discover Similar Repos** - Find repositories similar to yours using GitHub API
3. **Calculate Similarity** - Rank discovered repos by multi-dimensional similarity
4. **Analyze Patterns** (Coming Soon) - Extract best practices from top matches
5. **Generate Recommendations** (Coming Soon) - Personalized improvement suggestions
6. **Recursive Refinement** (Coming Soon) - Learn from feedback and improve

## Installation

### Prerequisites

- Python 3.8+
- Git
- GitHub account (for API access)

### Step 1: Install Dependencies

```bash
pip install -r requirements-research.txt
```

This installs:
- `PyGithub` - GitHub API integration
- `PyYAML` - Configuration parsing
- `pandas` - Data analysis
- Other utilities

### Step 2: Get a GitHub Token

For best results, you need a GitHub Personal Access Token:

1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select scopes: `public_repo`, `read:org` (minimum)
4. Copy the token

### Step 3: Set Environment Variable

```bash
export GITHUB_TOKEN="your_token_here"
```

Or add to your `.bashrc`/`.zshrc`:

```bash
echo 'export GITHUB_TOKEN="your_token_here"' >> ~/.bashrc
source ~/.bashrc
```

### Step 4: Verify Installation

```bash
make research-check-deps
```

You should see:
```
✓ All dependencies installed
```

---

## Quick Start

### Option 1: Run Full Research Cycle (Recommended)

This runs all phases in sequence:

```bash
make research-full
```

**What this does:**
1. Analyzes your codebase to create an organization profile
2. Discovers similar repositories on GitHub
3. Calculates similarity scores
4. Generates a summary report

**Time:** ~5-10 minutes (depending on API rate limits)

**Output:** Check `artifacts/research/` for results

### Option 2: Run Phases Individually

If you want more control:

```bash
# Phase 1: Create organization profile
make research-profile

# Phase 2: Discover repositories
make research-discover

# Phase 3: Calculate similarity scores
make research-similarity

# Phase 4: View summary
make research-report
```

---

## Understanding the Results

### Organization Profile

**File:** `artifacts/research/profiles/org_profile.json`

This contains:
```json
{
  "fingerprint": "a1b2c3d4e5f6g7h8",
  "technology": {
    "languages": {
      "Python": {"file_count": 42, "percentage": 35.2}
    },
    "frameworks": {
      "Python": ["Django@4.2", "Flask@2.3"]
    },
    "tools": ["Docker", "GitHub Actions", "Make"]
  },
  "metrics": {
    "total_files": 119,
    "total_lines": 12547,
    "primary_languages": ["Python", "JavaScript", "Go"]
  },
  "challenges": {
    "high_priority": [
      {
        "category": "code_quality",
        "issue": "high_hotspot_count",
        "research_focus": ["refactoring", "testing"]
      }
    ],
    "research_areas": ["testing", "ci_cd", "security"]
  }
}
```

**Key Fields:**
- **fingerprint**: Unique ID for your org profile
- **technology**: Detected languages, frameworks, tools
- **challenges**: Identified pain points → drives research focus
- **research_areas**: Topics to search for

### Discovered Repositories

**File:** `artifacts/research/discoveries/similarity_scores.json`

This contains ranked repositories with similarity scores:

```json
{
  "similarity_metadata": {
    "total_scored": 247,
    "above_threshold": 42,
    "threshold": 0.6
  },
  "repositories": [
    {
      "full_name": "pallets/flask",
      "description": "The Python micro framework for building web applications.",
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

**Understanding Scores:**
- **Overall Score** (0-1): Combined similarity across all dimensions
- **Breakdown**: Individual dimension scores
  - **tech_stack**: Language/framework overlap
  - **problem_domain**: Topic/purpose alignment
  - **scale**: Size/complexity similarity
  - **activity**: Update frequency match
  - **maturity**: Age/stability alignment

**Threshold:** Only repos scoring ≥0.6 are included (configurable)

### Research Report

Run `make research-report` to see a summary:

```
========================================
Research System Summary
========================================

Organization Profile:
  Fingerprint: a1b2c3d4e5f6g7h8
  Languages: Python, JavaScript, Go, Shell, Makefile
  Research Areas: 8
  High Priority Challenges: 3

Discovery Results:
  Total Scored: 247
  Above Threshold: 42
  Threshold: 0.6
  Top 5 Matches:
    1. pallets/flask (score: 0.8542)
    2. django/django (score: 0.8231)
    3. tiangolo/fastapi (score: 0.8012)
    4. encode/django-rest-framework (score: 0.7854)
    5. requests/requests (score: 0.7623)
========================================
```

---

## Configuration

### Discovery Configuration

**File:** `config/research/discovery_config.yaml`

Key settings:

```yaml
github:
  min_stars: 10                 # Minimum stars for repos
  min_updated_days_ago: 365     # Only repos updated in last year
  max_results_per_query: 100    # Results per search query

search_queries:
  manual:
    - "topic:architecture topic:governance"
    - "topic:testing topic:best-practices"

filters:
  exclude_keywords:
    - "tutorial"
    - "homework"
  include_forks: false
  include_archived: false
```

**Customization:**
- Add manual queries for specific topics
- Adjust star thresholds
- Add/remove exclusion keywords

### Similarity Weights

**File:** `config/research/similarity_weights.yaml`

Adjust how similarity is calculated:

```yaml
weights:
  tech_stack: 0.30        # 30% weight on language/framework match
  problem_domain: 0.25    # 25% weight on topic alignment
  scale: 0.15             # 15% weight on size similarity
  activity: 0.15          # 15% weight on activity patterns
  maturity: 0.15          # 15% weight on maturity

similarity_threshold: 0.60  # Only show repos ≥60% similar
```

**Customization:**
- Increase `tech_stack` weight if you want exact language matches
- Increase `problem_domain` if you care more about purpose alignment
- Lower `threshold` to see more results (but less relevant)

---

## Troubleshooting

### "PyGithub not installed"

```bash
pip install PyGithub PyYAML
```

### "GitHub API rate limit exceeded"

**Problem:** GitHub limits unauthenticated requests to 60/hour

**Solution:** Set `GITHUB_TOKEN` environment variable

```bash
export GITHUB_TOKEN="your_token_here"
```

With a token, you get 5000 requests/hour.

### "No repositories discovered"

**Possible causes:**
1. Too restrictive filters (lower `min_stars`)
2. Narrow search queries (check `config/research/discovery_config.yaml`)
3. Organization profile is incomplete (run `make research-profile` again)

**Fix:**
```yaml
# In config/research/discovery_config.yaml
github:
  min_stars: 5  # Lower from 10
  min_updated_days_ago: 730  # Expand to 2 years
```

### "Low similarity scores"

**Problem:** All discovered repos score < 0.6

**Solution:** Lower the threshold or broaden search

```yaml
# In config/research/similarity_weights.yaml
similarity_threshold: 0.4  # Lower from 0.6
```

### "Missing organization profile data"

**Problem:** Profile doesn't detect your tech stack

**Fix:**
1. Ensure you're running from the repo root: `cd /path/to/repo && make research-profile`
2. Check that your codebase has recognizable files (package.json, requirements.txt, etc.)
3. Review `artifacts/research/profiles/tech_signature.json` for what was detected

---

## Next Steps

### Phase 1 Complete: Now What?

Once you've run `make research-full`, you have:
1. ✅ Organization profile
2. ✅ Discovered repositories ranked by similarity
3. ✅ Summary report

**Recommended next steps:**

1. **Review Top Matches**
   ```bash
   # View top 10 repositories
   cat artifacts/research/discoveries/similarity_scores.json | python3 -m json.tool | less
   ```

2. **Manually Explore**
   - Visit the top 5 repositories on GitHub
   - Look for patterns you want to adopt (CI/CD, testing, documentation)
   - Bookmark repos for deeper analysis

3. **Customize Configuration**
   - Adjust similarity weights based on your priorities
   - Add specific topics to `discovery_config.yaml`
   - Re-run: `make research-discover research-similarity`

4. **Wait for Future Phases** (Coming Soon)
   - Automated pattern extraction
   - Recommendation generation
   - Implementation scaffolding

### Manual Analysis Workflow

While automated analysis is being built, here's a manual workflow:

1. **Pick Top 3 Repos**
   ```bash
   # Extract top 3
   python3 -c "
   import json
   with open('artifacts/research/discoveries/similarity_scores.json') as f:
       data = json.load(f)
       for i, repo in enumerate(data['repositories'][:3], 1):
           print(f\"{i}. {repo['full_name']} - {repo['url']}\")
   "
   ```

2. **Clone and Explore**
   ```bash
   # Clone a top match
   git clone https://github.com/[owner]/[repo] /tmp/research_analysis
   cd /tmp/research_analysis

   # Look for patterns
   ls -la  # Directory structure
   cat .github/workflows/*.yml  # CI/CD patterns
   cat README.md  # Documentation practices
   ```

3. **Document Learnings**
   Create an ADR for promising patterns:
   ```bash
   make adr-new TITLE="Adopt Pattern X from [repo]"
   ```

---

## Configuration Reference

### Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `GITHUB_TOKEN` | GitHub API authentication | None (required) |

### Configuration Files

| File | Purpose |
|------|---------|
| `config/research/discovery_config.yaml` | Search parameters, filters |
| `config/research/similarity_weights.yaml` | Similarity scoring weights |
| `config/research/analysis_config.yaml` | Analysis pipeline config (future) |
| `config/research/prioritization_weights.yaml` | Recommendation ranking (future) |

### Artifacts

| Path | Contents |
|------|----------|
| `artifacts/research/profiles/` | Organization profiles |
| `artifacts/research/discoveries/` | Discovered repos and scores |
| `artifacts/research/analysis/` | Cloned repo analysis (future) |
| `artifacts/research/patterns/` | Extracted patterns (future) |
| `artifacts/research/recommendations/` | Generated recommendations (future) |

---

## Feedback and Iteration

The research system is **recursive** - it learns from feedback:

1. **Review Results**: Check similarity scores and discovered repos
2. **Provide Feedback**: Adjust configuration based on what you find useful
3. **Re-run**: `make research-full` with new settings
4. **Track Changes**: Compare new results with previous runs

**Coming Soon:** Automated feedback collection and model retraining

---

## Support

### Documentation

- **Full Roadmap**: `docs/ROADMAP_RECURSIVE_RESEARCH_SYSTEM.md`
- **Task List**: `docs/TASK_LIST_RESEARCH_SYSTEM.md`
- **Main README**: `README.md`

### Getting Help

1. Check existing documentation
2. Review configuration files for options
3. Open an issue on GitHub (if applicable)

---

## What's Coming Next

The research system is being built in phases:

- ✅ **Phase 1**: Organization Profiling
- ✅ **Phase 2**: Repository Discovery & Similarity Scoring
- 🚧 **Phase 3**: Automated Repository Analysis (in progress)
- 📅 **Phase 4**: Pattern Recognition & Learning
- 📅 **Phase 5**: Recommendation Engine
- 📅 **Phase 6**: Recursive Refinement

Stay tuned for updates!

---

**Happy researching! 🚀**
