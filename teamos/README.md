# TeamOS

Telegram Native Workspace на базе Obsidian Vault. Задачи, проекты и база знаний
хранятся как markdown-файлы и синхронизируются между участниками через Syncthing.
Пользователь работает только через Telegram-бота и Telegram Mini App.

## Структура

```
teamos/
├── vault/        Obsidian Vault — единственный источник данных (markdown)
├── backend/      FastAPI: REST API над Vault, поиск, дайджесты, бэкапы
├── bot/          Telegram Bot (aiogram): уведомления, быстрые действия, /newtask
└── miniapp/      Telegram Mini App (статический HTML/JS): Kanban, проекты, поиск
```

## Запуск (локально)

```bash
cp .env.example .env  # заполнить TELEGRAM_BOT_TOKEN

cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

cd ../bot
pip install -r requirements.txt
python main.py
```

Mini App — статика, можно открыть `miniapp/index.html` через любой http-сервер
(например `python -m http.server 8080` из папки `miniapp`) и указать URL в
BotFather как Web App для бота.

## Запуск через docker-compose

```bash
docker compose up --build
```

Поднимает backend (порт 8000), bot, miniapp (порт 8080) и Syncthing (порт 8384
для UI, используется для синхронизации Vault между участниками команды).

## Vault

Каждая сущность — один `.md` файл с YAML frontmatter и markdown-описанием в теле.
Связи между сущностями — через `[[wiki-ссылки]]` в духе Obsidian.

- `Tasks/task-XXX.md` — задачи
- `Projects/<slug>.md` — проекты
- `Knowledge/*.md` — база знаний
- `People/<id>.md` — участники команды (роль admin/member, telegram_id)
- `Templates/` — шаблоны для новых заметок

## API

- `GET/POST /api/tasks`, `GET/PATCH/DELETE /api/tasks/{id}`
- `GET/POST /api/projects`, `GET/DELETE /api/projects/{id}`
- `GET /api/knowledge?q=...`, `GET /api/knowledge/{id}`
- `GET /api/people`, `GET /api/people/{id}`
- `GET /api/digest` — текст утреннего дайджеста

## Бэкапы

`backend/scripts/backup_vault.py` — архивирует Vault и хранит последние
`TEAMOS_BACKUP_KEEP` (по умолчанию 30) архивов. Запускать по cron каждую ночь.

## Дайджест

`bot/digest.py` — забирает текст дайджеста из `/api/digest` и отправляет в
Telegram-чат `TEAMOS_DIGEST_CHAT_ID`. Запускать по cron в 09:00.

## Что входит в MVP

Telegram Bot, Telegram Mini App, Tasks, Projects, Knowledge, Syncthing,
Obsidian-интеграция (markdown + frontmatter + wiki-ссылки).

Не входит (v2): AI-ассистент, комментарии, мобильное приложение, вложенные
задачи, сложные права доступа, голосовые команды, OCR, генерация отчётов,
диаграмма связей знаний, личные заметки, интеграция с календарём.
