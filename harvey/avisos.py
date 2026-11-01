"""Avisos de Harvey al celular de Rodrigo.

Cada 5 minutos revisa la base de Harvey (data/harvey.db, solo lectura) y, por cada mensaje nuevo
de un prospecto, le manda un correo a AVISO_A (el Gmail de Rodrigo, que suena en el celular):

  - "💰 Pidió precio: <negocio>"  si pregunta precio, costo, cuánto cuesta, cotización...
  - "⚠️ Te toca contestar"       Harvey no contesta (ya es tuyo, queja o reclamo)
  - "Respondió: <negocio>"        cualquier otra respuesta de una persona
  - las respuestas automáticas (fuera de oficina) no avisan

Si piden precio Harvey no contesta nada (parches/precio_a_rodrigo.py): el prospecto pasa a Rodrigo.

Uso (desde C:\\Users\\rodri\\harvey, lo arranca iniciar-harvey.cmd):
    .venv\\Scripts\\python avisos.py            revisa cada 5 minutos, para siempre
    .venv\\Scripts\\python avisos.py --una-vez  revisa una vez y termina
    .venv\\Scripts\\python avisos.py --prueba   manda un correo de prueba a AVISO_A (solo a Rodrigo)

Usa el mismo buzón de Harvey (SMTP_* en .env). AVISO_A en .env cambia el destino.
"""

import json
import os
import re
import smtplib
import sqlite3
import ssl
import sys
import time
from email.message import EmailMessage
from pathlib import Path

AQUI = Path(__file__).resolve().parent
DB = AQUI / "data" / "harvey.db"
VISTOS = AQUI / "data" / "avisos-enviados.json"
DESTINO_POR_DEFECTO = "rodrigoherreraarita@gmail.com"

PRECIO = re.compile(
    r"precio|costo|cu[aá]nto\s+(cuesta|cobra|vale|sale|ser[ií]a|es)|tarifa|cotiz|mensualidad|"
    r"inversi[oó]n|presupuesto|planes|paquete|\bvalor\b|\bq\s?\d|\$\s?\d|\bl\.?\s?\d",
    re.IGNORECASE,
)


def cargar_env():
    f = AQUI / ".env"
    if not f.exists():
        return
    for linea in f.read_text(encoding="utf-8", errors="ignore").splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#") or "=" not in linea:
            continue
        k, v = linea.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def contexto_tls():
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


def enviar(asunto, cuerpo):
    host = os.environ.get("SMTP_HOST", "")
    port = int(os.environ.get("SMTP_PORT", "587") or 587)
    user = os.environ.get("SMTP_USERNAME", "")
    clave = os.environ.get("SMTP_PASSWORD", "")
    destino = os.environ.get("AVISO_A", DESTINO_POR_DEFECTO)
    m = EmailMessage()
    m["From"] = user
    m["To"] = destino
    m["Subject"] = asunto
    m.set_content(cuerpo)
    if port == 465:
        with smtplib.SMTP_SSL(host, port, context=contexto_tls(), timeout=30) as s:
            s.login(user, clave)
            s.send_message(m)
    else:
        with smtplib.SMTP(host, port, timeout=30) as s:
            s.starttls(context=contexto_tls())
            s.login(user, clave)
            s.send_message(m)


def mensajes_nuevos(vistos):
    """[(clave, negocio, correo, intent, texto)] de mensajes de prospectos que todavía no avisaron."""
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True, timeout=10)
    try:
        filas = con.execute(
            "select c.id, c.intent, c.thread_json, p.email, coalesce(co.name, p.company, '') "
            "from conversations c left join prospects p on p.id = c.prospect_id "
            "left join companies co on co.id = p.company_id"
        ).fetchall()
    finally:
        con.close()
    nuevos = []
    for cid, intent, thread, correo, negocio in filas:
        try:
            msgs = json.loads(thread or "[]")
        except json.JSONDecodeError:
            continue
        for m in msgs:
            if m.get("sender") != "prospect":
                continue
            clave = f"{cid}|{m.get('timestamp', '')}"
            if clave not in vistos:
                nuevos.append((clave, negocio or correo, correo, intent or "", m.get("content", "")))
    return nuevos


def avisar(nuevo):
    clave, negocio, correo, intent, texto = nuevo
    if intent == "ooo":
        return False                        # respuesta automática: no es interés
    precio = bool(PRECIO.search(texto))
    if precio:
        asunto = f"💰 Pidió precio: {negocio}"
        que = "Preguntó el precio. Harvey no le contestó nada: este prospecto es tuyo, contestale vos hoy."
    elif intent in ("unsubscribe", "not_interested"):
        asunto = f"Dijo que no: {negocio}"
        que = "No quiere seguir. Harvey ya no le escribe más."
    elif intent == "escalate":
        asunto = f"⚠️ Te toca contestar: {negocio}"
        que = "Harvey no contesta este mensaje (ya es tuyo, o es una queja o reclamo). Contestale vos."
    else:
        asunto = f"Respondió: {negocio}"
        que = "Respondió una persona. Si Harvey preparó respuesta, espera tu aprobación."
    enviar(asunto, f"{que}\n\nNegocio: {negocio}\nCorreo: {correo}\nTipo según Harvey: {intent or 'sin clasificar'}\n\nLo que escribió:\n\n{texto.strip()[:3000]}\n")
    return True


def revisar():
    vistos = set(json.loads(VISTOS.read_text())) if VISTOS.exists() else set()
    for n in mensajes_nuevos(vistos):
        try:
            avisar(n)
        except Exception as e:              # sin internet o buzón caído: se reintenta en la próxima vuelta
            print(f"aviso no enviado ({n[1]}): {e}", file=sys.stderr)
            continue
        vistos.add(n[0])
        VISTOS.write_text(json.dumps(sorted(vistos)))


def main():
    cargar_env()
    if "--prueba" in sys.argv:
        enviar("Prueba: avisos de Harvey", "Si te llegó este correo, los avisos de Harvey funcionan.\nCuando un prospecto conteste o pida precio, te llega un correo así.")
        print("Correo de prueba enviado a", os.environ.get("AVISO_A", DESTINO_POR_DEFECTO))
        return
    while True:
        try:
            revisar()
        except Exception as e:
            print(f"error revisando: {e}", file=sys.stderr)
        if "--una-vez" in sys.argv:
            return
        time.sleep(300)


if __name__ == "__main__":
    main()
