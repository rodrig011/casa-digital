#!/usr/bin/env bash
# Instala el bot y el panel de Con Sabor a Pueblo en un Droplet nuevo de DigitalOcean (Ubuntu 24.04).
# Se corre UNA vez, como root, en la consola del Droplet:
#   curl -fsSL https://raw.githubusercontent.com/rodrig011/casa-digital/main/con-sabor-a-pueblo/droplet/instalar.sh | bash
# Con dominio propio (opcional; antes cree el registro A en Namecheap apuntando a la IP del Droplet):
#   curl -fsSL https://raw.githubusercontent.com/rodrig011/casa-digital/main/con-sabor-a-pueblo/droplet/instalar.sh | bash -s -- bot.clientiatech.com
# Se puede volver a correr: no borra datos ni cambia las llaves ya creadas.
set -euo pipefail

SERVICIO=con-sabor-a-pueblo
REPO=https://github.com/rodrig011/casa-digital.git
APP=/opt/casa-digital
DATOS=/var/data
ENVF=/etc/$SERVICIO.env

[ "$(id -u)" = 0 ] || { echo "Córralo como root (en la consola del Droplet ya es root)."; exit 1; }
. /etc/os-release
[ "${ID:-}" = ubuntu ] || { echo "Este instalador es para Ubuntu (24.04). Cree el Droplet con Ubuntu."; exit 1; }

paso() { printf '\n\033[1m==> %s\033[0m\n' "$1"; }
export DEBIAN_FRONTEND=noninteractive

paso "Sistema al día y actualizaciones de seguridad automáticas"
apt-get update -qq
apt-get -y -qq upgrade
apt-get install -y -qq curl git ufw unattended-upgrades ca-certificates gnupg debian-keyring debian-archive-keyring apt-transport-https openssl nano
dpkg-reconfigure -f noninteractive unattended-upgrades
timedatectl set-timezone America/Tegucigalpa

paso "Memoria extra (swap de 1 GB) para que no se quede sin memoria"
if ! swapon --show | grep -q /swapfile; then
  fallocate -l 1G /swapfile && chmod 600 /swapfile && mkswap /swapfile >/dev/null && swapon /swapfile
  grep -q '^/swapfile' /etc/fstab || echo '/swapfile none swap sw 0 0' >> /etc/fstab
fi

paso "Node.js 22"
if ! command -v node >/dev/null || [ "$(node -p 'process.versions.node.split(".")[0]')" -lt 22 ]; then
  curl -fsSL https://deb.nodesource.com/setup_22.x | bash - >/dev/null
  apt-get install -y -qq nodejs
fi
node -v

paso "Caddy (HTTPS automático)"
if ! command -v caddy >/dev/null; then
  curl -1sLf https://dl.cloudsmith.io/public/caddy/stable/gpg.key | gpg --dearmor --yes -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
  curl -1sLf https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt > /etc/apt/sources.list.d/caddy-stable.list
  apt-get update -qq && apt-get install -y -qq caddy
fi

paso "Usuario del bot y código"
id bot >/dev/null 2>&1 || useradd --system --home "$APP" --shell /usr/sbin/nologin bot
if [ -d "$APP/.git" ]; then git -C "$APP" fetch -q origin main && git -C "$APP" reset -q --hard origin/main
else git clone -q --depth 1 "$REPO" "$APP"; fi
(cd "$APP/bot-restaurante" && npm ci --omit=dev --no-audit --no-fund --loglevel=error)
chown -R bot:bot "$APP"
mkdir -p "$DATOS" && chown bot:bot "$DATOS" && chmod 700 "$DATOS"

paso "Configuración ($ENVF)"
IP=$(curl -fsS https://api.ipify.org || hostname -I | awk '{print $1}')
DOMINIO=${1:-$(echo "$IP" | tr . -).sslip.io}
if [ ! -f "$ENVF" ]; then
  sec() { openssl rand -hex 32; }
  umask 077
  cat > "$ENVF" <<CONF
# Configuración del bot de Con Sabor a Pueblo. Solo root la puede leer. Para cambiarla: con-sabor editar
# NUNCA copie este archivo a un chat, un correo ni a GitHub.
NODE_ENV=production
TZ=America/Tegucigalpa
PORT=3000
DATA_DIR=$DATOS
EXIGIR_CIFRADO=on
NEGOCIO=negocios/con-sabor-a-pueblo.json
PUBLIC_URL=https://$DOMINIO

# GUARDE UNA COPIA de DATA_KEY en su gestor de contraseñas: sin ella no se abren los pedidos guardados.
DATA_KEY=$(sec)
PANEL_SECRET=$(sec)
LEADS_TOKEN=$(sec)
META_VERIFY_TOKEN=$(openssl rand -hex 16)

# El JSON del archivo privado del proyecto, entre comillas simples, en una sola línea:
# NEGOCIO_PRIVADO='{"sucursales":{"tegucigalpa":{"whatsapp":""}},"repartidores":[],"cobro":{"transferencia":""}}'
NEGOCIO_PRIVADO=

# WhatsApp (Meta). Vacíos = el panel funciona y WhatsApp todavía no está conectado.
META_TOKEN=
META_PHONE_ID=
META_NUMERO=
META_APP_SECRET=
META_PLANTILLA=
META_PLANTILLA_CODIGO=
OWNER_WHATSAPP=

# Claude (la IA). Vacía = contesta el menú.
ANTHROPIC_API_KEY=
ANTHROPIC_MODEL=claude-haiku-5-5
BOT_IA=on
LIMITE_IA_DIA=60
CONF
  chmod 600 "$ENVF"
  echo "Creada. Llaves nuevas generadas."
else
  echo "Ya existía: se deja igual."
fi
DOMINIO=$(sed -n 's#^PUBLIC_URL=https://##p' "$ENVF")

paso "Servicio que arranca solo y se levanta si se cae"
cat > /etc/systemd/system/$SERVICIO.service <<UNIT
[Unit]
Description=Bot y panel de Con Sabor a Pueblo
After=network-online.target
Wants=network-online.target

[Service]
User=bot
WorkingDirectory=$APP/bot-restaurante
EnvironmentFile=$ENVF
ExecStart=/usr/bin/node server.js
Restart=always
RestartSec=3
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$DATOS

[Install]
WantedBy=multi-user.target
UNIT
systemctl daemon-reload
systemctl enable -q $SERVICIO
systemctl restart $SERVICIO

paso "HTTPS en https://$DOMINIO"
cat > /etc/caddy/Caddyfile <<CADDY
$DOMINIO {
	encode gzip
	reverse_proxy 127.0.0.1:3000
}
CADDY
systemctl reload caddy || systemctl restart caddy

paso "Firewall: solo SSH, HTTP y HTTPS"
ufw allow OpenSSH >/dev/null && ufw allow 80/tcp >/dev/null && ufw allow 443/tcp >/dev/null
ufw --force enable >/dev/null

paso "Comando de ayuda: con-sabor"
install -m 755 "$APP/con-sabor-a-pueblo/droplet/con-sabor" /usr/local/bin/con-sabor

sleep 3
if curl -fsS http://127.0.0.1:3000/ >/dev/null; then ESTADO="✓ El bot está corriendo."; else ESTADO="✗ El bot no contestó todavía. Vea: con-sabor logs"; fi
cat <<FIN

$ESTADO

Panel:    https://$DOMINIO/panel   (el certificado HTTPS tarda hasta 1 minuto la primera vez)
Webhook:  https://$DOMINIO/meta    (para Meta, cuando lo conecte)

Siguiente:
  1. con-sabor editar      pegue NEGOCIO_PRIVADO (y lo de Meta y Claude cuando los tenga). Guarda y reinicia solo.
  2. con-sabor usuario agregar correo@ejemplo.com "Nombre" 504XXXXXXXX
  3. con-sabor revisar
  4. Copie DATA_KEY a su gestor de contraseñas: con-sabor llave
FIN
