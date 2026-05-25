import ast
from collections import defaultdict
from collections.abc import Iterable, Mapping
from pathlib import Path

import pytest

from tests.config.helpers.io import read_text_utf8

SRC = Path("src/semantic_context_server")


def _normalize(module: str) -> str:
    return module.split(":")[0].strip()


def _is_internal(module: str) -> bool:
    return module.startswith("semantic_context_server")


def _get_module_name(file: Path) -> str:
    return "semantic_context_server." + str(file.relative_to("src")).replace("/", ".").replace(
        ".py", ""
    )


@pytest.mark.architecture
def get_layer(module: str):
    if ".domain." in module:
        return "domain"
    if ".application." in module:
        return "application"
    if ".interfaces." in module:
        return "interfaces"
    if ".infrastructure." in module:
        return "infrastructure"

    return "unknown"


@pytest.mark.architecture
def get_import_graph() -> dict[str, set[str]]:
    graph = defaultdict(set)

    for file in SRC.rglob("*.py"):
        module = _get_module_name(file)

        tree = ast.parse(read_text_utf8(file))

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for n in node.names:
                    name = _normalize(n.name)
                    if _is_internal(name):
                        graph[module].add(name)

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    name = _normalize(node.module)
                    if _is_internal(name):
                        graph[module].add(name)

    return graph


@pytest.mark.architecture
def find_cycles(graph: Mapping[str, Iterable[str]]) -> list[list[str]]:
    visited: set[str] = set()
    stack: list[str] = []

    cycles: list[list[str]] = []

    def visit(node: str) -> None:
        if node in stack:
            idx = stack.index(node)
            cycles.append(stack[idx:] + [node])
            return

        if node in visited:
            return

        visited.add(node)
        stack.append(node)

        for neighbor in graph.get(node, []):
            visit(neighbor)

        stack.pop()

    for node in list(graph.keys()):
        visit(node)

    return cycles


@pytest.mark.architecture
def test_no_cycles():
    graph = get_import_graph()

    cycles = find_cycles(graph)

    assert not cycles, "\n\n".join(" -> ".join(cycle) for cycle in cycles)


@pytest.mark.architecture
def test_no_cross_layer_cycles():
    graph = get_import_graph()
    cycles = find_cycles(graph)

    errors = []

    for cycle in cycles:
        layers = {get_layer(m) for m in cycle}

        if len(layers) > 1:
            errors.append(f"Cross-layer cycle: {cycle}")

    assert not errors, "\n".join(errors)
