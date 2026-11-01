"""Parche de Clientia Tech para Harvey: si un prospecto pregunta el precio, Harvey NO contesta.

La conversación queda en "needs_human" (aparece en el panel como escalada), no se redacta respuesta,
y avisos.py le manda a Rodrigo el correo "💰 Pidió precio". Rodrigo contesta en persona.

Cómo funciona: agrega palabras de precio (español e inglés) a las palabras que ya hacen que Harvey
escale sin contestar (abogado, demanda, spam...), le dice al clasificador que una pregunta de
precio es "escalate", y si el prospecto ya está en manos de Rodrigo (needs_human) cualquier mensaje
nuevo suyo también se escala sin respuesta. Si Rodrigo se lo devuelve a Harvey desde el panel,
Harvey vuelve a contestarle. Se puede correr varias veces; si ya está aplicado no cambia nada.

    .venv\\Scripts\\python parche_precios.py            (desde C:\\Users\\rodri\\harvey)
Después hay que reiniciar Harvey (iniciar-harvey.cmd).
"""

import sys
from pathlib import Path

MARCA = "# Clientia Tech: precio_a_rodrigo"

PALABRAS = (
    "precio", "costo", "cotiz", "tarifa", "mensualidad", "presupuesto", "inversión", "inversion",
    "cuánto cuesta", "cuanto cuesta", "cuánto cobra", "cuanto cobra", "cuánto sale", "cuanto sale",
    "cuánto vale", "cuanto vale", "cuánto sería", "cuanto seria", "cuánto es", "cuanto es",
    "cuánto le", "cuanto le", "cuánto me", "cuanto me", "cuánto nos", "cuanto nos",
    "price", "pricing", "how much", "quote",
)

BLOQUE = f'''

{MARCA}
# Una pregunta de precio la contesta Rodrigo, nunca Harvey: se escala sin respuesta automática.
PRECIO_PATTERNS = {PALABRAS!r}
ESCALATION_PATTERNS = ESCALATION_PATTERNS + PRECIO_PATTERNS
'''

CHEQUEO_VIEJO = "        elif any(p in keyword_text for p in ESCALATION_PATTERNS):\n"
CHEQUEO_NUEVO = (
    "        elif any(c.prospect_id == prospect.id  # Clientia Tech: ya está en manos de Rodrigo\n"
    "                 for c in await self.state.get_conversations_by_status(\"needs_human\")):\n"
    "            intent = \"escalate\"\n" + CHEQUEO_VIEJO
)

REGLA_VIEJA = 'When in doubt between anything and "escalate", choose "escalate".'
REGLA_NUEVA = (REGLA_VIEJA + '\nIf they ask about price, cost, fees, plans or a quote (in any language), '
               'choose "escalate": a person answers that, never an automatic reply.')


def aplicar(handler: Path) -> str:
    t = handler.read_text(encoding="utf-8")
    if MARCA in t:
        return "ya estaba aplicado"
    inicio = t.index("ESCALATION_PATTERNS = (")
    fin = t.index("\n)\n", inicio) + 2
    if REGLA_VIEJA not in t or t.count(CHEQUEO_VIEJO) != 1:
        raise SystemExit("No encontré la regla del clasificador: la versión de Harvey cambió, revisar a mano.")
    t = t[:fin] + BLOQUE + t[fin:]
    t = t.replace(REGLA_VIEJA, REGLA_NUEVA, 1).replace(CHEQUEO_VIEJO, CHEQUEO_NUEVO, 1)
    handler.write_text(t, encoding="utf-8")
    return "aplicado"


if __name__ == "__main__":
    base = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent
    print(aplicar(base / "harvey" / "agents" / "handler.py"))
