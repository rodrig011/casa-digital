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

## Vista previa al compartir el enlace

`og.png` (1200×630) es la imagen que sale cuando alguien pega clientiatech.com en WhatsApp o Facebook. Se arma desde `src/og/og.html` con Playwright (captura de 1200×630) y `build.mjs` la copia a la raíz; el flujo de Pages también la publica.

## En el celular

Pasando la portada aparece abajo un botón fijo "Escríbame por WhatsApp". Se esconde solo cuando ya hay otro botón de WhatsApp a la vista (portada, contacto, pie) o cuando la persona está escribiendo en la demostración del bot.

## Demostración con IA

Lo que el visitante escribe va al servidor de demostración (Render gratis, se duerme). La primera respuesta espera hasta 75 s y avisa a los 7 s que tarda un poco; las siguientes esperan 30 s. Si falla, contesta el bot de menú.

## El símbolo en 3D

Después de la portada hay una escena que avanza con el scroll (`#cine`): la cámara empieza metida dentro del símbolo y se aleja mientras pasan tres frases. En la sección de contacto, el mismo símbolo gira despacio. Está hecho con three.js (`three.module.min.js`, licencia MIT en `LICENSE-three.txt`), que se carga solo cuando esa sección está cerca. Con "reducir movimiento", ahorro de datos o un teléfono con muy poca memoria no se carga nada y queda el símbolo plano de siempre. Para quitarlo: revertir el PR que lo agregó.
