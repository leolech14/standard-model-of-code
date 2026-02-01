# Atom Research Tooling Makefile
# Usage: make <target>

PYTHON ?= python3
PATTERNS_DIR ?= ../../src/patterns
ANALYSIS_FILE ?= ../../.collider/unified_analysis.json
ARTIFACTS_DIR ?= ../../artifacts/atom-research
CORPUS_FILE ?= $(ARTIFACTS_DIR)/corpus_pilot.yaml

.PHONY: all inventory coverage quality check self-analysis pilot summarize t2-samples help

help:
	@echo "Atom Research Tooling"
	@echo ""
	@echo "Targets:"
	@echo "  inventory      Run atom inventory analysis"
	@echo "  coverage       Run coverage analysis on latest Collider output"
	@echo "  quality        Run quality checks (duplicates, overlaps)"
	@echo "  check          Run CI checks (fails on issues)"
	@echo "  self-analysis  Full self-analysis pipeline"
	@echo "  pilot          Run pilot corpus (10 repos)"
	@echo "  summarize      Summarize latest corpus run"
	@echo "  t2-samples     Extract T2 samples for labeling"
	@echo ""
	@echo "Variables:"
	@echo "  PATTERNS_DIR   Path to patterns (default: ../../src/patterns)"
	@echo "  ANALYSIS_FILE  Path to unified_analysis.json"
	@echo "  ARTIFACTS_DIR  Output directory for artifacts"
	@echo "  CORPUS_FILE    Corpus manifest (default: corpus_pilot.yaml)"

# Full inventory analysis
inventory:
	$(PYTHON) atom_inventory.py --patterns-dir $(PATTERNS_DIR) --output $(ARTIFACTS_DIR)/inventory.json

# Coverage analysis from existing Collider output
coverage:
	@if [ -f "$(ANALYSIS_FILE)" ]; then \
		$(PYTHON) atom_coverage.py $(ANALYSIS_FILE) --output $(ARTIFACTS_DIR)/coverage.json; \
	else \
		echo "Error: Analysis file not found. Run './collider full . --output .collider' first."; \
		exit 1; \
	fi

# Quality checks (informational)
quality:
	$(PYTHON) atom_inventory.py --patterns-dir $(PATTERNS_DIR)
	@echo ""
	@if [ -f "$(ANALYSIS_FILE)" ]; then \
		$(PYTHON) atom_coverage.py $(ANALYSIS_FILE); \
	fi

# CI checks (fails on issues)
check:
	$(PYTHON) atom_inventory.py --patterns-dir $(PATTERNS_DIR) --check-duplicates --quiet
	@echo "[PASS] No duplicate atom IDs"
	@if [ -f "$(ANALYSIS_FILE)" ]; then \
		$(PYTHON) atom_coverage.py $(ANALYSIS_FILE) --check-unknown 15 --quiet; \
		echo "[PASS] Unknown rate within threshold"; \
	fi

# Full self-analysis: run Collider then analyze
self-analysis:
	@echo "Running Collider self-analysis..."
	cd ../.. && ./collider full . --output .collider
	@echo ""
	@echo "Running research analysis..."
	@mkdir -p $(ARTIFACTS_DIR)
	$(PYTHON) atom_inventory.py --patterns-dir $(PATTERNS_DIR) --output $(ARTIFACTS_DIR)/inventory.json
	$(PYTHON) atom_coverage.py $(ANALYSIS_FILE) --output $(ARTIFACTS_DIR)/coverage.json
	@echo ""
	@echo "Artifacts saved to $(ARTIFACTS_DIR)/"

# Run pilot corpus (10 repos)
pilot:
	@if [ -f "$(CORPUS_FILE)" ]; then \
		$(PYTHON) run_corpus.py $(CORPUS_FILE) --output $(ARTIFACTS_DIR); \
	else \
		echo "Error: Corpus file not found: $(CORPUS_FILE)"; \
		exit 1; \
	fi

# Summarize latest corpus run
summarize:
	@LATEST=$$(ls -td $(ARTIFACTS_DIR)/20*/ 2>/dev/null | head -1); \
	if [ -n "$$LATEST" ]; then \
		$(PYTHON) summarize_corpus.py "$$LATEST"; \
	else \
		echo "Error: No corpus runs found in $(ARTIFACTS_DIR)"; \
		exit 1; \
	fi

# Extract T2 samples for precision labeling
t2-samples:
	@if [ -f "$(ANALYSIS_FILE)" ]; then \
		$(PYTHON) atom_coverage.py $(ANALYSIS_FILE) --extract-t2-samples 200 --output $(ARTIFACTS_DIR)/t2_samples.csv; \
	else \
		echo "Error: Analysis file not found. Run './collider full . --output .collider' first."; \
		exit 1; \
	fi

# Default: show help
all: help
