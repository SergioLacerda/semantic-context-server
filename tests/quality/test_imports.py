import ast
from pathlib import Path

from tests.config.helpers.io import read_text_utf8

SRC_PATH = Path("src")


def get_imports(file_path):
    tree = ast.parse(read_text_utf8(file_path))
    imports = set()

    for node in ast.walk(tree):
        # import x
        if isinstance(node, ast.Import):
            for n in node.names:
                alias = n.asname or n.name.split(".")[0]
                imports.add(alias)

        # from x import y
        elif isinstance(node, ast.ImportFrom):
            if node.module == "__future__":
                continue
            for n in node.names:
                if n.name == "*":
                    continue
                alias = n.asname or n.name
                imports.add(alias)

    return imports


def get_used_names(file_path):
    tree = ast.parse(read_text_utf8(file_path))
    names = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            names.add(node.id)

    return names


def get_reexported_names(file_path):
    tree = ast.parse(read_text_utf8(file_path))
    exported = set()

    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if (
                isinstance(target, ast.Name)
                and target.id == "__all__"
                and isinstance(node.value, (ast.List, ast.Tuple))
            ):
                for el in node.value.elts:
                    if isinstance(el, ast.Constant) and isinstance(el.value, str):
                        exported.add(el.value)

    return exported


def test_no_unused_imports():
    errors = []

    for file in SRC_PATH.rglob("*.py"):
        if "__init__" in file.name:
            continue

        imports = get_imports(file)
        used = get_used_names(file)
        used |= get_reexported_names(file)

        unused = imports - used

        if unused:
            errors.append(f"{file}: unused imports → {unused}")

    assert not errors, "\n".join(errors)
