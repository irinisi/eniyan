# Деплой TeamOS на VPS

Целевой сервер: Hetzner CX23, Ubuntu 24.04, IP `135.181.198.243`,
домен `teamos.anotheroffice.work` (A-запись уже указывает на сервер).

## 1. Подключение по SSH

```bash
ssh -i ~/.ssh/<твой_приватный_ключ> root@135.181.198.243
```

(SSH-ключ, добавленный при создании сервера в Hetzner.)

## 2. Клонировать репозиторий

```bash
git clone <URL_РЕПОЗИТОРИЯ> /opt/teamos
cd /opt/teamos
git checkout claude/cool-turing-vqt4u3   # или main, если уже влит
cd teamos
```

## 3. Заполнить .env

```bash
cp .env.example .env
nano .env
```

Обязательно укажи:
- `TELEGRAM_BOT_TOKEN` — токен бота от @BotFather
- `TEAMOS_DIGEST_CHAT_ID` — chat_id, куда слать утренний дайджест (можно оставить пустым и настроить позже)
- `TEAMOS_MINIAPP_URL=https://teamos.anotheroffice.work`
- `TEAMOS_API_BASE_URL=http://127.0.0.1:8000` (бот общается с backend локально на сервере)

## 4. Запустить деплой-скрипт

```bash
sudo bash deploy/deploy.sh
```

Скрипт сам:
- ставит Docker, nginx, certbot
- поднимает backend, bot, syncthing через docker compose
- настраивает nginx (Mini App статика + проксирование `/api/` на backend)
- выпускает Let's Encrypt сертификат и включает HTTPS-редирект
- открывает нужные порты в ufw (22, 80, 443, 22000, 21027 — для Syncthing)

После завершения проверь:

```bash
curl https://teamos.anotheroffice.work/api/health
# {"status":"ok"}
```

Открой `https://teamos.anotheroffice.work` в браузере — должен открыться Mini App.

## 5. Настроить Mini App в BotFather

В диалоге с @BotFather:

```
/mybots → выбрать бота → Bot Settings → Menu Button → Configure menu button
```

Указать URL: `https://teamos.anotheroffice.work`

Либо через `/newapp`, если нужен отдельный Web App (не обязательно для MVP — кнопка в `/start` уже шлёт `WebAppInfo` с этим URL).

## 6. Проверить бота

В Telegram:
- `/start` — должна появиться кнопка "🏠 Открыть TeamOS", открывающая Mini App
- `/tasks`, `/newtask`, `/search <запрос>` — должны работать

## 7. Cron: бэкапы и дайджест

```bash
crontab -e
```

Добавить:

```cron
0 3 * * * cd /opt/teamos/teamos/backend && docker compose run --rm backend python scripts/backup_vault.py >> /var/log/teamos-backup.log 2>&1
0 9 * * * cd /opt/teamos/teamos/bot && docker compose run --rm bot python digest.py >> /var/log/teamos-digest.log 2>&1
```

(Можно поправить под фактическую структуру docker compose — главное, что обе команды должны выполняться внутри контейнеров, где доступны зависимости и `.env`.)

## 8. Syncthing — подключение Obsidian-устройств участников

1. На сервере: `ssh -L 8384:127.0.0.1:8384 root@135.181.198.243` (туннель к закрытому Syncthing Web UI)
2. Открыть `http://127.0.0.1:8384` в браузере локально
3. На каждой машине участника команды установить Syncthing, добавить устройство по ID, расшарить папку `vault`
4. В Obsidian: **Open folder as vault** → выбрать синхронизированную папку `vault`

## Обновление после изменений в коде

```bash
cd /opt/teamos
git pull
cd teamos
docker compose up -d --build backend bot syncthing
sudo systemctl reload nginx   # если менялся deploy/nginx-teamos.conf
```
