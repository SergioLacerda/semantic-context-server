# tests/architecture/utils.py

import ast
from pathlib import Path

from tests.config.helpers.io import read_text_utf8


def extract_imports(file_path: Path):
    tree = ast.parse(read_text_utf8(file_path))
    imports = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                imports.append(n.name)

        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)

    return imports
