# Enforcement Rules

This document describes the enforcement mechanisms for the IA documentation spec.

## Pre-commit Hook

All commits must pass structural validation of the `/docs/ia/` directory.
Changes to canonical files are checked for consistency across projects.

## Architecture Tests

Architecture tests (`tests/architecture/test_spec_compliance.py`) validate:
- Canonical paths use the correct `/docs/ia/CANONICAL/` prefix.
- No project-specific names appear in canonical files.
- Canonical files are identical across all registered projects.
- Each project has a `custom/` folder with `development/` and `reality/` subdirectories.

## CI/CD Gate

The CI pipeline runs the full architecture test suite on every pull request.
Failures block merging until all spec compliance checks pass.

## Manual Review

Pull requests that modify `/docs/ia/CANONICAL/` require at least one reviewer
familiar with the IA documentation spec before approval.
