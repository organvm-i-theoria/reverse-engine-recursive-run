# CLAUDE.md — reverse-engine-recursive-run

**ORGAN I** (Theory) · `organvm-i-theoria/reverse-engine-recursive-run`
**Status:** ACTIVE · **Branch:** `main`

## What This Repo Is

Architecture governance toolkit — 7-script Python pipeline for risk scoring, drift detection, ownership analysis, and SBOM generation across any codebase

## Stack

**Languages:** Python, Shell, Makefile
**Build:** Python (pip/setuptools), Make
**Testing:** pytest (likely)

## Directory Structure

```
📁 .github/
📁 config/
    risk_weights.yaml
    service_paths.yaml
📁 docs/
    adr
    summary_compiled.md
📁 scripts/
    README.md
    __main__.py
    adr_new.sh
    gen_sbom.sh
    hotspot_merge.py
    ownership_diff.py
    parse_semgrep.py
    parse_trivy.py
    risk_update.py
    scan_drift.py
📁 templates/
📁 tests/
    __init__.py
    test_scripts.py
  .gitignore
  CHANGELOG.md
  Dockerfile.analysis
  LICENSE
  Makefile
  QUICKSTART.md
  README.md
  pyproject.toml
  seed.yaml
```

## Key Files

- `README.md` — Project documentation
- `pyproject.toml` — Python project config
- `seed.yaml` — ORGANVM orchestration metadata
- `tests/` — Test suite

## Development

```bash
pip install -e .    # Install in development mode
pytest              # Run tests
```

## ORGANVM Context

This repository is part of the **ORGANVM** eight-organ creative-institutional system.
It belongs to **ORGAN I (Theory)** under the `organvm-i-theoria` GitHub organization.

**Dependencies:**
- organvm-i-theoria/recursive-engine--generative-entity

**Registry:** [`registry-v2.json`](https://github.com/meta-organvm/organvm-corpvs-testamentvm/blob/main/registry-v2.json)
**Corpus:** [`organvm-corpvs-testamentvm`](https://github.com/meta-organvm/organvm-corpvs-testamentvm)
