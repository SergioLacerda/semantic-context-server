#!/usr/bin/env python3
"""Detect import cycles in semantic_context_server package."""

from __future__ import annotations

import ast
from pathlib import Path

SRC_ROOT = Path("src/semantic_context_server")
PKG_PREFIX = "semantic_context_server"


def module_name(path: Path) -> str:
    rel = path.relative_to(SRC_ROOT.parent).with_suffix("")
    parts = list(rel.parts)
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def resolve_relative(current: str, level: int, module: str | None) -> str:
    parts = current.split(".")
    if level > len(parts):
        return ""
    base = parts[:-level]
    if module:
        base.extend(module.split("."))
    return ".".join(base)


def collect_import_edges(path: Path, current_mod: str) -> set[str]:
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    edges: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                target = alias.name
                if target.startswith(PKG_PREFIX):
                    edges.add(target)
        elif isinstance(node, ast.ImportFrom):
            if node.level > 0:
                target = resolve_relative(current_mod, node.level, node.module)
            else:
                target = node.module or ""
            if target.startswith(PKG_PREFIX):
                edges.add(target)
    return edges


def normalize_target(target: str, known_modules: set[str]) -> str | None:
    if target in known_modules:
        return target

    probe = target
    while "." in probe:
        probe = probe.rsplit(".", 1)[0]
        if probe in known_modules:
            return probe

    init_mod = f"{target}.__init__"
    if init_mod in known_modules:
        return init_mod
    return None


def find_cycles(graph: dict[str, set[str]]) -> list[list[str]]:
    visited: set[str] = set()
    stack: list[str] = []
    in_stack: set[str] = set()
    cycles: set[tuple[str, ...]] = set()

    def dfs(node: str) -> None:
        visited.add(node)
        stack.append(node)
        in_stack.add(node)

        for nxt in graph.get(node, set()):
            if nxt not in visited:
                dfs(nxt)
            elif nxt in in_stack:
                idx = stack.index(nxt)
                cycle = stack[idx:] + [nxt]
                # canonicalize to reduce duplicates
                core = cycle[:-1]
                rotations = [tuple(core[i:] + core[:i]) for i in range(len(core))]
                canonical = min(rotations)
                cycles.add(canonical)

        stack.pop()
        in_stack.remove(node)

    for node in sorted(graph):
        if node not in visited:
            dfs(node)

    return [list(cycle) for cycle in sorted(cycles)]


def main() -> int:
    files = [p for p in SRC_ROOT.rglob("*.py") if "__pycache__" not in p.parts]
    modules = {module_name(path): path for path in files}
    known = set(modules)

    graph: dict[str, set[str]] = {mod: set() for mod in known}
    for mod, path in modules.items():
        for raw_target in collect_import_edges(path, mod):
            target = normalize_target(raw_target, known)
            if target and target != mod:
                graph[mod].add(target)

    cycles = find_cycles(graph)
    if cycles:
        print("FAIL: import cycle(s) detected:")
        for cycle in cycles:
            print(" - " + " -> ".join(cycle + [cycle[0]]))
        return 1

    print("Import cycle guard passed: no cycles detected.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
