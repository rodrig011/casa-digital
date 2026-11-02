#!/usr/bin/env bash
# Instala un Harvey aparte para Plaza Gardenias. No toca el Harvey de Clientia.
# Uso, desde la carpeta casa-digital:   bash harvey/plaza-gardenias/instalar.sh
# Queda en ~/harvey-plaza (en Windows: C:\Users\rodri\harvey-plaza).
set -euo pipefail
AQUI="$(cd "$(dirname "$0")" && pwd)"
export HARVEY_DIR="${HARVEY_DIR:-$HOME/harvey-plaza}"
bash "$AQUI/../instalar.sh"          # misma versión de Harvey y mismos parches que Clientia
cp "$AQUI/harvey.local.yaml" "$HARVEY_DIR/harvey.local.yaml"
cp "$AQUI/skills/product_knowledge.md" "$HARVEY_DIR/skills/product_knowledge.md"
cp "$AQUI/cargar_prospectos.py" "$AQUI/../avisos.py" "$HARVEY_DIR/"
mkdir -p "$HARVEY_DIR/entrada" && cp "$AQUI/entrada/"*.csv "$HARVEY_DIR/entrada/"
cp "$AQUI/iniciar-harvey-plaza.cmd" "$HARVEY_DIR/"
grep -q '^AVISO_PREFIJO=' "$HARVEY_DIR/.env" || echo 'AVISO_PREFIJO="[Plaza] "' >> "$HARVEY_DIR/.env"
echo
echo "Harvey de la plaza listo en $HARVEY_DIR"
echo "Falta: en $HARVEY_DIR/.env poner SMTP_* e IMAP_* del correo de la plaza (lo escribe Rodrigo),"
echo "y en harvey.local.yaml cambiar CORREO_DE_LA_PLAZA por ese correo."
