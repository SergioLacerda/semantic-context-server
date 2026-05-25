# Enforcement Rules

## Pre-commit Hook
All local commits must run repository hooks that block formatting, lint, or governance violations before a commit is created.

## Architecture Tests
Architecture test suites must run in CI and locally to detect layer leaks, contract drift, and forbidden dependency direction.

## CI/CD Gate
Pull request and protected-branch pipelines must fail on governance, quality, architecture, or contract violations.

## Manual Review
Reviewers must verify that structural changes keep canonical specifications and project customizations aligned with governance rules.
