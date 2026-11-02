"""Carga entrada/franquicias.csv en la base de este Harvey (data/harvey.db).

Uso, desde la carpeta del Harvey de la plaza (C:\\Users\\rodri\\harvey-plaza):
    .venv\\Scripts\\python cargar_prospectos.py entrada\\franquicias.csv

Cada fila es el correo general de una empresa (no de una persona), así que entra
como "company_inbox". Las filas sin correo o con enviado=si se saltan. Se puede
correr varias veces: Harvey no duplica empresas ni correos.
"""

import asyncio
import csv
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

from harvey.models.company import Company  # noqa: E402
from harvey.models.prospect import COMPANY_INBOX_SOURCE, Prospect  # noqa: E402
from harvey.state import StateManager  # noqa: E402


async def cargar(ruta: Path):
    st = StateManager()
    await st.init_db()
    n = 0
    with ruta.open(encoding="utf-8-sig", newline="") as f:
        for fila in csv.DictReader(f):
            correo = (fila.get("correo") or "").strip()
            if not correo or (fila.get("enviado") or "").strip().lower() in ("si", "sí", "x"):
                continue
            sitio = (fila.get("sitio") or "").strip()
            dominio = sitio.split("//")[-1].split("/")[0].removeprefix("www.") if sitio else correo.split("@")[-1]
            empresa = Company(
                name=fila["empresa"].strip(), domain=dominio, website=sitio,
                industry=fila.get("giro", ""), location=fila.get("ciudad", "Honduras"),
                phone=fila.get("telefono", ""), source="lista_plaza_gardenias",
                source_url=fila.get("fuente", ""), notes=fila.get("hechos_para_el_correo", ""),
            )
            cid = await st.add_company(empresa)
            await st.add_prospect(Prospect(
                company_id=cid, email=correo, title="Expansión / nuevos locales",
                source=COMPANY_INBOX_SOURCE, source_url=fila.get("fuente", ""),
                company=empresa.name, industry=empresa.industry,
                personalization_notes=fila.get("hechos_para_el_correo", ""),
            ))
            n += 1
            print(f"cargado: {empresa.name} <{correo}>")
    print(f"\n{n} prospectos cargados. Harvey escribe los borradores y esperan tu aprobación en el Outbox.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Uso: python cargar_prospectos.py entrada/franquicias.csv")
    asyncio.run(cargar(Path(sys.argv[1])))
