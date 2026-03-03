.PHONY: help setup setup-full test lint hooks clean

help: ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

setup: ## Core setup (Collider venv + hooks + tools venv)
	@bash scripts/setup.sh

setup-full: ## Full setup (core + Wave AI tools with Doppler)
	@bash scripts/setup.sh --full

test: ## Run Collider tests
	cd particle && uv run pytest tests/ -q

lint: ## Run pre-commit on all files
	pre-commit run --all-files

hooks: ## Reinstall git hooks only
	@git config --unset core.hooksPath 2>/dev/null || true
	pre-commit install --hook-type commit-msg --hook-type pre-commit
	@mkdir -p .git/hooks
	@ln -sf ../../.agent/hooks/pre-push .git/hooks/pre-push && chmod +x .git/hooks/pre-push
	@ln -sf ../../.agent/hooks/post-commit .git/hooks/post-commit && chmod +x .git/hooks/post-commit
	@echo "Hooks installed."

clean: ## Remove .collider/ analysis artifacts
	rm -rf .collider/
	@echo "Cleaned .collider/ artifacts."
