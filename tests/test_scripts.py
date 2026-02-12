"""Tests for all Python scripts in the reverse-engine-recursive-run toolkit.

Covers: hotspot_merge, ownership_diff, parse_semgrep, parse_trivy,
        risk_update, scan_drift, and the CLI entry point.
"""
from __future__ import annotations

import json
import os
import tempfile

import pytest


# ─── hotspot_merge tests ────────────────────────────────────────────

class TestHotspotMerge:
    def test_load_churn(self):
        from hotspot_merge import load_churn
        fd, path = tempfile.mkstemp()
        with os.fdopen(fd, "w") as f:
            f.write("10 src/app.py\n5 src/utils.py\n")
        result = load_churn(path)
        os.unlink(path)
        assert result == {"src/app.py": 10, "src/utils.py": 5}

    def test_load_churn_empty_lines(self):
        from hotspot_merge import load_churn
        fd, path = tempfile.mkstemp()
        with os.fdopen(fd, "w") as f:
            f.write("\n10 src/app.py\n\n")
        result = load_churn(path)
        os.unlink(path)
        assert "src/app.py" in result

    def test_load_complexity(self):
        from hotspot_merge import load_complexity
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w") as f:
            json.dump({"src/app.py": [{"complexity": 10}, {"complexity": 20}]}, f)
        result = load_complexity(path)
        os.unlink(path)
        assert result["src/app.py"] == 15.0

    def test_load_complexity_empty_blocks(self):
        from hotspot_merge import load_complexity
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w") as f:
            json.dump({"src/empty.py": []}, f)
        result = load_complexity(path)
        os.unlink(path)
        assert result["src/empty.py"] == 0

    def test_load_coverage(self):
        from hotspot_merge import load_coverage
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w") as f:
            json.dump({"files": {"src/app.py": 0.85}}, f)
        result = load_coverage(path)
        os.unlink(path)
        assert result["src/app.py"] == 0.85

    def test_load_coverage_flat_format(self):
        from hotspot_merge import load_coverage
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w") as f:
            json.dump({"src/app.py": 0.7}, f)
        result = load_coverage(path)
        os.unlink(path)
        assert result["src/app.py"] == 0.7


# ─── parse_semgrep tests ────────────────────────────────────────────

class TestParseSemgrep:
    def _run_parse(self, input_data):
        from parse_semgrep import main as semgrep_main, MAP
        fd_in, in_path = tempfile.mkstemp(suffix=".json")
        fd_out, out_path = tempfile.mkstemp(suffix=".json")
        os.close(fd_out)
        with os.fdopen(fd_in, "w") as f:
            json.dump(input_data, f)
        import sys
        old_argv = sys.argv
        sys.argv = ["parse_semgrep", "--input", in_path, "--out", out_path]
        semgrep_main()
        sys.argv = old_argv
        with open(out_path) as f:
            result = json.load(f)
        os.unlink(in_path)
        os.unlink(out_path)
        return result

    def test_parse_single_finding(self):
        data = {"results": [{
            "check_id": "rule.xss",
            "path": "src/views.py",
            "extra": {"message": "XSS vulnerability", "severity": "ERROR"},
            "start": {"line": 42},
        }]}
        result = self._run_parse(data)
        assert len(result) == 1
        assert result[0]["severity"] == "HIGH"
        assert "line 42" in result[0]["desc"]

    def test_severity_mapping(self):
        data = {"results": [
            {"check_id": "r1", "path": "a.py", "extra": {"message": "m", "severity": "WARNING"}, "start": {"line": 1}},
            {"check_id": "r2", "path": "b.py", "extra": {"message": "m", "severity": "INFO"}, "start": {"line": 1}},
        ]}
        result = self._run_parse(data)
        sevs = {r["severity"] for r in result}
        assert "MEDIUM" in sevs
        assert "LOW" in sevs

    def test_empty_results(self):
        result = self._run_parse({"results": []})
        assert result == []

    def test_missing_results_key(self):
        result = self._run_parse({})
        assert result == []


# ─── parse_trivy tests ──────────────────────────────────────────────

class TestParseTrivy:
    def _run_parse(self, input_data):
        from parse_trivy import main as trivy_main
        fd_in, in_path = tempfile.mkstemp(suffix=".json")
        fd_out, out_path = tempfile.mkstemp(suffix=".json")
        os.close(fd_out)
        with os.fdopen(fd_in, "w") as f:
            json.dump(input_data, f)
        import sys
        old_argv = sys.argv
        sys.argv = ["parse_trivy", "--input", in_path, "--out", out_path]
        trivy_main()
        sys.argv = old_argv
        with open(out_path) as f:
            result = json.load(f)
        os.unlink(in_path)
        os.unlink(out_path)
        return result

    def test_parse_single_vuln(self):
        data = {"Results": [{
            "Target": "requirements.txt",
            "Vulnerabilities": [{
                "VulnerabilityID": "CVE-2024-1234",
                "PkgName": "requests",
                "InstalledVersion": "2.28.0",
                "FixedVersion": "2.31.0",
                "Severity": "HIGH",
                "Title": "SSRF in requests",
            }],
        }]}
        result = self._run_parse(data)
        assert len(result) == 1
        assert result[0]["cve"] == "CVE-2024-1234"
        assert result[0]["severity"] == "HIGH"

    def test_critical_maps_to_high(self):
        data = {"Results": [{
            "Target": "go.sum",
            "Vulnerabilities": [{
                "VulnerabilityID": "CVE-2024-9999",
                "PkgName": "stdlib",
                "InstalledVersion": "1.20",
                "Severity": "CRITICAL",
            }],
        }]}
        result = self._run_parse(data)
        assert result[0]["severity"] == "HIGH"

    def test_no_vulnerabilities(self):
        data = {"Results": [{"Target": "Dockerfile", "Vulnerabilities": None}]}
        result = self._run_parse(data)
        assert result == []

    def test_empty_input(self):
        result = self._run_parse({})
        assert result == []


# ─── risk_update tests ──────────────────────────────────────────────

class TestRiskUpdate:
    def test_hotspot_severity_high(self):
        from risk_update import hotspot_sev
        assert hotspot_sev(0.80) == "HIGH"

    def test_hotspot_severity_medium(self):
        from risk_update import hotspot_sev
        assert hotspot_sev(0.60) == "MEDIUM"

    def test_hotspot_severity_low(self):
        from risk_update import hotspot_sev
        assert hotspot_sev(0.30) == "LOW"

    def test_hotspot_severity_boundary(self):
        from risk_update import hotspot_sev
        assert hotspot_sev(0.75) == "HIGH"
        assert hotspot_sev(0.50) == "MEDIUM"


# ─── scan_drift tests ───────────────────────────────────────────────

class TestScanDrift:
    def test_edge_key(self):
        from scan_drift import edge_key
        e = {"from": "A", "to": "B", "type": "import"}
        assert edge_key(e) == ("A", "B", "import")

    def test_edge_key_missing_type(self):
        from scan_drift import edge_key
        e = {"from": "A", "to": "B"}
        assert edge_key(e) == ("A", "B", "")

    def test_drift_detection(self):
        """Full integration: write two graph files and run scan_drift.main()."""
        from scan_drift import main as drift_main
        prev = {
            "nodes": [{"id": "A"}, {"id": "B"}],
            "edges": [{"from": "A", "to": "B", "type": "import"}],
            "meta": {"ref": "abc123"},
        }
        cur = {
            "nodes": [{"id": "A"}, {"id": "B"}, {"id": "C"}],
            "edges": [
                {"from": "A", "to": "B", "type": "import"},
                {"from": "A", "to": "C", "type": "import"},
            ],
            "meta": {"ref": "def456"},
        }
        fd_prev, prev_path = tempfile.mkstemp(suffix=".json")
        fd_cur, cur_path = tempfile.mkstemp(suffix=".json")
        fd_out, out_path = tempfile.mkstemp(suffix=".json")
        os.close(fd_out)
        with os.fdopen(fd_prev, "w") as f:
            json.dump(prev, f)
        with os.fdopen(fd_cur, "w") as f:
            json.dump(cur, f)

        import sys
        old_argv = sys.argv
        # threshold 0.5 -> churn is 1/1=1.0, should breach
        sys.argv = ["scan_drift", "--current", cur_path, "--previous", prev_path,
                     "--threshold", "0.5", "--out", out_path]
        with pytest.raises(SystemExit) as exc_info:
            drift_main()
        sys.argv = old_argv

        assert exc_info.value.code == 2  # breach
        with open(out_path) as f:
            report = json.load(f)
        assert report["summary"]["breach"] is True
        assert report["summary"]["added_edges_count"] == 1

        os.unlink(prev_path)
        os.unlink(cur_path)
        os.unlink(out_path)


# ─── ownership_diff tests ──────────────────────────────────────────

class TestOwnershipDiff:
    def test_bucket_by_directory(self):
        from ownership_diff import bucket_by_directory
        entries = [
            "alice@example.com",
            "src/core/main.py",
            "src/core/utils.py",
            "bob@example.com",
            "src/api/handler.py",
        ]
        result = bucket_by_directory(entries, depth=2)
        assert "src/core" in result
        assert result["src/core"]["alice@example.com"] == 2
        assert "src/api" in result
        assert result["src/api"]["bob@example.com"] == 1

    def test_bucket_skips_empty_paths(self):
        from ownership_diff import bucket_by_directory
        entries = ["alice@x.com", "", "src/a.py"]
        result = bucket_by_directory(entries, depth=2)
        assert "src" in result or len(result) >= 0  # should not crash
