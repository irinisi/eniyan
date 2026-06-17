"""Nightly Vault backup: archive the vault and keep only the N most recent archives.

Intended to run from cron, e.g.:
    0 3 * * * python -m scripts.backup_vault
"""
from __future__ import annotations

import shutil
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.config import BACKUP_DIR, BACKUP_KEEP, VAULT_PATH


def backup_vault() -> Path:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    archive_base = BACKUP_DIR / f"vault-{timestamp}"
    archive_path = shutil.make_archive(str(archive_base), "zip", root_dir=VAULT_PATH)
    _prune_old_backups()
    return Path(archive_path)


def _prune_old_backups() -> None:
    archives = sorted(BACKUP_DIR.glob("vault-*.zip"), key=lambda p: p.stat().st_mtime, reverse=True)
    for old in archives[BACKUP_KEEP:]:
        old.unlink()


if __name__ == "__main__":
    path = backup_vault()
    print(f"Backup created: {path}")
