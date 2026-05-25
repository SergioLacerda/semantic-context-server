"""
Pytest fixtures for SPEC compliance validation.

These tests enforce SPEC governance rules and prevent violations
of immutable architecture layers.
"""

import re
from pathlib import Path

import pytest

from tests.config.helpers.io import read_text_utf8


class SpecComplianceValidator:
    """Validator for SPEC framework compliance rules."""

    PROJECT_ROOT = Path(__file__).parent.parent.parent
    DOCS_IA = PROJECT_ROOT / "docs" / "ia"

    @classmethod
    def get_all_files(cls, directory: Path) -> list[Path]:
        """Get all markdown and Python files in directory."""
        return list(directory.rglob("*.md")) + list(directory.rglob("*.py"))

    @classmethod
    def read_file(cls, path: Path) -> str:
        """Read file content safely."""
        try:
            return read_text_utf8(path)
        except Exception as e:
            raise RuntimeError(f"Failed to read {path}: {e}") from e

    @classmethod
    def validate_canonical_paths(cls) -> list[str]:
        """Rule 1: CANONICAL/ must use correct paths."""
        errors = []
        canonical_dir = cls.DOCS_IA / "CANONICAL"

        if not canonical_dir.exists():
            return errors

        invalid_patterns = [
            (r"/docs/specs", "Should be /docs/ia/CANONICAL/specifications"),
            (r"/runtime/", "Should be /docs/ia/custom/[PROJECT]/development/"),
            (r"docs/runtime", "Should be /docs/ia/custom/[PROJECT]/development/"),
            (r"/REALITY/", "Should be /docs/ia/custom/[PROJECT]/reality/"),
            (r"/DEVELOPMENT/", "Should be /docs/ia/custom/[PROJECT]/development/"),
            (r"^specs/", "Should be /docs/ia/CANONICAL/specifications/"),
            (r"^runtime/", "Should be /docs/ia/custom/[PROJECT]/development/"),
        ]

        for file in cls.get_all_files(canonical_dir):
            if file.name in [".gitkeep", "README.md"]:
                continue

            content = cls.read_file(file)

            for pattern, suggestion in invalid_patterns:
                matches = re.finditer(pattern, content)
                for match in matches:
                    line_no = content[: match.start()].count("\n") + 1
                    errors.append(
                        f"{file.relative_to(cls.PROJECT_ROOT)}:{line_no} - "
                        f"Invalid path '{match.group()}' → {suggestion}"
                    )

        return errors

    @classmethod
    def validate_no_project_names_in_canonical(cls) -> list[str]:
        """Rule 2: No project-specific names in CANONICAL/."""
        errors = []
        canonical_dir = cls.DOCS_IA / "CANONICAL"

        if not canonical_dir.exists():
            return errors

        project_patterns = [
            (r"semantic-context-server", "Use [PROJECT_NAME] placeholder"),
            (r"semantic_context_server", "Use [PROJECT_NAME] placeholder"),
            (r"game-master-api", "Use [PROJECT_NAME] placeholder"),
            (r"game_master_api", "Use [PROJECT_NAME] placeholder"),
        ]

        for file in cls.get_all_files(canonical_dir):
            if file.name in [".gitkeep"]:
                continue

            content = cls.read_file(file)

            for pattern, suggestion in project_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    line_no = content[: match.start()].count("\n") + 1
                    errors.append(
                        f"{file.relative_to(cls.PROJECT_ROOT)}:{line_no} - "
                        f"Project name '{match.group()}' found → {suggestion}"
                    )

        return errors

    @classmethod
    def validate_canonical_identical_across_projects(cls) -> list[str]:
        """Rule 3: CANONICAL/ must be identical across all projects."""
        errors = []
        canonical_source = cls.DOCS_IA / "CANONICAL"
        custom_dir = cls.DOCS_IA / "custom"

        if not canonical_source.exists() or not custom_dir.exists():
            return errors

        # Check each project's CANONICAL
        for project_dir in custom_dir.iterdir():
            if project_dir.name == "_TEMPLATE":
                continue

            project_canonical = project_dir / "CANONICAL"
            if not project_canonical.exists():
                # OK - not all projects need their own copy
                continue

            # If it exists, must match source
            source_files = set(
                f.relative_to(canonical_source) for f in canonical_source.rglob("*") if f.is_file()
            )
            project_files = set(
                f.relative_to(project_canonical)
                for f in project_canonical.rglob("*")
                if f.is_file()
            )

            if source_files != project_files:
                missing = source_files - project_files
                extra = project_files - source_files
                if missing:
                    errors.append(f"{project_dir.name}: Missing files: {missing}")
                if extra:
                    errors.append(f"{project_dir.name}: Extra files: {extra}")

        return errors

    @classmethod
    def validate_custom_folders_exist(cls) -> list[str]:
        """Rule 4: Each project should have custom/ folder."""
        errors = []
        custom_dir = cls.DOCS_IA / "custom"

        if not custom_dir.exists():
            errors.append("Missing /docs/ia/custom/ directory")
            return errors

        required_projects = ["semantic-context-server"]
        for project in required_projects:
            project_dir = custom_dir / project
            if not project_dir.exists():
                errors.append(f"Missing /docs/ia/custom/{project}/ directory")

            # Check required structure
            for required_subdir in ["development", "reality"]:
                subdir = project_dir / required_subdir
                if not subdir.exists():
                    errors.append(f"Missing /docs/ia/custom/{project}/{required_subdir}/ structure")

        return errors

    @classmethod
    def validate_enforcement_rules_documented(cls) -> list[str]:
        """Rule 5: Enforcement rules must be documented."""
        errors = []
        enforcement_file = cls.DOCS_IA / "CANONICAL" / "rules" / "ENFORCEMENT_RULES.md"

        if not enforcement_file.exists():
            errors.append("Missing /docs/ia/CANONICAL/rules/ENFORCEMENT_RULES.md")
            return errors

        content = cls.read_file(enforcement_file)

        required_sections = [
            "Pre-commit Hook",
            "Architecture Tests",
            "CI/CD Gate",
            "Manual Review",
        ]

        for section in required_sections:
            if section not in content:
                errors.append(f"ENFORCEMENT_RULES.md missing section: '{section}'")

        return errors

    @classmethod
    def run_all_validations(cls) -> dict:
        """Run all validation rules and return results."""
        validations = {
            "canonical_paths": cls.validate_canonical_paths(),
            "no_project_names": cls.validate_no_project_names_in_canonical(),
            "canonical_identical": cls.validate_canonical_identical_across_projects(),
            "custom_structure": cls.validate_custom_folders_exist(),
            "enforcement_documented": cls.validate_enforcement_rules_documented(),
        }
        return validations


# Pytest fixtures


@pytest.fixture
def spec_validator():
    """Provide SPEC validator instance."""
    return SpecComplianceValidator()


def test_canonical_paths_valid(spec_validator):
    """Rule 1: CANONICAL/ must use correct paths."""
    errors = spec_validator.validate_canonical_paths()
    assert not errors, "Invalid paths found in CANONICAL/:\n" + "\n".join(errors)


def test_no_project_names_in_canonical(spec_validator):
    """Rule 2: No project-specific names in CANONICAL/."""
    errors = spec_validator.validate_no_project_names_in_canonical()
    assert not errors, "Project names found in CANONICAL/:\n" + "\n".join(errors)


def test_canonical_identical_across_projects(spec_validator):
    """Rule 3: CANONICAL/ must be identical across projects."""
    errors = spec_validator.validate_canonical_identical_across_projects()
    assert not errors, "CANONICAL/ inconsistencies found:\n" + "\n".join(errors)


def test_custom_folders_structure(spec_validator):
    """Rule 4: custom/ folders must have proper structure."""
    errors = spec_validator.validate_custom_folders_exist()
    assert not errors, "custom/ structure issues:\n" + "\n".join(errors)


def test_enforcement_rules_documented(spec_validator):
    """Rule 5: Enforcement rules must be documented."""
    errors = spec_validator.validate_enforcement_rules_documented()
    assert not errors, "Enforcement rules issues:\n" + "\n".join(errors)


def test_spec_compliance_summary(spec_validator):
    """Summary test showing all compliance results."""
    results = spec_validator.run_all_validations()

    total_errors = sum(len(errors) for errors in results.values())

    if total_errors > 0:
        summary = "SPEC Compliance Issues:\n"
        for rule, errors in results.items():
            if errors:
                summary += f"\n{rule}:\n"
                for error in errors:
                    summary += f"  - {error}\n"
        raise AssertionError(summary)
    else:
        print("✅ All SPEC compliance rules passed!")
