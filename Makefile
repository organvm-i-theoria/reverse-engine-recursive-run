# Makefile for Architecture Governance Toolkit

.PHONY: help build-analysis-image run-analysis adr-new artifacts-dir

ANALYSIS_IMAGE=analysis:local
ARTIFACTS_DIR=artifacts

help:
	@echo "Architecture Governance Toolkit - Available Commands:"
	@echo ""
	@echo "Core Analysis:"
	@echo "  make artifacts-dir          - Create artifacts directory"
	@echo "  make build-analysis-image   - Build Docker analysis image"
	@echo "  make run-analysis           - Run analysis in Docker"
	@echo "  make hotspots               - Generate code hotspots"
	@echo "  make ownership              - Analyze code ownership"
	@echo "  make drift                  - Detect architecture drift"
	@echo "  make risk                   - Generate consolidated risk register"
	@echo "  make full-analysis          - Run complete analysis pipeline"
	@echo "  make adr-new TITLE='...'    - Create new ADR"
	@echo "  make clean                  - Remove artifacts directory"
	@echo ""
	@echo "Research System (NEW):"
	@echo "  make research-check-deps    - Check research system dependencies"
	@echo "  make research-profile       - Create organization profile"
	@echo "  make research-discover      - Discover similar repositories"
	@echo "  make research-similarity    - Calculate similarity scores"
	@echo "  make research-report        - Generate research summary"
	@echo "  make research-full          - Run complete research cycle"
	@echo "  make research-clean         - Remove research artifacts"
	@echo ""
	@echo "Environment Variables:"
	@echo "  GITHUB_TOKEN                - GitHub API token (for research-discover)"
	@echo ""

artifacts-dir:
	mkdir -p $(ARTIFACTS_DIR)/sbom $(ARTIFACTS_DIR)/timeseries

build-analysis-image:
	docker build -t $(ANALYSIS_IMAGE) -f Dockerfile.analysis .

run-analysis: artifacts-dir
	docker run --rm -v $(PWD):/workspace -w /workspace $(ANALYSIS_IMAGE) \
		bash -lc "bash scripts/gen_sbom.sh --out artifacts/sbom --ref \$$(git rev-parse HEAD)"

adr-new:
	@if [ -z "$(TITLE)" ]; then \
		echo "Error: TITLE is required. Usage: make adr-new TITLE='Decision Title'"; \
		exit 1; \
	fi
	bash scripts/adr_new.sh "$(TITLE)"

clean:
	rm -rf $(ARTIFACTS_DIR)

# Analysis pipeline targets (require Python and tools installed locally)
sbom:
	bash scripts/gen_sbom.sh --out artifacts/sbom --ref $$(git rev-parse HEAD)

hotspots: artifacts-dir
	@echo "Generating complexity metrics..."
	@mkdir -p artifacts
	@# Placeholder - replace with actual complexity tool
	@echo '{}' > artifacts/complexity.json
	@echo "Generating churn metrics..."
	@git log --since=90.days --name-only --pretty=format: 2>/dev/null | sort | grep -v '^$$' | uniq -c > artifacts/churn.txt || echo "" > artifacts/churn.txt
	@echo "Merging hotspots..."
	@python3 scripts/hotspot_merge.py --churn artifacts/churn.txt --complexity artifacts/complexity.json --out artifacts/hotspots.json 2>/dev/null || echo "[WARN] hotspot_merge.py requires adjustments"

ownership: artifacts-dir
	python3 scripts/ownership_diff.py --out artifacts/ownership.json

drift: artifacts-dir
	@# Requires current_graph.json and previous_graph.json
	@echo '{"nodes":[],"edges":[],"meta":{"ref":"'$$(git rev-parse HEAD)'"}}' > artifacts/current_graph.json
	@if [ ! -f artifacts/previous_graph.json ]; then cp artifacts/current_graph.json artifacts/previous_graph.json; fi
	python3 scripts/scan_drift.py --current artifacts/current_graph.json --previous artifacts/previous_graph.json --out artifacts/drift_report.json || true

risk: artifacts-dir
	python3 scripts/risk_update.py \
		--hotspots artifacts/hotspots.json \
		--drift artifacts/drift_report.json \
		--ownership artifacts/ownership.json \
		--out artifacts/consolidated_risk.json

full-analysis: hotspots ownership drift risk
	@echo "Full analysis complete. Check artifacts/ directory."

# ============================================================================
# Research System Targets
# ============================================================================

RESEARCH_ARTIFACTS=$(ARTIFACTS_DIR)/research
ORG_PROFILE=$(RESEARCH_ARTIFACTS)/profiles/org_profile.json
DISCOVERED_REPOS=$(RESEARCH_ARTIFACTS)/discoveries/discovered_repos.json
SIMILARITY_SCORES=$(RESEARCH_ARTIFACTS)/discoveries/similarity_scores.json

research-dirs:
	@mkdir -p $(RESEARCH_ARTIFACTS)/profiles
	@mkdir -p $(RESEARCH_ARTIFACTS)/discoveries
	@mkdir -p $(RESEARCH_ARTIFACTS)/analysis
	@mkdir -p $(RESEARCH_ARTIFACTS)/patterns
	@mkdir -p $(RESEARCH_ARTIFACTS)/recommendations
	@mkdir -p $(RESEARCH_ARTIFACTS)/feedback

research-profile: research-dirs
	@echo "========================================="
	@echo "Creating Organization Profile..."
	@echo "========================================="
	python3 scripts/research/profile_org.py \
		--path . \
		--artifacts $(ARTIFACTS_DIR) \
		--out $(ORG_PROFILE)
	@echo ""
	@echo "✓ Organization profile created: $(ORG_PROFILE)"

research-discover: research-profile
	@echo "========================================="
	@echo "Discovering Similar Repositories..."
	@echo "========================================="
	@if [ -z "$(GITHUB_TOKEN)" ]; then \
		echo "WARNING: GITHUB_TOKEN not set. Rate limits will be restrictive."; \
		echo "Set GITHUB_TOKEN environment variable for better results."; \
		echo ""; \
	fi
	python3 scripts/research/discover_repos.py \
		--config config/research/discovery_config.yaml \
		--profile $(ORG_PROFILE) \
		--out $(DISCOVERED_REPOS)
	@echo ""
	@echo "✓ Repository discovery complete: $(DISCOVERED_REPOS)"

research-similarity: research-discover
	@echo "========================================="
	@echo "Calculating Similarity Scores..."
	@echo "========================================="
	python3 scripts/research/similarity_scorer.py \
		--discovered $(DISCOVERED_REPOS) \
		--profile $(ORG_PROFILE) \
		--weights config/research/similarity_weights.yaml \
		--out $(SIMILARITY_SCORES)
	@echo ""
	@echo "✓ Similarity scoring complete: $(SIMILARITY_SCORES)"

research-report: research-similarity
	@echo "========================================="
	@echo "Research System Summary"
	@echo "========================================="
	@echo ""
	@echo "Organization Profile:"
	@python3 -c "import json; p=json.load(open('$(ORG_PROFILE)')); print(f\"  Fingerprint: {p.get('fingerprint', 'unknown')}\"); print(f\"  Languages: {', '.join(list(p.get('metrics', {}).get('primary_languages', []))[:5])}\"); print(f\"  Research Areas: {len(p.get('challenges', {}).get('research_areas', []))}\"); print(f\"  High Priority Challenges: {len(p.get('challenges', {}).get('high_priority', []))}\")"
	@echo ""
	@echo "Discovery Results:"
	@python3 -c "import json; d=json.load(open('$(SIMILARITY_SCORES)')); meta=d.get('similarity_metadata', {}); print(f\"  Total Scored: {meta.get('total_scored', 0)}\"); print(f\"  Above Threshold: {meta.get('above_threshold', 0)}\"); print(f\"  Threshold: {meta.get('threshold', 0)}\"); repos=d.get('repositories', []); print(f\"  Top 5 Matches:\"); [print(f\"    {i+1}. {r.get('full_name', 'unknown')} (score: {r.get('similarity_score', 0):.4f})\") for i, r in enumerate(repos[:5])]"
	@echo ""
	@echo "========================================="

research-clean:
	rm -rf $(RESEARCH_ARTIFACTS)

research-full: research-profile research-discover research-similarity research-report
	@echo ""
	@echo "✓ Full research cycle complete!"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Review discovered repositories in: $(SIMILARITY_SCORES)"
	@echo "  2. Analyze top matches manually"
	@echo "  3. Run 'make research-analyze' to analyze selected repositories (coming soon)"
	@echo ""

# Helper target to check research system dependencies
research-check-deps:
	@echo "Checking research system dependencies..."
	@python3 -c "import github" 2>/dev/null || (echo "ERROR: PyGithub not installed. Run: pip install PyGithub" && exit 1)
	@python3 -c "import yaml" 2>/dev/null || (echo "ERROR: PyYAML not installed. Run: pip install PyYAML" && exit 1)
	@echo "✓ All dependencies installed"
