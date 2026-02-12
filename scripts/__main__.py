"""CLI entry point for reverse-engine-recursive-run analysis toolkit.

Usage:
    python -m scripts analyze --churn churn.txt --complexity complexity.json --out hotspots.json
    python -m scripts risk --hotspots hotspots.json --out risk.json
    python -m scripts drift --current graph.json --previous prev.json --out drift.json
    python -m scripts sbom (placeholder — wraps gen_sbom.sh)
"""
from __future__ import annotations

import argparse
import json
import sys


def cmd_analyze(args: argparse.Namespace) -> int:
    """Run hotspot analysis using hotspot_merge logic."""
    from hotspot_merge import load_churn, load_complexity, load_coverage
    import os, math

    churn = load_churn(args.churn)
    complexity = load_complexity(args.complexity)
    coverage = load_coverage(args.coverage) if args.coverage else {}

    max_churn = max(churn.values()) if churn else 1
    max_cc = max(complexity.values()) if complexity else 1

    w_churn = float(os.getenv("RISK_W_CHURN", "0.4"))
    w_complexity = float(os.getenv("RISK_W_COMPLEXITY", "0.4"))
    w_coverage = float(os.getenv("RISK_W_COVERAGE", "0.1"))
    w_crit = float(os.getenv("RISK_W_CRITICALITY", "0.1"))
    total = w_churn + w_complexity + w_coverage + w_crit
    if not math.isclose(total, 1.0):
        w_churn /= total
        w_complexity /= total
        w_coverage /= total
        w_crit /= total

    files = set(churn) | set(complexity) | set(coverage)
    records = []
    for f in files:
        c = churn.get(f, 0)
        cc = complexity.get(f, 0)
        cov = coverage.get(f, 0.5)
        norm_churn = c / max_churn if max_churn else 0
        norm_cc = cc / max_cc if max_cc else 0
        risk = norm_churn * w_churn + norm_cc * w_complexity + (1 - cov) * w_coverage + w_crit
        records.append({"file": f, "risk_score": round(risk, 4)})

    records.sort(key=lambda r: r["risk_score"], reverse=True)
    top = records[: args.top]

    with open(args.out, "w") as fh:
        json.dump({"hotspots": top}, fh, indent=2)
    print(f"[ANALYZE] Wrote {len(top)} hotspots to {args.out}")
    return 0


def cmd_risk(args: argparse.Namespace) -> int:
    """Consolidate risk from multiple sources."""
    from risk_update import load, hotspot_sev
    import time

    hotspots = load(args.hotspots) if args.hotspots else None
    security = load(args.security) if args.security else None

    derived = []
    if hotspots:
        for h in hotspots.get("hotspots", []):
            sev = hotspot_sev(h["risk_score"])
            derived.append({"id": f"RISK-HOTSPOT-{h['file']}", "severity": sev})
    if security:
        for finding in security:
            derived.append({"id": finding.get("id", "SEC-UNSET"), "severity": finding.get("severity", "MEDIUM")})

    out = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "derived_risks": derived,
    }
    with open(args.out, "w") as fh:
        json.dump(out, fh, indent=2)
    print(f"[RISK] Consolidated {len(derived)} risks to {args.out}")
    return 0


def cmd_drift(args: argparse.Namespace) -> int:
    """Compare dependency graphs for architecture drift."""
    from scan_drift import load, edge_key
    from collections import defaultdict

    cur = load(args.current)
    prev = load(args.previous)

    prev_edges = set(edge_key(e) for e in prev.get("edges", []))
    cur_edges = set(edge_key(e) for e in cur.get("edges", []))
    added = cur_edges - prev_edges
    removed = prev_edges - cur_edges
    prev_count = len(prev_edges) or 1
    churn = (len(added) + len(removed)) / prev_count

    print(f"[DRIFT] Added edges: {len(added)}, Removed: {len(removed)}, Churn: {churn:.4f}")
    return 0 if churn < args.threshold else 2


def cmd_sbom(args: argparse.Namespace) -> int:
    """Generate SBOM (placeholder — delegates to gen_sbom.sh)."""
    print("[SBOM] SBOM generation requires gen_sbom.sh — run it directly.")
    print("  Usage: bash scripts/gen_sbom.sh")
    return 0


def main(argv: list[str] | None = None) -> int:
    """Parse arguments and dispatch to the appropriate subcommand."""
    parser = argparse.ArgumentParser(
        prog="reverse-engine",
        description="Security analysis toolkit: hotspot, risk, drift, SBOM",
    )
    sub = parser.add_subparsers(dest="command")

    # analyze
    p_analyze = sub.add_parser("analyze", help="Run hotspot analysis")
    p_analyze.add_argument("--churn", required=True, help="Path to churn file")
    p_analyze.add_argument("--complexity", required=True, help="Path to complexity JSON")
    p_analyze.add_argument("--coverage", help="Optional coverage JSON")
    p_analyze.add_argument("--out", required=True, help="Output file")
    p_analyze.add_argument("--top", type=int, default=50, help="Top N hotspots")

    # risk
    p_risk = sub.add_parser("risk", help="Consolidate risk register")
    p_risk.add_argument("--hotspots", help="Hotspots JSON")
    p_risk.add_argument("--security", help="Security findings JSON")
    p_risk.add_argument("--out", required=True, help="Output file")

    # drift
    p_drift = sub.add_parser("drift", help="Check architecture drift")
    p_drift.add_argument("--current", required=True, help="Current graph JSON")
    p_drift.add_argument("--previous", required=True, help="Previous graph JSON")
    p_drift.add_argument("--threshold", type=float, default=0.1)
    p_drift.add_argument("--out", help="Output file")

    # sbom
    sub.add_parser("sbom", help="Generate SBOM")

    args = parser.parse_args(argv)
    if not args.command:
        parser.print_help()
        return 2

    dispatch = {
        "analyze": cmd_analyze,
        "risk": cmd_risk,
        "drift": cmd_drift,
        "sbom": cmd_sbom,
    }
    return dispatch[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
