"""Read/write markdown files with YAML frontmatter as the persistence layer.

Each entity (task, project, ...) is a single .md file: a YAML frontmatter
block followed by free-form markdown body. This module is the only place
that touches the filesystem directly so the Vault stays the single source
of truth (synced separately by Syncthing).
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n?(.*)$", re.DOTALL)


def slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9а-яё]+", "-", text)
    return text.strip("-") or "untitled"


def read_entity(path: Path) -> dict[str, Any]:
    raw = path.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(raw)
    if not match:
        return {"frontmatter": {}, "body": raw, "path": path}
    frontmatter = yaml.safe_load(match.group(1)) or {}
    body = match.group(2).lstrip("\n")
    return {"frontmatter": frontmatter, "body": body, "path": path}


def write_entity(path: Path, frontmatter: dict[str, Any], body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fm_text = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False).strip()
    content = f"---\n{fm_text}\n---\n\n{body.strip()}\n"
    path.write_text(content, encoding="utf-8")


def list_entities(directory: Path) -> list[dict[str, Any]]:
    if not directory.exists():
        return []
    return [read_entity(p) for p in sorted(directory.glob("*.md"))]


def delete_entity(path: Path) -> bool:
    if path.exists():
        path.unlink()
        return True
    return False


def find_links(body: str) -> list[str]:
    """Extract Obsidian-style [[wiki links]] from a markdown body."""
    return re.findall(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]", body)
