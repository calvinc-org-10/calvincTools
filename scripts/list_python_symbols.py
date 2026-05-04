"""Print a class/function outline for a Python source file."""

from __future__ import annotations

import ast
import sys
from pathlib import Path


class SymbolPrinter:
    """Pretty-printer for Python class/function symbols."""

    def __init__(self) -> None:
        self._seen_any = False

    def print_module(self, tree: ast.Module) -> None:
        for node in tree.body:
            if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                self._print_node(node, indent=0)

        if not self._seen_any:
            print("No classes or functions found.")

    def _print_node(self, node: ast.AST, indent: int) -> None:
        prefix = "  " * indent

        if isinstance(node, ast.ClassDef):
            self._seen_any = True
            print(f"{prefix}class {node.name} (line {node.lineno})")
            for child in node.body:
                if isinstance(child, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                    self._print_node(child, indent + 1)
            return

        if isinstance(node, ast.AsyncFunctionDef):
            self._seen_any = True
            print(f"{prefix}async def {node.name} (line {node.lineno})")
            self._print_nested_defs(node, indent + 1)
            return

        if isinstance(node, ast.FunctionDef):
            self._seen_any = True
            print(f"{prefix}def {node.name} (line {node.lineno})")
            self._print_nested_defs(node, indent + 1)

    def _print_nested_defs(self, node: ast.AST, indent: int) -> None:
        body = getattr(node, "body", None)
        if not isinstance(body, list):
            return

        for child in body:
            if isinstance(child, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                self._print_node(child, indent)


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python scripts/list_python_symbols.py <python_file>")
        return 1

    target = Path(sys.argv[1])
    if not target.exists() or not target.is_file():
        print(f"File not found: {target}")
        return 1

    try:
        source = target.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(target))
    except SyntaxError as exc:
        print(f"Syntax error in {target}: {exc}")
        return 1
    except UnicodeDecodeError:
        print(f"Could not decode {target} as UTF-8.")
        return 1

    SymbolPrinter().print_module(tree)
    return 0

from calvincTools.utils import pretty_show_fns
def cPretty():
    if len(sys.argv) != 2:
        print("Usage: python scripts/list_python_symbols.py <python_file>")
        return 1

    target = Path(sys.argv[1])
    if not target.exists() or not target.is_file():
        print(f"File not found: {target}")
        return 1

    print(target)
    print(f"Symbols in {target}:")
    print(pretty_show_fns(str(target)))
    return 0
        
if __name__ == "__main__":
    raise SystemExit(main())
    # raise SystemExit(cPretty())
