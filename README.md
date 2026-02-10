[![ORGAN-I: Theory](https://img.shields.io/badge/ORGAN--I-Theory-1a237e?style=flat-square)](https://github.com/organvm-i-theoria)
[![Python](https://img.shields.io/badge/python-3.11+-3776ab?style=flat-square&logo=python&logoColor=white)]()
[![Status: Active](https://img.shields.io/badge/status-active-brightgreen?style=flat-square)]()

# reverse-engine-recursive-run

**Architecture governance toolkit — a 7-script Python pipeline for risk scoring, drift detection, ownership analysis, and SBOM generation across any codebase.**

> Most codebases accumulate architectural debt invisibly. By the time a team notices, the drift between intended architecture and actual dependencies has calcified into technical risk that blocks every initiative. This toolkit makes that drift visible, quantifiable, and actionable — before it becomes an emergency.

---

## Table of Contents

- [Problem Statement](#problem-statement)
- [What This Toolkit Actually Does](#what-this-toolkit-actually-does)
- [Core Pipeline](#core-pipeline)
- [Risk Scoring Model](#risk-scoring-model)
- [Architecture Drift Detection](#architecture-drift-detection)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Templates and Outputs](#templates-and-outputs)
- [Repository Contents](#repository-contents)
- [Containerized Analysis](#containerized-analysis)
- [ADR Scaffolding](#adr-scaffolding)
- [Roadmap](#roadmap)
- [Cross-References](#cross-references)
- [Author](#author)

---

## Problem Statement

Software architecture degrades through three invisible mechanisms:

1. **Knowledge concentration** — critical subsystems understood by one person, creating single points of failure that only surface during attrition or incident response.
2. **Dependency drift** — the actual import graph and service boundaries diverge from the documented or intended architecture, introducing coupling that contradicts design decisions.
3. **Security surface expansion** — vulnerability density in specific modules grows unchecked because scanning tools produce raw findings without contextual prioritization.

Traditional approaches treat these as separate concerns: bus-factor analysis in one tool, dependency graphing in another, vulnerability scanning in a third. This toolkit unifies all three into a single pipeline that produces a weighted, composite risk score per service or module — so you can see which parts of your codebase are simultaneously poorly understood, architecturally drifting, and accumulating vulnerabilities.

The output is a prioritized remediation backlog, not a dashboard. It is designed to feed into sprint planning, not sit in a monitoring tab.

## What This Toolkit Actually Does

This is a **working set of 7 Python scripts and 1 shell script**, orchestrated by a Makefile, that analyze a codebase and produce structured risk assessments. The pipeline is functional and has been used for real analysis. It is not a SaaS product, a web application, or a platform — it is a command-line toolkit that runs locally or in a container.

**What exists today:**
- 7 analysis scripts covering risk scoring, drift detection, ownership analysis, and security normalization
- A Makefile that orchestrates the full pipeline with `make full-analysis`
- A Docker image for reproducible analysis environments
- YAML-driven configuration for risk weights and service boundaries
- Markdown and YAML output templates for executive summaries and remediation backlogs
- ADR (Architecture Decision Record) scaffolding for documenting governance decisions

**What does not exist yet** (see [Roadmap](#roadmap)):
- A Backstage plugin or web UI
- A backend server or API
- CI/CD workflow integration
- Automated scheduling or continuous monitoring
- Test suite or formal packaging (no `pyproject.toml`)

## Core Pipeline

The pipeline consists of 7 scripts that run sequentially. Each script reads from upstream outputs or external tool results and writes structured data for the next stage.

| # | Script | Purpose | Input | Output |
|---|--------|---------|-------|--------|
| 1 | `parse_trivy.py` | Normalize Trivy vulnerability scan results into a standard schema | Trivy JSON output | Normalized vulnerability records |
| 2 | `parse_semgrep.py` | Normalize Semgrep static analysis results into the same schema | Semgrep JSON output | Normalized finding records |
| 3 | `gen_sbom.sh` | Generate Software Bill of Materials using Syft | Target codebase | SBOM in CycloneDX format |
| 4 | `scan_drift.py` | Detect architecture drift by comparing actual imports/dependencies against declared service boundaries | Codebase + `service_paths.yaml` | Drift report with boundary violations |
| 5 | `ownership_diff.py` | Analyze git blame and commit history to identify knowledge concentration (bus factor) | Git repository | Ownership concentration scores per module |
| 6 | `hotspot_merge.py` | Merge vulnerability, drift, and ownership signals into composite risk scores using configurable weights | Outputs from steps 1–5 + `risk_weights.yaml` | Weighted risk scores per service/module |
| 7 | `risk_update.py` | Aggregate risk scores into a final prioritized report and populate output templates | Merged risk data | Executive summary + remediation backlog |

The canonical invocation is:

```bash
make full-analysis
```

This runs all 7 stages in order. Individual stages can also be run independently if you only need a subset of the analysis (e.g., `python hotspot_merge.py` for risk scoring alone, given pre-existing inputs).

## Risk Scoring Model

The composite risk score for each service or module is computed by `hotspot_merge.py` using a weighted formula. The weights are defined in `risk_weights.yaml` and can be tuned per-project.

The three input signals are:

- **Vulnerability density** — normalized count of security findings (from Trivy + Semgrep) per module, weighted by severity (critical > high > medium > low).
- **Drift score** — number and severity of boundary violations detected by `scan_drift.py`. A module that imports from a service it should not depend on receives a higher drift score.
- **Ownership concentration** — inverse of bus factor. A module where 90% of commits come from one author scores higher than a module with distributed authorship.

These three signals are multiplied by their respective weights and summed to produce a final risk score. The output is sorted descending — the highest-risk modules appear first, making it immediately clear where to focus remediation effort.

The default weights in `risk_weights.yaml` emphasize ownership concentration slightly more than vulnerability density, on the theory that a well-understood module with known vulnerabilities is less risky than a poorly understood module with fewer vulnerabilities — because the former can be fixed by anyone, while the latter requires a specific person who may not be available.

## Architecture Drift Detection

`scan_drift.py` is the most theoretically interesting script in the pipeline. It operates on a simple but powerful premise: if you can declare what your service boundaries *should* be, the tool can tell you where reality has diverged.

The intended architecture is declared in `service_paths.yaml`, which maps service names to directory paths and lists their permitted dependencies. The script then walks the actual import graph (via AST parsing for Python, `require`/`import` analysis for JavaScript/TypeScript) and flags any import that crosses a boundary not listed in the permitted dependencies.

This is not a full architectural fitness function — it does not enforce layering rules or detect temporal coupling. But it catches the most common form of architectural decay: the unauthorized cross-service import that gets added during a deadline sprint and never removed.

## Quick Start

```bash
# Clone the repository
git clone https://github.com/organvm-i-theoria/reverse-engine-recursive-run.git
cd reverse-engine-recursive-run

# Option 1: Run directly (requires Python 3.11+)
# Point the scripts at your target codebase by editing service_paths.yaml
# Then run the full pipeline:
make full-analysis

# Option 2: Run in Docker (recommended for reproducibility)
docker build -f Dockerfile.analysis -t reverse-engine .
docker run -v /path/to/your/codebase:/workspace reverse-engine make full-analysis
```

See `QUICKSTART.md` for detailed setup instructions and `scripts/README.md` for per-script documentation.

## Configuration

| File | Purpose |
|------|---------|
| `risk_weights.yaml` | Tunable weights for the three risk signals (vulnerability, drift, ownership). Adjust these to reflect your organization's priorities. |
| `service_paths.yaml` | Declares service boundaries — maps service names to directory paths and lists permitted inter-service dependencies. This is the "intended architecture" that drift detection compares against. |

Both files are YAML and designed to be human-editable. There are no environment variables or CLI flags to set — all configuration is file-based.

## Templates and Outputs

| File | Purpose |
|------|---------|
| `templates/executive_summary_template.md` | Markdown template populated by `risk_update.py` — produces a narrative summary suitable for sharing with leadership or architecture review boards. |
| `templates/remediation_backlog.yaml` | YAML template populated by `risk_update.py` — produces a structured backlog of prioritized remediation items, ready to import into a project tracker. |

The compiled reference document at `docs/summary_compiled.md` (3,000+ words) provides a detailed walkthrough of the methodology, scoring model, and interpretation guidelines.

## Repository Contents

```
reverse-engine-recursive-run/
├── Makefile                          # Pipeline orchestration (make full-analysis)
├── Dockerfile.analysis               # Ubuntu 22.04, Python 3, Node 20, Go 1.22
├── README.md                         # This file
├── QUICKSTART.md                     # Setup and first-run guide
├── risk_weights.yaml                 # Configurable risk signal weights
├── service_paths.yaml                # Declared service boundaries
├── hotspot_merge.py                  # Risk scoring — merges 3 signals into composite score
├── scan_drift.py                     # Architecture drift detection
├── ownership_diff.py                 # Knowledge concentration / bus factor analysis
├── risk_update.py                    # Aggregation and report generation
├── parse_trivy.py                    # Trivy vulnerability normalization
├── parse_semgrep.py                  # Semgrep finding normalization
├── scripts/
│   ├── gen_sbom.sh                   # SBOM generation via Syft
│   ├── adr_new.sh                    # ADR scaffolding script
│   └── README.md                     # Per-script documentation
├── templates/
│   ├── executive_summary_template.md # Report output template
│   ├── remediation_backlog.yaml      # Backlog output template
│   └── adr_template.md              # ADR template
└── docs/
    └── summary_compiled.md           # 3,000+ word methodology reference
```

**22 files, ~151KB total. Pure Python + shell. No external Python dependencies beyond the standard library.**

## Containerized Analysis

The `Dockerfile.analysis` provides a reproducible analysis environment based on Ubuntu 22.04 with:

- Python 3 (for the analysis scripts)
- Node.js 20 (for JavaScript/TypeScript import analysis in `scan_drift.py`)
- Go 1.22 (for Go dependency analysis)
- Trivy, Semgrep, and Syft (for security scanning and SBOM generation)

This ensures that the full pipeline — including the external security tools — runs identically regardless of the host environment. The image is designed for ephemeral analysis runs, not as a long-running service.

## ADR Scaffolding

The repository includes lightweight Architecture Decision Record tooling:

- `scripts/adr_new.sh` — creates a new ADR from the template with auto-incrementing numbering
- `templates/adr_template.md` — standard ADR format (context, decision, consequences)

This is included because governance decisions about the codebase under analysis should be recorded alongside the analysis itself. When the risk pipeline identifies a structural problem, the ADR scaffolding provides a place to document the decision about how to address it.

## Roadmap

The following capabilities are planned but **do not exist in the current codebase**:

- **Test suite** — unit tests for each script, integration tests for the full pipeline, and property-based tests for the risk scoring model.
- **Formal packaging** — `pyproject.toml` with proper dependency declaration, versioned releases, and `pip install` support.
- **CI/CD integration** — GitHub Actions workflow that runs the pipeline on pull requests and comments with risk score changes.
- **Backstage plugin** — a read-only Backstage catalog integration that surfaces risk scores alongside service metadata.
- **Scheduling and continuous monitoring** — cron-driven or event-driven pipeline execution with historical trend tracking.
- **Additional language support** — expand `scan_drift.py` import analysis beyond Python and JavaScript to cover Rust, Go, and Java.
- **Visualization** — dependency graph rendering with drift violations highlighted, exportable as SVG or embedded in the executive summary.

Contributions toward any of these are welcome. The current scripts are deliberately simple (single-file, standard library only) to make extension straightforward.

## Cross-References

| Resource | Description |
|----------|-------------|
| [recursive-engine](https://github.com/organvm-i-theoria/recursive-engine) | Flagship ORGAN-I repository — recursive system theory and self-referential computation |
| [ORGAN-I: Theoria](https://github.com/organvm-i-theoria) | Parent organization — theory, epistemology, recursion, ontology |
| [meta-organvm](https://github.com/meta-organvm) | Meta-organization — umbrella governance across all 8 organs |
| [ORGAN-IV: Taxis](https://github.com/organvm-iv-taxis) | Orchestration organ — governance routing and system coordination |

This repository belongs to ORGAN-I because architecture governance is fundamentally a theoretical concern: it asks "what *should* the system look like?" and measures deviation from that ideal. The toolkit operationalizes architectural intent — making it a bridge between theory (ORGAN-I) and orchestration (ORGAN-IV).

---

**Author:** **[@4444J99](https://github.com/4444J99)** / Part of [ORGAN-I: Theoria](https://github.com/organvm-i-theoria)

**License:** Not yet specified. See [Roadmap](#roadmap).
