.DEFAULT_GOAL := help

.PHONY: help install sync sync-ci sync-full run \
        lint lint-fix fmt type \
        test test-fast arch contract \
        ci ci-local validate \
        lock lock-check clean hooks hooks-install

help:
	@echo "Usage: make <target>"
	@echo ""
	@echo "Setup"
	@echo "  install     Install deps + install git hooks (onboarding)"
	@echo "  sync        Alias for install"
	@echo "  sync-ci     Install ci dependencies (frozen)"
	@echo "  sync-full   Install all optional extras"
	@echo ""
	@echo "Run"
	@echo "  run         Start the uvicorn server"
	@echo ""
	@echo "Quality"
	@echo "  lint        Unified gate + anti-hack guardrails (suppression+text-io policy)"
	@echo "  lint-fix    Auto-fix style and re-run full lint gate"
	@echo "  fmt         Alias for lint-fix"
	@echo "  type        Run mypy type checks only"
	@echo ""
	@echo "Tests"
	@echo "  test        Run all tests with coverage"
	@echo "  test-fast   Run fast tests only (not slow, not integration)"
	@echo "  arch        Run architecture validation tests"
	@echo "  contract    Run contract tests"
	@echo ""
	@echo "CI/CD"
	@echo "  ci          Run full local CI pipeline (same as ci-local)"
	@echo "  ci-local    Run full local CI pipeline"
	@echo "  validate    Run lock-check + lint + type (fast pre-push check)"
	@echo ""
	@echo "Lock"
	@echo "  lock        Regenerate uv.lock"
	@echo "  lock-check  Assert uv.lock is up to date"
	@echo ""
	@echo "Misc"
	@echo "  hooks        Alias for hooks-install"
	@echo "  hooks-install Install local git hooks from tools/git-hooks"
	@echo "  clean       Remove build and cache artifacts"

# ─── Setup ──────────────────────────────────────────────────────────────────

install:
	uv sync --extra dev --extra test
	@$(MAKE) hooks-install

sync: install

sync-ci:
	uv sync --extra ci --frozen

sync-full:
	uv sync --extra full --extra dev --extra test

# ─── Run ────────────────────────────────────────────────────────────────────

run:
	uv run uvicorn semantic_context_server.app:app --host 0.0.0.0 --port 8000

# ─── Quality ────────────────────────────────────────────────────────────────

lint:
	uv run python tools/quality/lint_runner.py check

lint-fix:
	uv run python tools/quality/lint_runner.py fix

fmt: lint-fix

type:
	uv run mypy src

# ─── Tests ──────────────────────────────────────────────────────────────────

test:
	uv run pytest --cov=src/semantic_context_server --cov-report=xml --cov-report=term-missing --cov-report=html

test-fast:
	uv run pytest -m "not slow and not integration"

arch:
	uv run pytest -m architecture

contract:
	uv run pytest -m contract

# ─── CI/CD pipeline ─────────────────────────────────────────────────────────

# Mirrors CI stages: preflight → quality → architecture → tests
ci-local: lock-check lint type arch contract test

ci: ci-local

# Fast pre-push gate (no tests): lock + lint + types
validate: lock-check lint type

# ─── Lock ───────────────────────────────────────────────────────────────────

lock:
	uv lock

lock-check:
	uv lock --check

# ─── Misc ───────────────────────────────────────────────────────────────────

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	rm -rf build/ 2>/dev/null || true
	# legacy cache dirs (now centralised under build/)
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true

hooks: hooks-install

hooks-install:
	bash tools/bootstrap/install-git-hooks.sh
