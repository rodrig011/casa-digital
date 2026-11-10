# Harvey WhatsApp

La versión de Harvey para WhatsApp. Página para el celular: https://claude.ai/artifact/SUV15bH8BrWtgiokUBPc59 (privada, entra con tu cuenta de claude.ai).

## Cómo funciona

1. **Hoy** te da hasta 10 negocios nuevos por día y los seguimientos que tocan. Cada uno trae su mensaje escrito.
2. Tocás **Abrir en WhatsApp**: se abre el chat con el texto puesto. Lo mandás y tocás **Ya lo mandé**.
3. Si no contestan, a los 3 días aparece solo el seguimiento (la presentación completa, para que se la pasen al dueño). A los 7 días más, un último mensaje corto, y se cierra.
4. Si contestan, tocás **Contestó**, pegás lo que te escribieron y Harvey escribe la respuesta con las reglas de Clientia (de usted, sin precios por escrito, 30 días gratis, buscando la llamada de 10 minutos). La revisás, la abrís en WhatsApp y la mandás.
5. **Agregar**: si ves un negocio en TikTok, ponés nombre, número y lo que viste, y Harvey escribe sus mensajes.

## Por qué el último toque lo das vos

WhatsApp no deja que un programa le escriba primero a un negocio que no lo pidió. La API oficial solo permite empezar con plantillas aprobadas a gente que aceptó recibir mensajes, y las herramientas no oficiales que mandan solas hacen que bloqueen el número (el +1 765 que sale en todos los videos). Harvey hace todo lo demás: elige a quién, escribe, lleva la cuenta de días y escribe las respuestas.

## Archivos

- `prospectos.py`: los 56 negocios con celular de `investigacion-masiva/` y `harvey/resultados/`, con lo que vimos de cada uno y su mensaje. Correrlo genera `prospectos.json`.
- `prospectos.json`: lo que se cargó en la página (colección `negocios`).
- `harvey-whatsapp.html`: la página.

Para cargar negocios nuevos en la página, Claude los agrega a `prospectos.py` y los sube a la base de la página con ArtifactData (colección `negocios`, `estado: "nuevo"`).

## Cambio del 10 nov 2026: el primer mensaje ya no pregunta por el dueño

De 15 negocios que recibieron "no es para un pedido, ¿cómo me comunico con el dueño?", 13 no contestaron y a los 2 que contestaron "díganos" (Carnes El Argentino y Felipe's Mexican) nunca se les dijo para qué era. El primer mensaje ahora va directo: quién escribe, un dato real del negocio, qué armamos y "si usted no es el dueño, ¿me haría el favor de pasarle este mensaje?". Sin precios, sin llamada para Honduras.

- Ya están así en la página 10 negocios nuevos (aparecen primero): Home Food HN, Típicos Olanchanos, La Esquina del Sabor Garífuna, Condys Grill, Típicos Nicolle, Pollos Sierra's, The Soul Chkn Club, Tato's Wings, Cric Cric Burger y Asados Marina.
- A 8 que solo recibieron la pregunta por el dueño se les cambió el seguimiento por el mensaje completo: Hijo de Pupa, Con Sabor a Pueblo, David's Crab, El Inge del Taco, Legato Burgers, Pollos Mamavila, Asados Mary y La Cacerola.
- Es una prueba: comparar cuántos contestan contra los 2 de 15 de antes. Si funciona mejor, pasar el resto al mismo formato.
- `prospectos.json` de esta carpeta es la versión vieja; la que manda es la base de datos de la página.
