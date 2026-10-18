# Página de Clientia Tech

`index.html` es la página completa en un solo archivo (letra, pantallazos y logo adentro). No se edita a mano: se arma desde `src/` con

```bash
node clientia-tech/build.mjs
```

- `src/index.html`: el diseño y los textos.
- `src/img/`: pantallazos reales del panel de `bot-restaurante/` con el restaurante de ejemplo ("Pollo de Ejemplo") y el símbolo de la marca.
- La demostración del chat corre el motor real del bot (`bot-restaurante/engine.js` y `negocio.js`) con `negocios/ejemplo.json`. Si el bot cambia, se vuelve a correr `build.mjs`.
- WhatsApp del botón: +1 (765) 543-4251, con el mensaje "Hola Rodrigo, vi la página de Clientia Tech. Mi negocio es: ".

Se publica sola en GitHub Pages con `.github/workflows/pagina-clientia.yml` cada vez que cambia algo aquí en `main` (solo esta página, nada más del repositorio).

Pendiente: una foto real de Rodrigo para la sección "Quién soy" (hoy va el símbolo de la marca en su lugar).
