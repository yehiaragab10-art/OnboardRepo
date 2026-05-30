"""Python AST chunker (T-005).

Given a Python source file, produce a list of :class:`CodeChunk` objects: one
per top-level function, one per class, and one per method (including methods of
nested classes). Decorated and async definitions are handled. Docstring /
leading-comment handling is intentionally out of scope here (added in T-006).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from tree_sitter import Node, Parser
from tree_sitter_languages import get_language

logger = logging.getLogger(__name__)

# tree-sitter node types we treat as functions/classes. `async def` parses as
# `function_definition` in current grammars; `async_function_definition` is
# included defensively for grammar versions that emit it.
_FUNCTION_TYPES = ("function_definition", "async_function_definition")
_CLASS_TYPES = ("class_definition",)
_DEFINITION_TYPES = (*_FUNCTION_TYPES, *_CLASS_TYPES)


@dataclass
class CodeChunk:
    """A chunk of code extracted from a file."""

    file_path: str  # Absolute or repo-relative path to the file.
    start_line: int  # 1-indexed, inclusive.
    end_line: int  # 1-indexed, inclusive.
    chunk_type: str  # Always "code" for this chunker.
    language: str  #"python", "c++", etc.
    symbol_name: str  # Fully qualified if nested ex: "MyClass.my_method".
    symbol_kind: str  # "function", "class", or "method".
    source_text: str  # Raw source lines for this chunk.
    has_docstring: bool  # Whether the symbol has a docstring (set in T-006).
    summary: str | None = None  # LLM-generated summary (set in T-014).
    embedding_model: str | None = None  # Embedding model name (set later).


def _get_node_name(node: Node) -> str:
    """Return the identifier text of a class/function node, or "unknown"."""
    for child in node.children:
        if child.type == "identifier" and child.text is not None:
            return child.text.decode("utf-8", errors="ignore")
    return "unknown"


def _extract_source(lines: list[str], start_line: int, end_line: int) -> str:
    """Join the 1-indexed inclusive line range [start_line, end_line]."""
    return "\n".join(lines[start_line - 1 : end_line])


def _get_body_block(node: Node) -> Node | None:
    """Return the `block` child of a class/function node, if present.

    In tree-sitter's Python grammar the members of a class live inside a
    `block` node, not as direct children of the `class_definition`.
    """
    for child in node.children:
        if child.type == "block":
            return child
    return None


def _inner_definition(node: Node) -> Node:
    """Unwrap a `decorated_definition` to its function/class node."""
    if node.type == "decorated_definition":
        for child in node.children:
            if child.type in _DEFINITION_TYPES:
                return child
    return node


def _build_chunk(
    range_node: Node,
    lines: list[str],
    file_path: str,
    language: str,
    symbol_name: str,
    symbol_kind: str,
) -> CodeChunk:
    """Build a single CodeChunk spanning ``range_node`` (decorators included)."""
    start_line = range_node.start_point[0] + 1
    end_line = range_node.end_point[0] + 1
    return CodeChunk(
        file_path=file_path,
        start_line=start_line,
        end_line=end_line,
        chunk_type="code",
        language=language,
        symbol_name=symbol_name,
        symbol_kind=symbol_kind,
        source_text=_extract_source(lines, start_line, end_line),
        has_docstring=False,  # Docstring detection is added in T-006.
    )


def _walk_members(
    parent: Node,
    qualifier: str,
    func_kind: str,
    lines: list[str],
    file_path: str,
    language: str,
    chunks: list[CodeChunk],
) -> None:
    """Emit chunks for every definition directly inside ``parent``.

    ``parent`` is the module root (top level) or a class `block`. ``qualifier``
    is "" at the top level or "Outer." inside a class, and ``func_kind`` is
    "function" at the top level or "method" inside a class. Recurses into
    nested classes. Decorated and async definitions are unwrapped first so the
    chunk's line range still includes the decorator lines.
    """
    for child in parent.children:
        definition = _inner_definition(child)

        if definition.type in _FUNCTION_TYPES:
            name = _get_node_name(definition)
            chunks.append(
                _build_chunk(child, lines, file_path, language, f"{qualifier}{name}", func_kind)
            )
        elif definition.type in _CLASS_TYPES:
            name = _get_node_name(definition)
            full_name = f"{qualifier}{name}"
            chunks.append(_build_chunk(child, lines, file_path, language, full_name, "class"))
            block = _get_body_block(definition)
            if block is not None:
                _walk_members(
                    block, f"{full_name}.", "method", lines, file_path, language, chunks
                )


def parse_python_file(file_path: str) -> list[CodeChunk]:
    """Parse a Python file and extract code chunks.
    Returns an empty list (never raises) on read failures, empty files, or
    files tree-sitter reports as containing syntax errors.
    """
    try:
        with open(file_path, encoding="utf-8") as f:
            source = f.read()
    except (OSError, UnicodeDecodeError) as e:
        logger.warning("Failed to read file %s: %s", file_path, e)
        return []

    if not source.strip():
        logger.warning("File %s is empty, skipping.", file_path)
        return []

    lines = source.splitlines()
    try:
        language = get_language("python")
        parser = Parser()
        parser.set_language(language)
        tree = parser.parse(bytes(source, "utf-8"))
        root = tree.root_node
    except Exception as e:
        logger.warning("Tree-sitter parse failed for file %s: %s", file_path, e)
        return []

    if root.has_error:
        logger.warning("Syntax errors detected in file %s, skipping.", file_path)
        return []

    chunks: list[CodeChunk] = []
    _walk_members(root, "", "function", lines, file_path, "python", chunks)
    return chunks