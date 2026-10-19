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
- `src/prueba.html` → clientiatech.com/prueba.html: prueba hecha con la skill oficial `frontend-design` de Anthropic (`.claude/skills/frontend-design/`), idea de la comanda colgada en el riel de la cocina, letra Archivo. La portada no cambia; si gana la prueba, se copia `src/prueba.html` sobre `src/index.html`. Tiene `noindex` para que Google no la muestre mientras es prueba. A propósito casi no se mueve (solo la comanda al caer), aunque el inspector de taste-skill pida más movimiento.
