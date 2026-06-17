import os

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
API_BASE_URL = os.environ.get("TEAMOS_API_BASE_URL", "http://localhost:8000")
MINIAPP_URL = os.environ.get("TEAMOS_MINIAPP_URL", "https://example.com/miniapp")
DIGEST_CHAT_ID = os.environ.get("TEAMOS_DIGEST_CHAT_ID")
