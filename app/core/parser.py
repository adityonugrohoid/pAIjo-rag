"""JSON and Markdown file parsing for knowledge base documents."""

import json
from pathlib import Path


def parse_file(filepath: str) -> list[dict]:
    """Parse a knowledge file into a list of document dicts.

    Each dict has keys: text, title, source, category.

    Handles:
    - .json files (arrays and objects, English + Indonesian keys)
    - .md/.txt files (with optional YAML frontmatter stripping)
    """
    path = Path(filepath)
    docs = []

    if path.suffix == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        items = data if isinstance(data, list) else [data]
        for item in items:
            text = (
                item.get("text")
                or item.get("content")
                or item.get("isi")
                or str(item)
            )
            title = item.get("title") or item.get("judul") or path.stem
            source = item.get("source") or item.get("sumber") or path.name
            category = item.get("category") or item.get("kategori") or "general"
            docs.append(
                {"text": text, "title": title, "source": source, "category": category}
            )

    elif path.suffix in (".md", ".txt"):
        content = path.read_text(encoding="utf-8")
        content = _strip_frontmatter(content)
        docs.append(
            {
                "text": content,
                "title": path.stem,
                "source": path.name,
                "category": "general",
            }
        )

    return docs


def _strip_frontmatter(content: str) -> str:
    """Remove YAML frontmatter (between --- markers) from markdown content."""
    lines = content.split("\n")
    if lines and lines[0].strip() == "---":
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == "---":
                return "\n".join(lines[i + 1 :])
    return content
