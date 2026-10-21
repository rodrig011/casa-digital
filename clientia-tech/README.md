# Página de Clientia Tech

`index.html` es la página completa en un solo archivo (letra, pantallazos y logo adentro). No se edita a mano: se arma desde `src/` con

```bash
node clientia-tech/build.mjs
```

- `src/index.html`: el diseño y los textos.
- `src/img/`: pantallazos reales del panel de `bot-restaurante/` con el restaurante de ejemplo ("Pollo de Ejemplo") y el símbolo de la marca.
- La demostración del chat corre el motor real del bot (`bot-restaurante/engine.js` y `negocio.js`) con `negocios/ejemplo.json`. Si el bot cambia, se vuelve a correr `build.mjs`.
- WhatsApp del botón: +1 (765) 543-4251, con el mensaje "Hola Rodrigo, vi la página de Clientia Tech. Mi negocio es: ".

Sale en **https://clientiatech.com**. GitHub Pages está en "Deploy from a branch" (main, raíz), así que `build.mjs` también escribe `index.html` en la raíz del repositorio (con `CNAME` y `.nojekyll`). Si algún día se cambia Pages a "GitHub Actions", se publica sola con `.github/workflows/pagina-clientia.yml` cada vez que cambia algo aquí en `main` (solo esta página, nada más del repositorio).

La foto de "Quién soy" es `src/img/rodrigo.webp` (recorte 4:5 de la foto que mandó Rodrigo).

## Páginas legales y página de prueba

- `src/legal/`: términos, privacidad, cookies, reembolsos y aviso legal. `build.mjs` mete cada una en `src/legal/plantilla.html` y las publica junto a la portada (clientiatech.com/terminos.html, etc.).
- `src/prueba.html` → clientiatech.com/prueba.html: prueba hecha desde cero con la skill oficial `frontend-design` de Anthropic (`.claude/skills/frontend-design/`). Idea: un día del restaurante hora por hora (11:47 p. m., 10:00 a. m., 12:40 p. m., 3:15 p. m., 9:00 p. m.), cada hora con la luz de ese momento; letras Big Shoulders (las horas) e Instrument Sans (el texto). La portada no cambia; si gana la prueba, se copia `src/prueba.html` sobre `src/index.html`. Tiene `noindex` mientras es prueba, y casi no se mueve a propósito.
- `src/prueba-ibm.html` → clientiatech.com/prueba-ibm.html: segunda prueba, sobria tipo corporativa (IBM Plex Sans/Mono, licencia OFL en `src/fonts/LICENSE-ibm-plex.txt`): franja negra arriba, botones rectos, fondo blanco y gris claro, el mismo bot real y los pantallazos reales. Revisada con `.claude/skills/taste-skill/scripts/inspect.mjs`. `noindex` mientras es prueba.
