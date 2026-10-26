"""Arma prospectos.csv y ../harvey/entrada/guatemala-el-salvador.csv desde datos.json.
Uso, desde casa-digital:  python3 expansion/herramientas/armar.py"""
import csv, json, os
AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
d = json.load(open(os.path.join(RAIZ, "datos.json"), encoding="utf-8"))
MONEDA = {"Guatemala": "GTQ (quetzales)", "El Salvador": "USD (dólares)"}
filas = sorted(d["con_correo"], key=lambda r: (r["pais"], r["prioridad"], r["nombre"]))

cols = ["prioridad", "pais", "ciudad", "nombre", "tipo", "correo", "otros_correos", "fuente_correo", "verificado_en_su_pagina",
        "whatsapp", "telefono", "web", "tiktok", "seguidores_tiktok", "video_top_vistas", "respondio", "senal", "gancho", "nota"]
with open(os.path.join(RAIZ, "prospectos.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(cols)
    for r in filas:
        w.writerow([r["prioridad"], r["pais"], r["ciudad"], r["nombre"], r["tipo"], r["correo"], " · ".join(r.get("correos_extra", [])),
                    r["fuente_correo"], "sí" if r.get("verificado") else "no", r.get("whatsapp", ""), r.get("telefono", ""), r.get("web", ""),
                    r.get("tiktok", ""), r.get("tiktok_seguidores", ""), r.get("tiktok_top", ""), r.get("tiktok_respondio", ""),
                    r.get("senal", ""), r["gancho"], r.get("nota", "")])
    for r in d["solo_whatsapp"]:
        w.writerow(["whatsapp", r["pais"], r["ciudad"], r["nombre"], r["tipo"], "", "", "", "", r.get("whatsapp", ""), "", "",
                    r.get("tiktok", ""), r.get("tiktok_seguidores", ""), r.get("tiktok_top", ""), r.get("tiktok_respondio", ""), r.get("senal", ""), "", ""])

# Entrada para Harvey: solo los que tienen correo, con lo que se puede decir de ellos (hechos con fuente)
os.makedirs(os.path.join(RAIZ, "..", "harvey", "entrada"), exist_ok=True)
with open(os.path.join(RAIZ, "..", "harvey", "entrada", "guatemala-el-salvador.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["prioridad", "pais", "moneda", "ciudad", "negocio", "correo", "fuente_correo", "verificado_en_su_pagina", "hechos_para_el_correo", "whatsapp_del_negocio", "nota", "enviado"])
    for r in filas:
        hechos = r["gancho"] + (" " + r["senal"] if r.get("senal") else "")
        w.writerow([r["prioridad"], r["pais"], MONEDA[r["pais"]], r["ciudad"], r["nombre"], r["correo"], r["fuente_correo"],
                    "sí" if r.get("verificado") else "no", hechos, r.get("whatsapp", ""), r.get("nota", ""), ""])
print(len(filas), "con correo ·", len(d["solo_whatsapp"]), "solo WhatsApp")
