"""Read/write markdown files with YAML frontmatter as the persistence layer.

Each entity (task, project, ...) is a single .md file: a YAML frontmatter
block followed by free-form markdown body. This module is the only place
that touches the filesystem directly so the Vault stays the single source
of truth (synced via git to Obsidian clients).
"""
from __future__ import annotations

import logging
import os
import re
import subprocess
from pathlib import Path
from typing import Any

import yaml

log = logging.getLogger(__name__)

_GIT_REPO = Path(os.environ.get("TEAMOS_GIT_REPO", "/repo"))

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


def _git_sync(message: str) -> None:
    try:
        subprocess.run(
            ["git", "add", "teamos/vault/"],
            cwd=_GIT_REPO, check=True, capture_output=True,
        )
        result = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            cwd=_GIT_REPO, capture_output=True,
        )
        if result.returncode == 0:
            return  # nothing staged
        subprocess.run(
            ["git", "commit", "-m", message],
            cwd=_GIT_REPO, check=True, capture_output=True,
        )
        subprocess.run(
            ["git", "push"],
            cwd=_GIT_REPO, check=True, capture_output=True,
        )
    except subprocess.CalledProcessError as exc:
        log.warning("git sync failed: %s", exc.stderr.decode(errors="replace"))


def write_entity(path: Path, frontmatter: dict[str, Any], body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fm_text = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False).strip()
    content = f"---\n{fm_text}\n---\n\n{body.strip()}\n"
    path.write_text(content, encoding="utf-8")
    _git_sync(f"vault: update {path.name}")


def list_entities(directory: Path) -> list[dict[str, Any]]:
    if not directory.exists():
        return []
    return [read_entity(p) for p in sorted(directory.glob("*.md"))]


def delete_entity(path: Path) -> bool:
    if path.exists():
        path.unlink()
        _git_sync(f"vault: delete {path.name}")
        return True
    return False


def find_links(body: str) -> list[str]:
    """Extract Obsidian-style [[wiki links]] from a markdown body."""
    return re.findall(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]", body)
