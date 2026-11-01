#!/usr/bin/env bash
# Instala Harvey (github.com/ethanplusai/harvey) con la configuración de Clientia Tech.
# Uso, desde la carpeta casa-digital:   bash harvey/instalar.sh
# Deja Harvey en ~/harvey. Se puede correr otra vez sin problema.
set -euo pipefail

AQUI="$(cd "$(dirname "$0")" && pwd)"
DESTINO="${HARVEY_DIR:-$HOME/harvey}"
VERSION="8023a9495eb46d644f03da8c8f4d2b9e41e5836e"   # versión revisada el 2026-10-26

PY=""
for p in python3.13 python3.12 python3.11 python3; do
  if command -v "$p" >/dev/null && "$p" -c 'import sys; sys.exit(sys.version_info < (3, 11))'; then PY="$p"; break; fi
done
[ -n "$PY" ] || { echo "Falta Python 3.11 o más nuevo."; exit 1; }
command -v claude >/dev/null || echo "Aviso: falta Claude Code (claude). Instálalo y corre 'claude login'."

[ -d "$DESTINO/.git" ] || git clone https://github.com/ethanplusai/harvey "$DESTINO"
git -C "$DESTINO" fetch -q origin
git -C "$DESTINO" checkout -q "$VERSION"

"$PY" -m venv "$DESTINO/.venv"
"$DESTINO/.venv/bin/pip" install -q -e "$DESTINO"

cp "$AQUI/harvey.local.yaml" "$DESTINO/harvey.local.yaml"
cp "$AQUI/skills/product_knowledge.md" "$DESTINO/skills/product_knowledge.md"
mkdir -p "$DESTINO/parches" && cp "$AQUI/parches/precio_a_rodrigo.py" "$DESTINO/parches/"
"$DESTINO/.venv/bin/python" "$DESTINO/parches/precio_a_rodrigo.py" "$DESTINO"   # si piden precio, Harvey no contesta
[ -f "$DESTINO/.env" ] || cp "$DESTINO/.env.example" "$DESTINO/.env"

cd "$DESTINO"
.venv/bin/harvey signals --confirm free >/dev/null
echo
echo "Listo. Harvey quedó en $DESTINO"
echo "Siguiente: abre $DESTINO/.env y llena las claves (ver harvey/COMO-USAR.md)."
