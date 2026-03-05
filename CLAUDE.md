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

<!-- ORGANVM:AUTO:START -->
## System Context (auto-generated — do not edit)

**Organ:** ORGAN-I (Theory) | **Tier:** standard | **Status:** CANDIDATE
**Org:** `unknown` | **Repo:** `reverse-engine-recursive-run`

### Edges
- **Produces** → `unknown`: unknown

### Siblings in Theory
`recursive-engine--generative-entity`, `organon-noumenon--ontogenetic-morphe`, `auto-revision-epistemic-engine`, `narratological-algorithmic-lenses`, `call-function--ontological`, `sema-metra--alchemica-mundi`, `system-governance-framework`, `cognitive-archaelogy-tribunal`, `a-recursive-root`, `radix-recursiva-solve-coagula-redi`, `.github`, `nexus--babel-alexandria-`, `4-ivi374-F0Rivi4`, `cog-init-1-0-`, `collective-persona-operations` ... and 4 more

### Governance
- Foundational theory layer. No upstream dependencies.

*Last synced: 2026-02-24T12:41:28Z*
<!-- ORGANVM:AUTO:END -->


## ⚡ Conductor OS Integration
This repository is a managed component of the ORGANVM meta-workspace.
- **Orchestration:** Use `conductor patch` for system status and work queue.
- **Lifecycle:** Follow the `FRAME -> SHAPE -> BUILD -> PROVE` workflow.
- **Governance:** Promotions are managed via `conductor wip promote`.
- **Intelligence:** Conductor MCP tools are available for routing and mission synthesis.
