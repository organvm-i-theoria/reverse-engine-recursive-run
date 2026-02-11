[![ORGAN-I: Theoria](https://img.shields.io/badge/ORGAN--I-Theoria-311b92?style=flat-square)](https://github.com/organvm-i-theoria)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-3776ab?style=flat-square&logo=python&logoColor=white)]()
[![License: MIT](https://img.shields.io/badge/license-MIT-green?style=flat-square)]()
[![Status: Active](https://img.shields.io/badge/status-active-brightgreen?style=flat-square)]()

# reverse-engine-recursive-run

**Architecture governance toolkit — a 7-script Python pipeline for risk scoring, drift detection, ownership analysis, and SBOM generation across any codebase.**

> Most codebases accumulate architectural debt invisibly. By the time a team notices, the drift between intended architecture and actual dependencies has calcified into technical risk that blocks every initiative. This toolkit makes that drift visible, quantifiable, and actionable — before it becomes an emergency.

---

## Table of Contents

- [Theoretical Motivation](#theoretical-motivation)
- [Problem Statement](#problem-statement)
- [What This Toolkit Actually Does](#what-this-toolkit-actually-does)
- [Technical Architecture](#technical-architecture)
- [Core Pipeline](#core-pipeline)
- [Risk Scoring Model](#risk-scoring-model)
- [Architecture Drift Detection](#architecture-drift-detection)
- [Ownership and Knowledge Concentration](#ownership-and-knowledge-concentration)
- [Security Normalization Layer](#security-normalization-layer)
- [Installation and Quick Start](#installation-and-quick-start)
- [Configuration Reference](#configuration-reference)
- [Pipeline Orchestration via Make](#pipeline-orchestration-via-make)
- [Templates and Outputs](#templates-and-outputs)
- [Containerized Analysis](#containerized-analysis)
- [SBOM Generation](#sbom-generation)
- [ADR Scaffolding](#adr-scaffolding)
- [Repository Structure](#repository-structure)
- [Design Decisions and Trade-offs](#design-decisions-and-trade-offs)
- [Extending the Toolkit](#extending-the-toolkit)
- [Roadmap](#roadmap)
- [Cross-Organ References](#cross-organ-references)
- [Related Work](#related-work)
- [Contributing](#contributing)
- [License](#license)
- [Author](#author)

---

## Theoretical Motivation

This repository sits within **ORGAN-I: Theoria** — the organ of the organvm system concerned with theory, epistemology, recursion, and ontology. Architecture governance belongs here because it is fundamentally a question about knowledge: *what does a system know about itself, and what has it forgotten?*

A codebase is a living structure that drifts from its intended design under the pressure of deadlines, personnel changes, and incremental feature work. The intended architecture — the one in the wiki, the one the tech lead describes in onboarding — becomes a fiction. The actual architecture is encoded in import graphs, commit histories, and vulnerability surfaces. The gap between these two is architectural ignorance: the system no longer knows its own shape.

This toolkit operationalizes the epistemological question. It treats the intended architecture (declared in `service_paths.yaml`) as a hypothesis and the actual dependency graph as empirical evidence. Drift detection is then hypothesis testing: does reality still match the model? Risk scoring quantifies the consequences of divergence. Ownership analysis maps where institutional knowledge has concentrated and where it has evaporated.

The name — *reverse-engine-recursive-run* — reflects this recursive quality. The toolkit reverse-engineers a codebase's actual structure, then runs that structure against its declared intent, producing a self-referential report: the system examining itself. This is the same recursive pattern explored in [recursive-engine](https://github.com/organvm-i-theoria/recursive-engine), the flagship ORGAN-I repository, applied not to abstract computation but to the concrete problem of software governance.

In the broader organvm model, this toolkit provides the theoretical foundation that ORGAN-IV (Taxis — orchestration) operationalizes at scale. Where ORGAN-IV coordinates governance across organizations, this repository provides the analytical primitives: the scoring models, detection heuristics, and reporting templates that make governance measurable rather than aspirational.

## Problem Statement

Software architecture degrades through three invisible mechanisms:

1. **Knowledge concentration** — critical subsystems understood by one person, creating single points of failure that only surface during attrition or incident response. The git history contains this information, but nobody reads `git log` to assess organizational risk.

2. **Dependency drift** — the actual import graph and service boundaries diverge from the documented or intended architecture, introducing coupling that contradicts design decisions. This coupling is invisible until someone tries to extract a service or change a shared module and discovers unexpected consumers.

3. **Security surface expansion** — vulnerability density in specific modules grows unchecked because scanning tools produce raw findings without contextual prioritization. A critical CVE in a dead-code module and a critical CVE in the authentication middleware are treated identically, diluting the signal.

Traditional approaches treat these as separate concerns: bus-factor analysis in one tool, dependency graphing in another, vulnerability scanning in a third. The result is three dashboards that nobody synthesizes. This toolkit unifies all three into a single pipeline that produces a weighted, composite risk score per service or module — so you can see which parts of your codebase are simultaneously poorly understood, architecturally drifting, and accumulating vulnerabilities.

The output is a prioritized remediation backlog, not a dashboard. It is designed to feed into sprint planning, not sit in a monitoring tab.

## What This Toolkit Actually Does

This is a **working set of 7 Python/shell scripts**, orchestrated by a Makefile, that analyze a codebase and produce structured risk assessments. The pipeline is functional and has been used for real analysis. It is not a SaaS product, a web application, or a platform — it is a command-line toolkit that runs locally or in a container.

**What exists today:**

- 7 analysis scripts covering risk scoring, drift detection, ownership analysis, and security normalization
- A Makefile that orchestrates the full pipeline with `make full-analysis`
- A Docker image (Ubuntu 22.04 base) for reproducible analysis environments with Python 3, Node.js 20, and Go 1.22
- YAML-driven configuration for risk weights and service boundaries
- Markdown and YAML output templates for executive summaries and remediation backlogs
- ADR (Architecture Decision Record) scaffolding for documenting governance decisions
- A 3,000+ word compiled methodology reference at `docs/summary_compiled.md`

**What does not exist yet** (see [Roadmap](#roadmap)):

- A Backstage plugin or web UI
- A backend server or API
- CI/CD workflow integration (GitHub Actions)
- Automated scheduling or continuous monitoring
- Test suite or formal packaging (no `pyproject.toml`)

## Technical Architecture

The toolkit follows a staged pipeline architecture where each script reads from upstream outputs or external tool results and writes structured JSON or YAML for the next stage. There is no shared state, no database, and no runtime coordination — each script is a standalone CLI tool that communicates through the filesystem.

```
                    ┌─────────────────┐
                    │  Target Codebase │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
     ┌────────────┐  ┌────────────┐  ┌────────────┐
     │ Trivy JSON │  │Semgrep JSON│  │  git log   │
     └─────┬──────┘  └─────┬──────┘  └─────┬──────┘
           ▼               ▼               ▼
    ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
    │parse_trivy.py│ │parse_semgrep │ │ownership_diff│
    │              │ │    .py       │ │    .py       │
    └──────┬───────┘ └──────┬───────┘ └──────┬───────┘
           │               │               │
           ▼               ▼               │
    ┌──────────────────────────┐           │
    │  Security Findings JSON  │           │
    └────────────┬─────────────┘           │
                 │                         │
    ┌────────────┼─────────┐               │
    │            │         │               │
    ▼            ▼         ▼               ▼
┌────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│ radon  │ │git churn │ │scan_drift│ │ownership │
│ (CC)   │ │          │ │   .py    │ │  .json   │
└───┬────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘
    │           │            │             │
    ▼           ▼            ▼             │
┌───────────────────────┐    │             │
│   hotspot_merge.py    │    │             │
│ (weighted risk scores)│    │             │
└──────────┬────────────┘    │             │
           │                 │             │
           ▼                 ▼             ▼
     ┌─────────────────────────────────────────┐
     │            risk_update.py               │
     │   (consolidated risk register)          │
     └──────────────────┬──────────────────────┘
                        │
           ┌────────────┼────────────┐
           ▼            ▼            ▼
    ┌────────────┐ ┌──────────┐ ┌──────────────┐
    │ Executive  │ │Remediation│ │   ADR        │
    │ Summary    │ │ Backlog  │ │ Generation   │
    └────────────┘ └──────────┘ └──────────────┘
```

Key architectural properties:

- **No shared mutable state.** Each script reads input files and writes output files. There is no database, queue, or in-memory coordination.
- **Standard library only.** The Python scripts use only the standard library (plus optional `pyyaml` for YAML config). No pip install required for core functionality.
- **Filesystem as integration bus.** All inter-script communication happens through JSON files in the `artifacts/` directory. This makes the pipeline trivially debuggable — you can inspect any intermediate artifact.
- **Idempotent stages.** Running any script twice with the same inputs produces the same output. There are no side effects beyond file writes.
- **Exit codes as signals.** `scan_drift.py` exits with code 2 when drift exceeds the configured threshold, enabling CI/CD integration via standard Unix conventions.

## Core Pipeline

The pipeline consists of 7 scripts that run sequentially via `make full-analysis`. Each script is independently executable.

| # | Script | Purpose | Input | Output |
|---|--------|---------|-------|--------|
| 1 | `parse_trivy.py` | Normalize Trivy vulnerability scan results into a standard schema | Trivy JSON output | Normalized vulnerability records |
| 2 | `parse_semgrep.py` | Normalize Semgrep static analysis results into the same schema | Semgrep JSON output | Normalized finding records |
| 3 | `gen_sbom.sh` | Generate Software Bill of Materials using Syft/CycloneDX across 5 ecosystems | Target codebase | SBOM in CycloneDX + SPDX format |
| 4 | `scan_drift.py` | Detect architecture drift by comparing dependency graph snapshots | Two graph JSON snapshots + threshold | Drift report with boundary violations |
| 5 | `ownership_diff.py` | Analyze git blame and commit history to identify knowledge concentration | Git repository + time window | Ownership concentration scores per directory |
| 6 | `hotspot_merge.py` | Merge churn, complexity, coverage, and criticality signals into composite risk scores | Churn data + complexity JSON + optional coverage/criticality | Weighted risk scores per file |
| 7 | `risk_update.py` | Aggregate all upstream reports into a prioritized consolidated risk register | Any combination of hotspots, drift, ownership, and security JSONs | Timestamped risk register with severity classifications |

The canonical invocation is:

```bash
make full-analysis
```

This runs stages 4-7 in order (hotspots, ownership, drift, risk). Security normalization (stages 1-2) and SBOM generation (stage 3) are run separately because they depend on external scanner output. Individual stages can also be run independently if you only need a subset of the analysis.

## Risk Scoring Model

The composite risk score for each file is computed by `hotspot_merge.py` using a weighted linear formula. Four input signals are combined:

```
risk = (norm_churn * W_churn) + (norm_complexity * W_complexity) 
     + (coverage_penalty * W_coverage) + (norm_criticality * W_criticality)
```

Where:

- **`norm_churn`** = `file_churn / max_churn` — how frequently this file has changed in the analysis window (default: 90 days). High churn indicates instability.
- **`norm_complexity`** = `avg_cyclomatic_complexity / max_cc` — the average cyclomatic complexity of functions in the file, as measured by radon or equivalent. High complexity indicates maintenance burden.
- **`coverage_penalty`** = `1 - test_coverage` — inverted test coverage. Low coverage means high penalty. Files with unknown coverage default to 0.5 (uncertain, not assumed-bad).
- **`norm_criticality`** = `business_criticality / max_criticality` — a manually assigned 1-5 score reflecting business impact. A payment processing module scores higher than an internal admin tool.

### Default Weights

The default weights in `config/risk_weights.yaml` are:

| Signal | Weight | Rationale |
|--------|--------|-----------|
| Churn | 0.30 | Volatile files are harder to reason about |
| Complexity | 0.35 | Complex code is the primary maintenance burden |
| Coverage gap | 0.15 | Missing tests compound other risks |
| Criticality | 0.10 | Business impact provides prioritization context |
| Security hotspot | 0.10 | Optional extension for vulnerability presence |

Weights can be overridden via environment variables (`RISK_W_CHURN`, `RISK_W_COMPLEXITY`, `RISK_W_COVERAGE`, `RISK_W_CRITICALITY`) or by editing the YAML config. The script normalizes weights to sum to 1.0 regardless of input values.

### Severity Classification

`risk_update.py` converts numeric risk scores into severity labels using configurable thresholds:

| Score Range | Severity | Action |
|-------------|----------|--------|
| >= 0.70 | **HIGH** | Immediate attention — schedule remediation this sprint |
| >= 0.50 | **MEDIUM** | Plan remediation within 90 days |
| < 0.50 | **LOW** | Monitor; address opportunistically |

### Severity Escalation Rules

Certain conditions trigger automatic severity escalation regardless of the base score:

- Security findings rated CRITICAL or HIGH by the scanner pass through as HIGH severity
- Single-contributor directories with criticality >= 3 escalate to HIGH
- Any drift boundary violation is at least MEDIUM
- Drift churn ratio >= 0.30 escalates architecture drift findings to HIGH

### Output Format

`hotspot_merge.py` writes a JSON file with full transparency into the scoring:

```json
{
  "meta": {
    "weights": { "churn": 0.3, "complexity": 0.35, "coverage": 0.15, "criticality": 0.1 }
  },
  "hotspots": [
    {
      "file": "src/core/payment_validator.py",
      "churn": 47,
      "avg_complexity": 8.3,
      "coverage": 0.42,
      "criticality": 5,
      "risk_score": 0.7821,
      "components": {
        "churn": 0.2100,
        "complexity": 0.2905,
        "coverage_penalty": 0.0870,
        "criticality_factor": 0.1000
      }
    }
  ]
}
```

The `components` breakdown lets you see exactly which signals drove the score, making it possible to have informed conversations about remediation strategy — should you reduce complexity, add tests, or spread knowledge?

## Architecture Drift Detection

`scan_drift.py` is the most theoretically interesting script in the pipeline. It operates on a premise drawn from control theory: if you can declare what your system boundaries *should* be, the tool can tell you where reality has diverged.

### How It Works

The script compares two dependency graph snapshots — a "previous" baseline and a "current" state — and computes:

1. **Added nodes** — new modules or services that did not exist in the baseline
2. **Removed nodes** — modules or services that have disappeared
3. **Added edges** — new dependencies between modules
4. **Removed edges** — dependencies that have been severed
5. **Edge churn ratio** — `(added_edges + removed_edges) / previous_edge_count`, a single number summarizing the rate of structural change
6. **Core boundary violations** — the most critical heuristic: new edges where the target node previously had zero incoming edges. A module with zero in-degree was architecturally isolated — a leaf or boundary. A new edge into it represents a boundary breach, potentially unintentional coupling.

### Graph Schema

Both snapshots use a simple JSON schema:

```json
{
  "nodes": [
    { "id": "moduleA", "group": "serviceX" }
  ],
  "edges": [
    { "from": "moduleA", "to": "moduleB", "type": "import" }
  ],
  "meta": {
    "ref": "abc123",
    "generated_at": "2025-10-29T00:00:00Z"
  }
}
```

This schema is deliberately minimal. You can generate it from AST parsing (for Python or JavaScript import analysis), from `go mod graph`, from explicit service declarations, or from any other dependency extraction tool. The drift detector does not care how the graph was produced — it only compares two snapshots.

### Exit Codes

- **0** — drift is below the configured threshold (default: 10% edge churn)
- **2** — drift exceeds the threshold, signaling that architectural review is warranted

This convention enables CI/CD integration: a GitHub Actions step can run drift detection and fail the build if the architecture has changed more than expected.

### Integrity Verification

The output includes a SHA-256 hash of the summary fields, allowing downstream consumers to verify that the drift report has not been tampered with between generation and consumption.

## Ownership and Knowledge Concentration

`ownership_diff.py` answers the question that org charts cannot: *who actually understands this code?*

The script runs `git log` over a configurable time window (default: 90 days) and computes per-directory authorship concentration. For each directory (at a configurable depth), it calculates:

- **Total commits** — the volume of activity
- **Author distribution** — each contributor's commit count and percentage
- **Top concentration** — the highest single-author percentage
- **Flag** — either `HIGH_CONCENTRATION` (top author > 60% but not sole contributor) or `SINGLE_CONTRIBUTOR` (only one person has touched the directory)

The flag thresholds are configurable. The default 60% threshold is deliberately aggressive — it flags directories where a single person has done most of the work even if others have contributed. This is because a 60/20/20 split means two people could leave and the remaining person still would not fully understand the module.

An optional criticality mapping (YAML) allows you to weight the importance of each directory. A `SINGLE_CONTRIBUTOR` flag on a criticality-5 payment processing directory is far more concerning than the same flag on an internal utility script.

## Security Normalization Layer

The toolkit does not perform security scanning itself — it normalizes the output of existing scanners into a unified schema that feeds into the risk aggregator.

### Trivy Parser (`parse_trivy.py`)

Ingests Trivy JSON output and produces normalized findings with:
- Standardized severity mapping (Trivy CRITICAL maps to HIGH in the risk model)
- Component identification (`target::package@version`)
- Actionable recommendations (upgrade path when a fixed version exists)
- CVE cross-references for audit trails

### Semgrep Parser (`parse_semgrep.py`)

Ingests Semgrep JSON output with severity mapping:
- `ERROR` maps to `HIGH`
- `WARNING` maps to `MEDIUM`
- `INFO` maps to `LOW`

Both parsers produce JSON arrays with the same schema, making them interchangeable inputs to `risk_update.py`. This normalization layer means you can swap Trivy for Grype, or Semgrep for CodeQL, by writing a single parser script that outputs the same schema.

## Installation and Quick Start

### Prerequisites

- Python 3.11+ (standard library only for core scripts; `pyyaml` optional for YAML config)
- Git (for ownership analysis)
- Make (for pipeline orchestration)

Optional for extended features:
- Docker (for containerized analysis)
- radon (`pip install radon`) for Python complexity metrics
- Trivy and/or Semgrep for security scanning
- Syft for SBOM generation

### Option 1: Run Directly

```bash
# Clone the repository
git clone https://github.com/organvm-i-theoria/reverse-engine-recursive-run.git
cd reverse-engine-recursive-run

# Edit service_paths.yaml to declare your architecture
# (see Configuration Reference below)

# Run the full analysis pipeline
make full-analysis

# Results appear in artifacts/
cat artifacts/consolidated_risk.json | python3 -m json.tool
```

### Option 2: Run in Docker

```bash
# Build the analysis image
docker build -f Dockerfile.analysis -t reverse-engine .

# Mount your target codebase and run
docker run --rm \
  -v /path/to/your/codebase:/workspace \
  reverse-engine \
  make full-analysis
```

### Option 3: Run Individual Scripts

```bash
# Ownership analysis only (runs git log internally)
python3 scripts/ownership_diff.py --days 90 --depth 2 --out ownership.json

# Hotspot analysis only (requires pre-generated churn and complexity data)
python3 scripts/hotspot_merge.py \
  --churn churn.txt \
  --complexity complexity.json \
  --out hotspots.json

# Drift detection only
python3 scripts/scan_drift.py \
  --current current_graph.json \
  --previous previous_graph.json \
  --threshold 0.1 \
  --out drift_report.json

# Risk aggregation (accepts any subset of inputs)
python3 scripts/risk_update.py \
  --hotspots hotspots.json \
  --drift drift_report.json \
  --ownership ownership.json \
  --out consolidated_risk.json
```

See `QUICKSTART.md` for detailed setup instructions with troubleshooting guidance, and `scripts/README.md` for per-script documentation.

## Configuration Reference

All configuration is file-based. There are no environment variables required (though `hotspot_merge.py` accepts optional weight overrides via `RISK_W_*` env vars).

### `config/risk_weights.yaml`

Controls the risk scoring model:

```yaml
weights:
  churn: 0.30          # Code volatility (git activity)
  complexity: 0.35     # Cyclomatic complexity
  coverage_gap: 0.15   # Missing test coverage
  criticality: 0.10    # Business impact weight
  security_hotspot: 0.10  # Vulnerability presence

thresholds:
  hotspot_high: 0.70      # Score >= this = HIGH severity
  hotspot_medium: 0.50    # Score >= this = MEDIUM severity
  ownership_concentration: 0.60   # Flag above this %
  drift_churn_high: 0.30  # Drift ratio >= this = HIGH
  drift_churn_medium: 0.12  # Drift ratio >= this = MEDIUM
```

Tuning guidance: increase the complexity weight during a refactoring phase to surface the worst tangles. Increase the churn weight before a release freeze to identify volatile modules that need stabilization.

### `config/service_paths.yaml`

Declares your intended architecture — the service boundaries that drift detection compares against:

```yaml
services:
  payments-service:
    paths:
      - "src/payments/"
      - "src/core/payment"
  billing-service:
    paths:
      - "src/billing/"
      - "src/core/billing"
  admin-portal:
    paths:
      - "src/ui/admin/"
```

This file answers: *what services exist, and which directories belong to each?* When `scan_drift.py` finds an import that crosses these boundaries unexpectedly, it flags a boundary violation.

## Pipeline Orchestration via Make

The Makefile provides named targets for each analysis stage:

| Target | What It Does |
|--------|-------------|
| `make full-analysis` | Run the complete pipeline: hotspots, ownership, drift, risk aggregation |
| `make hotspots` | Generate churn data from git, create placeholder complexity, merge into hotspot report |
| `make ownership` | Run ownership concentration analysis |
| `make drift` | Run drift detection (creates baseline graph on first run) |
| `make risk` | Aggregate all available reports into consolidated risk register |
| `make sbom` | Generate SBOM via `gen_sbom.sh` |
| `make build-analysis-image` | Build the Docker analysis image |
| `make clean` | Remove the `artifacts/` directory |
| `make adr-new TITLE='...'` | Create a new Architecture Decision Record |

All targets create the `artifacts/` directory if it does not exist.

## Templates and Outputs

The `templates/` directory contains two structured output templates:

### Executive Summary (`templates/executive_summary_template.md`)

A comprehensive Markdown template with 13 sections designed for architecture review boards, leadership briefings, and audit submissions. Includes placeholders for:

- Architecture snapshot with layer mapping
- Top-5 findings with impact and severity
- Risk heat map across security, drift, knowledge concentration, performance, and compliance
- Code-level hotspots with component breakdowns
- Security posture assessment
- KPI baselines and targets

### Remediation Backlog (`templates/remediation_backlog.yaml`)

A structured YAML template for tracking prioritized remediation items. Each item includes:

- Impact, urgency, and criticality scores (1-5 scale)
- Effort estimate (S/M/L)
- Priority formula: `(impact * urgency * criticality) / effort_weight`
- Acceptance criteria (testable conditions for closure)
- Issue tracker cross-references
- Owner and target date

The template ships with 5 example items covering code quality, security, architecture drift, knowledge concentration, and observability gaps. Replace these with your actual findings.

## Containerized Analysis

The `Dockerfile.analysis` provides a reproducible analysis environment based on Ubuntu 22.04 with:

- **Python 3** — for the analysis scripts and radon complexity metrics
- **Node.js 20** — for JavaScript/TypeScript import analysis and CycloneDX npm plugin
- **Go 1.22** — for Go dependency analysis and module graph extraction
- **Pre-installed tools** — radon 6.0.1, pipdeptree 2.23.1, cyclonedx-bom 4.3.5, pyyaml 6.0.2
- **Graphviz** — for dependency graph visualization (future roadmap)

The image is designed for ephemeral analysis runs, not as a long-running service. Mount your target codebase at `/workspace` and run any Make target or individual script.

## SBOM Generation

`gen_sbom.sh` automatically detects and generates SBOMs for up to 5 ecosystems:

| Ecosystem | Detection | Tool | Output Format |
|-----------|-----------|------|---------------|
| Node.js | `package.json` | `@cyclonedx/cyclonedx-npm` | CycloneDX JSON |
| Python | `requirements.txt` or `pyproject.toml` | `cyclonedx-py` + `pipdeptree` | CycloneDX JSON |
| Go | `go.mod` | `syft` | CycloneDX JSON |
| Java | `pom.xml` or `*.gradle` | Maven dependency:tree | Text |
| Rust | `Cargo.toml` | `cargo metadata` + `syft` | CycloneDX JSON |

The script consolidates all CycloneDX fragments into a single `sbom_combined.cyclonedx.json` with deduplicated components, a UUID serial number, and the source git ref embedded in metadata. If Syft is available, it also generates an SPDX JSON output.

The SBOM outputs contain only dependency coordinates (package names, versions, licenses) — never source code. This makes them safe for distribution in compliance contexts (SOX, PCI DSS, HIPAA, ISO 27001) without exposing proprietary implementation details.

## ADR Scaffolding

Architecture Decision Records provide a paper trail for governance decisions. The toolkit includes:

- **`scripts/adr_new.sh`** — creates a new ADR from the template with auto-incrementing four-digit numbering. Usage: `make adr-new TITLE='Adopt Event-Driven Architecture'`
- **`docs/adr/ADR_TEMPLATE.md`** — a structured template with sections for Context, Decision, Alternatives Considered, Consequences, Implementation Plan, and Metrics/Validation
- **`docs/adr/0000-record-architecture-decisions.md`** — the meta-ADR documenting the decision to use ADRs, serving as both the index and the workflow reference

ADR scaffolding is included alongside the analysis toolkit because governance decisions should be recorded in the same context where problems are detected. When drift analysis identifies a boundary violation, the ADR scaffolding provides an immediate place to document the response: was the boundary intentionally changed, or was this accidental coupling that needs to be reversed?

## Repository Structure

```
reverse-engine-recursive-run/
├── Makefile                              # Pipeline orchestration
├── Dockerfile.analysis                   # Reproducible environment (Ubuntu 22.04)
├── README.md                             # This document
├── QUICKSTART.md                         # Setup and first-run guide
├── config/
│   ├── risk_weights.yaml                 # Tunable risk signal weights and thresholds
│   └── service_paths.yaml                # Declared service boundaries for drift detection
├── scripts/
│   ├── README.md                         # Per-script documentation and CI pipeline diagram
│   ├── hotspot_merge.py                  # Risk scoring — 4-signal weighted linear model
│   ├── scan_drift.py                     # Architecture drift — graph diff with boundary flags
│   ├── ownership_diff.py                 # Knowledge concentration — git authorship analysis
│   ├── risk_update.py                    # Aggregation — consolidates all upstream reports
│   ├── parse_trivy.py                    # Security normalization — Trivy output
│   ├── parse_semgrep.py                  # Security normalization — Semgrep output
│   ├── gen_sbom.sh                       # SBOM generation — 5-ecosystem auto-detection
│   └── adr_new.sh                        # ADR scaffolding — numbered record creation
├── templates/
│   ├── executive_summary_template.md     # 13-section report template for leadership
│   └── remediation_backlog.yaml          # Prioritized backlog with scoring formula
├── docs/
│   ├── summary_compiled.md               # 3,000+ word methodology reference
│   └── adr/
│       ├── 0000-record-architecture-decisions.md  # ADR index and workflow
│       └── ADR_TEMPLATE.md               # Template for new ADRs
└── .gitignore
```

**22 files, ~158KB total. Pure Python + shell. No external Python dependencies beyond the standard library.**

## Design Decisions and Trade-offs

### Why single-file scripts instead of a package?

Each script is a standalone CLI tool with no cross-imports. This means you can copy any single script into another project and use it immediately. The cost is some duplication (each script has its own argparse setup and JSON loading) and no shared utilities. The benefit is zero coupling between tools — you can adopt hotspot analysis without drift detection, or vice versa.

### Why JSON as the integration format?

JSON is universally readable, trivially debuggable (`cat artifacts/hotspots.json | python3 -m json.tool`), and requires no additional libraries. Every intermediate artifact is human-inspectable. The alternative — an in-process pipeline with shared Python objects — would be faster but opaque. For a governance toolkit, transparency matters more than performance.

### Why a linear risk model instead of something more sophisticated?

The weighted linear model is explainable. When you present a risk score to a team lead, they can see exactly which signals drove it and by how much. A neural network or random forest might produce more accurate rankings, but it cannot answer "why is this file risky?" in a way that leads to actionable conversation. Governance tools must be interpretable.

### Why standard library only?

No `pip install` step means no dependency conflicts, no virtual environment setup, and no supply chain risk from third-party packages. The only optional dependency is `pyyaml` for YAML config loading, and even that falls back gracefully (the scripts accept JSON configuration as well). This is a governance tool — it should not itself be a source of dependency risk.

### Why exit code 2 for drift breach?

Exit code 1 conventionally means "general error." Exit code 2 means "drift threshold exceeded" — a structured, expected condition that CI/CD can act on. This follows the convention of tools like `grep` (exit 1 = no match, not an error) and allows pipelines to distinguish between "the tool crashed" and "the tool ran successfully and found a problem."

## Extending the Toolkit

The toolkit is designed for extension through new scripts that follow the same conventions:

- **New risk dimension:** Write a script that produces a JSON file with per-file or per-directory scores. Add it as a new signal in `hotspot_merge.py` or as a new input to `risk_update.py`.
- **New scanner parser:** Follow the pattern of `parse_trivy.py` — read the scanner's native JSON, output a list of `{ "id", "severity", "component", "desc", "recommendation" }` objects.
- **New output format:** Write a script that reads `consolidated_risk.json` and produces your desired output (Jira tickets, Slack messages, Backstage annotations, etc.).
- **Coverage integration:** Produce a `coverage.json` file with `{ "files": { "path": fraction } }` and pass it to `hotspot_merge.py --coverage`.
- **Custom criticality:** Create a YAML file mapping file paths or directories to 1-5 criticality scores and pass it to `hotspot_merge.py --criticality` or `ownership_diff.py --criticality`.

## Roadmap

The following capabilities are planned but **do not exist in the current codebase**:

- **Test suite** — unit tests for each script, integration tests for the full pipeline, and property-based tests for the risk scoring model
- **Formal packaging** — `pyproject.toml` with proper dependency declaration, versioned releases, and `pip install` support
- **CI/CD integration** — GitHub Actions workflow that runs the pipeline on pull requests and comments with risk score changes
- **Backstage plugin** — a read-only Backstage catalog integration that surfaces risk scores alongside service metadata
- **Scheduling and continuous monitoring** — cron-driven or event-driven pipeline execution with historical trend tracking and time-series persistence
- **Additional language support** — expand import analysis beyond Python and JavaScript to cover Rust, Go, and Java
- **Visualization** — dependency graph rendering with drift violations highlighted, exportable as SVG
- **Non-linear risk model** — optional exponential scaling for extreme values, Z-score anomaly detection on time-series data
- **GraphQL API** — for UI components to query risk slices per service

Contributions toward any of these are welcome. The current scripts are deliberately simple (single-file, standard library only) to make extension straightforward.

## Cross-Organ References

| Resource | Organ | Relationship |
|----------|-------|-------------|
| [recursive-engine](https://github.com/organvm-i-theoria/recursive-engine) | I — Theoria | Flagship ORGAN-I repository exploring recursive system theory and self-referential computation. This toolkit applies that recursive principle to software governance: the system examines itself. |
| [ORGAN-I: Theoria](https://github.com/organvm-i-theoria) | I — Theoria | Parent organization. Theory, epistemology, recursion, ontology. |
| [ORGAN-IV: Taxis](https://github.com/organvm-iv-taxis) | IV — Taxis | Orchestration organ. This toolkit's risk primitives feed into ORGAN-IV's cross-organ governance routing. |
| [agentic-titan](https://github.com/organvm-iv-taxis/agentic-titan) | IV — Taxis | Agentic orchestration system. Could consume this toolkit's outputs as governance signals for automated decision-making. |
| [meta-organvm](https://github.com/meta-organvm) | VIII — Meta | Umbrella governance across all 8 organs. This toolkit exemplifies the meta-governance principle at the individual-repo scale. |

This repository belongs to ORGAN-I because architecture governance is fundamentally a theoretical concern: it asks "what *should* the system look like?" and measures deviation from that ideal. The toolkit operationalizes architectural intent — making it a bridge between theory (ORGAN-I) and orchestration (ORGAN-IV). It does not orchestrate; it observes, measures, and reports. The orchestration — deciding what to do about the findings — is ORGAN-IV's domain.

## Related Work

- **[Backstage](https://backstage.io/)** — Spotify's developer portal. This toolkit's outputs are designed to feed into Backstage's catalog annotations. The planned Backstage plugin would surface risk scores, hotspots, and drift metrics alongside service metadata.
- **[radon](https://radon.readthedocs.io/)** — Python cyclomatic complexity analyzer. Used upstream of `hotspot_merge.py` to generate complexity metrics.
- **[Trivy](https://trivy.dev/)** — Aqua Security's vulnerability scanner. `parse_trivy.py` normalizes its output.
- **[Semgrep](https://semgrep.dev/)** — Static analysis tool. `parse_semgrep.py` normalizes its output.
- **[Syft](https://github.com/anchore/syft)** — SBOM generation tool by Anchore. Used by `gen_sbom.sh`.
- **[ArchUnit](https://www.archunit.org/)** — Java architecture testing library. Solves a similar problem (architecture-as-code) but is language-specific and test-oriented rather than pipeline-oriented.
- **[Fitness Functions](https://www.thoughtworks.com/insights/articles/fitness-function-driven-development)** — The concept from *Building Evolutionary Architectures* that inspired drift detection's approach: declare architectural properties, then continuously verify them.

## Contributing

Contributions are welcome, particularly toward the [Roadmap](#roadmap) items. The toolkit is designed to be extended by adding new scripts that follow the existing conventions:

1. Single-file Python scripts with standard library only
2. CLI via `argparse` with `--out` for output path
3. JSON output for inter-script communication
4. Descriptive docstrings at the top of each file documenting inputs, outputs, and schema

Please open an issue before starting work on a major feature to discuss approach.

## License

MIT License. See [LICENSE](LICENSE) for full text.

---

**Author:** **[@4444J99](https://github.com/4444J99)** / Part of [ORGAN-I: Theoria](https://github.com/organvm-i-theoria)
