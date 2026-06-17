import os
from pathlib import Path

VAULT_PATH = Path(os.environ.get("TEAMOS_VAULT_PATH") or Path(__file__).resolve().parents[2] / "vault")

TASKS_DIR = VAULT_PATH / "Tasks"
PROJECTS_DIR = VAULT_PATH / "Projects"
KNOWLEDGE_DIR = VAULT_PATH / "Knowledge"
MEETINGS_DIR = VAULT_PATH / "Meetings"
PEOPLE_DIR = VAULT_PATH / "People"
TEMPLATES_DIR = VAULT_PATH / "Templates"

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
API_BASE_URL = os.environ.get("TEAMOS_API_BASE_URL", "http://localhost:8000")
BACKUP_DIR = Path(os.environ.get("TEAMOS_BACKUP_DIR") or VAULT_PATH.parent / "backups")
BACKUP_KEEP = int(os.environ.get("TEAMOS_BACKUP_KEEP", "30"))
