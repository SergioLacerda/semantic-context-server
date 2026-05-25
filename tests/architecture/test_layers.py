# tests/architecture/test_layers.py
from pathlib import Path

import pytest

from tests.config.helpers.io import read_text_utf8

from .rules import RULES
from .utils import extract_imports

SRC = Path("src/semantic_context_server")


@pytest.mark.architecture
def get_layer(file: Path) -> str:
    path = str(file)

    if "/domain/" in path:
        return "domain"
    if "/application/" in path:
        return "application"
    if "/interfaces/" in path:
        return "interfaces"
    if "/infrastructure/" in path:
        return "infrastructure"
    if "/shared/" in path:
        return "shared"

    return "unknown"


SRC = Path("src/semantic_context_server")


@pytest.mark.architecture
def test_layer_dependencies():
    errors = []

    for file in SRC.rglob("*.py"):
        layer = get_layer(file)

        if layer == "unknown":
            continue

        imports = extract_imports(file)

        for imp in imports:
            for forbidden in RULES[layer].get("forbidden", []):
                if f"semantic_context_server.{forbidden}" in imp:
                    allowed = RULES[layer].get("allowed", [])

                    if any(imp.startswith(a) for a in allowed):
                        continue

                    errors.append(f"{file} → {layer} cannot depend on {forbidden} ({imp})")

    assert not errors, "\n".join(errors)


@pytest.mark.architecture
def test_no_cross_layer_leak():
    errors = []

    for file in SRC.rglob("*.py"):
        content = read_text_utf8(file)

        if "infrastructure" in content and "domain" in str(file):
            errors.append(f"{file} leaking infra")

    assert not errors, "\n".join(errors)
