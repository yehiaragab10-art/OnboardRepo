"""Manual test runner for the Python chunker
"""

from __future__ import annotations

import sys
from pathlib import Path

from onboardrepo.indexer.chunker_code import CodeChunk, parse_python_file

SAMPLES = Path(__file__).resolve().parent.parent / "tests" / "samples"


def print_chunks(path: str, chunks: list[CodeChunk]) -> None:
    """Step 3 — print results in a readable way."""
    print(f"\n=== {path} -> {len(chunks)} chunk(s) ===")
    for c in chunks:
        print(f"  [{c.symbol_kind:8}] {c.symbol_name:20} lines {c.start_line}-{c.end_line}")


def basic_assertions(chunks: list[CodeChunk]) -> None:
    """Step 5 — invariants that must hold for every chunk."""
    for c in chunks:
        assert c.start_line > 0, f"start_line not positive: {c}"
        assert c.start_line <= c.end_line, f"start_line > end_line: {c}"
        assert c.chunk_type == "code", f"unexpected chunk_type: {c}"


def count_kinds(chunks: list[CodeChunk]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for c in chunks:
        counts[c.symbol_kind] = counts.get(c.symbol_kind, 0) + 1
    return counts


def debug_dump(path: str) -> None:
    """Step 6 — dump raw tree-sitter nodes to inspect AST traversal."""
    from tree_sitter import Parser
    from tree_sitter_languages import get_language

    source = Path(path).read_text(encoding="utf-8")
    parser = Parser()
    parser.set_language(get_language("python"))
    root = parser.parse(bytes(source, "utf-8")).root_node

    print(f"\n--- DEBUG AST for {path} ---")

    def walk(node: object, depth: int = 0) -> None:
        sp = node.start_point  # type: ignore[attr-defined]
        ep = node.end_point  # type: ignore[attr-defined]
        print(f"{'  ' * depth}{node.type} {sp}-{ep}")  # type: ignore[attr-defined]
        for child in node.children:  # type: ignore[attr-defined]
            walk(child, depth + 1)

    walk(root)


def run_controlled_cases() -> None:
    # Case A — single function
    a = parse_python_file(str(SAMPLES / "sample_a.py"))
    print_chunks("sample_a.py", a)
    basic_assertions(a)
    assert len(a) == 1, f"expected 1 chunk, got {len(a)}"
    assert a[0].symbol_kind == "function"
    print("  PASS: single function -> 1 function chunk")

    # Case B — class with 3 methods
    b = parse_python_file(str(SAMPLES / "sample_b.py"))
    print_chunks("sample_b.py", b)
    basic_assertions(b)
    kinds = count_kinds(b)
    assert len(b) == 4, f"expected 4 chunks, got {len(b)}"
    assert kinds.get("class") == 1, kinds
    assert kinds.get("method") == 3, kinds
    print("  PASS: class + 3 methods -> 1 class + 3 methods")

    # Case C — empty file
    c = parse_python_file(str(SAMPLES / "sample_c.py"))
    print_chunks("sample_c.py", c)
    assert c == [], f"expected [], got {c}"
    print("  PASS: empty file -> []")

    # Case D — nested class
    d = parse_python_file(str(SAMPLES / "sample_d.py"))
    print_chunks("sample_d.py", d)
    basic_assertions(d)
    names = {(x.symbol_kind, x.symbol_name) for x in d}
    assert ("class", "A") in names, names
    assert ("class", "A.B") in names, names
    assert ("method", "A.B.m") in names, names
    print("  PASS: nested class -> dotted symbol names")

    print("\nALL CONTROLLED CASES PASSED")


def main() -> None:
    args = sys.argv[1:]
    debug = "--debug" in args
    real_files = [a for a in args if a != "--debug"]

    if real_files:
        # Step 7 — run on a real file: no crash, reasonable chunk count
        for path in real_files:
            chunks = parse_python_file(path)
            print_chunks(path, chunks)
            basic_assertions(chunks)
            if debug:
                debug_dump(path)
        return

    run_controlled_cases()
    if debug:
        for name in ("sample_a.py", "sample_b.py", "sample_d.py"):
            debug_dump(str(SAMPLES / name))


if __name__ == "__main__":
    main()