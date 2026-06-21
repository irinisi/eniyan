#!/usr/bin/env bash
# Run as root on the target Ubuntu VPS (e.g. via SSH).
#   ssh root@<server-ip>
#   git clone <repo-url> /opt/teamos
#   cd /opt/teamos/teamos
#   cp .env.example .env && nano .env   # fill TELEGRAM_BOT_TOKEN, TEAMOS_DIGEST_CHAT_ID
#   bash deploy/deploy.sh
set -euo pipefail

DOMAIN="teamos.anotheroffice.work"
REPO_ROOT="/opt/teamos"
PROJECT_DIR="$REPO_ROOT/teamos"

if [ "$EUID" -ne 0 ]; then
  echo "Run as root" >&2
  exit 1
fi

if [ ! -f "$PROJECT_DIR/.env" ]; then
  echo "Missing $PROJECT_DIR/.env — copy .env.example, fill TELEGRAM_BOT_TOKEN, then re-run." >&2
  exit 1
fi

echo "==> Installing system packages"
apt-get update -y
apt-get install -y ca-certificates curl gnupg nginx certbot python3-certbot-nginx

if ! command -v docker >/dev/null 2>&1; then
  echo "==> Installing Docker"
  install -m 0755 -d /etc/apt/keyrings
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
  chmod a+r /etc/apt/keyrings/docker.asc
  . /etc/os-release
  echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $VERSION_CODENAME stable" \
    > /etc/apt/sources.list.d/docker.list
  apt-get update -y
  apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
fi

echo "==> Building and starting backend, bot, syncthing"
cd "$PROJECT_DIR"
docker compose up -d --build backend bot syncthing

echo "==> Configuring nginx (HTTP first, for certbot's HTTP-01 challenge)"
cp "$PROJECT_DIR/deploy/nginx-teamos.conf" /etc/nginx/sites-available/teamos.conf
ln -sf /etc/nginx/sites-available/teamos.conf /etc/nginx/sites-enabled/teamos.conf
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl reload nginx

echo "==> Requesting TLS certificate"
certbot --nginx -d "$DOMAIN" --non-interactive --agree-tos -m "${CERTBOT_EMAIL:-admin@$DOMAIN}" --redirect

echo "==> Configuring firewall"
apt-get install -y ufw
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 22000/tcp
ufw allow 22000/udp
ufw allow 21027/udp
ufw --force enable

echo "==> Done. https://$DOMAIN should now serve the Mini App, https://$DOMAIN/api/health the backend."
