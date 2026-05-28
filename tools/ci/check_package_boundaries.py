#!/usr/bin/env python3
"""Enforce modular-monolith boundary imports for apps/packages layout."""

from __future__ import annotations

import ast
from pathlib import Path

ROOTS = (Path("apps"), Path("packages"))

ALLOWED = {
    "apps": {"apps", "interfaces", "features", "core"},
    "interfaces": {"interfaces", "features", "core"},
    "features": {"features", "core"},
    "core": {"core"},
}


PUBLIC_FEATURE_MODULES = {"contracts"}

# Legacy namespaces that must not reappear after package migration waves.
FORBIDDEN_LEGACY_PREFIXES = (
    "semantic_context_server.shared.text_io",
    "semantic_context_server.shared.json_utils",
    "semantic_context_server.shared.hash_utils",
    "semantic_context_server.shared.resilience",
    "semantic_context_server.shared.execution",
    "semantic_context_server.shared.logging.context",
    "semantic_context_server.frameworks.discord",
    "semantic_context_server.app",
    "semantic_context_server.application.services.llm",
    "semantic_context_server.application.ports.llm",
    "semantic_context_server.infrastructure.adapters.llm",
    "semantic_context_server.infrastructure.adapters.benchmark",
    "semantic_context_server.application.services.benchmark_analysis",
    "semantic_context_server.application.services.benchmark_formatter",
    "semantic_context_server.domain.narrative.narrative_builder",
    "semantic_context_server.domain.narrative.session_summarizer",
    "semantic_context_server.infrastructure.storage.providers.campaign_storage_provider",
)


def py_module(path: Path) -> str:
    no_suffix = path.with_suffix("")
    parts = list(no_suffix.parts)
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def layer_for_module(mod: str) -> str | None:
    if mod.startswith("apps"):
        return "apps"
    if mod.startswith("packages.interfaces"):
        return "interfaces"
    if mod.startswith("packages.features"):
        return "features"
    if mod.startswith("packages.core"):
        return "core"
    return None


def resolve_relative(current_mod: str, level: int, module: str | None) -> str:
    parts = current_mod.split(".")
    if level > len(parts):
        return ""
    base = parts[:-level]
    if module:
        base.extend(module.split("."))
    return ".".join(base)


def imported_modules(path: Path, current_mod: str) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imports: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.level > 0:
                imports.add(resolve_relative(current_mod, node.level, node.module))
            elif node.module:
                imports.add(node.module)
    return {i for i in imports if i}


def feature_name(mod: str) -> str | None:
    parts = mod.split(".")
    if len(parts) >= 3 and parts[0] == "packages" and parts[1] == "features":
        return parts[2]
    return None


def is_forbidden_cross_feature_deep_import(src_mod: str, target_mod: str) -> bool:
    src_feature = feature_name(src_mod)
    dst_feature = feature_name(target_mod)
    if not src_feature or not dst_feature or src_feature == dst_feature:
        return False

    parts = target_mod.split(".")
    if len(parts) <= 3:
        return False

    if len(parts) == 4 and parts[3] in PUBLIC_FEATURE_MODULES:
        return False

    return True


def main() -> int:
    py_files: list[Path] = []
    for root in ROOTS:
        if root.exists():
            py_files.extend(p for p in root.rglob("*.py") if "__pycache__" not in p.parts)

    violations: list[str] = []
    for path in sorted(py_files):
        src_mod = py_module(path)
        src_layer = layer_for_module(src_mod)
        if src_layer is None:
            continue

        for target in imported_modules(path, src_mod):
            dst_layer = layer_for_module(target)
            if dst_layer is not None and dst_layer not in ALLOWED[src_layer]:
                violations.append(
                    f"{path}: forbidden import '{target}' ({src_layer} -> {dst_layer})"
                )
                continue

            if is_forbidden_cross_feature_deep_import(src_mod, target):
                violations.append(
                    f"{path}: forbidden deep cross-feature import '{target}'"
                )
                continue

            if any(target == prefix or target.startswith(f"{prefix}.") for prefix in FORBIDDEN_LEGACY_PREFIXES):
                violations.append(
                    f"{path}: forbidden legacy import '{target}'"
                )

    if violations:
        print("FAIL: package boundary violations detected:")
        for item in violations:
            print(f" - {item}")
        return 1

    print("Package boundary guard passed: no cross-layer violations detected.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
