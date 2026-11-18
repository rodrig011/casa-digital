---
name: slush-style
description: Pastel sticker-book look (giant crushed display type, inflated blue ribbon, outlined sticker colors, black pill buttons) that clientiatech.com uses since 2026-11-18. Use for any visual work on the Clientia Tech site.
---

# Estilo Slush, adaptado a Clientia Tech

rodrigo subió esta guía el 2026-11-18 y pidió "borrón y cuenta nueva, algo exacto como eso relacionado a nuestra marca".
La portada (`clientia-tech/src/index.html`) se rehízo desde cero con ella. La guía original completa está en [reference.md](reference.md).
Úsela junto con las otras skills de diseño (impeccable, taste-skill, emil-design-eng). Reemplaza a `superr-style`.

## Lo que tomamos tal cual

- **Franjas de color a todo lo ancho**, cada sección un "póster": celeste `#DCEEFF` (portada, panel), blanco, gris `#CCCCCC` (lo que hace), lavanda `#E9CCFF` (quiénes somos), azul `#4DA2FF` (contacto).
- **Letra de exhibición gigante en mayúsculas**: Bowlby One (OFL, `clientia-tech/src/fonts/bowlby-one-latin.woff2`) en lugar de Lateral. Texto, menús y botones en Hanken Grotesk (en el papel de Aeonik Pro), etiquetas en mayúscula 700 con 0.032em.
- **Paleta de stickers compartida**: menta `#55DB9C`, lavanda, amarillo `#FFD731`, brasa `#FB4903`, violeta `#5C4ADE`, como rellenos de tarjetas y stickers; nunca como color de enlace.
- **Bordes negros de 1.5px en todo** (tarjetas, botones, fotos), sin sombras, sin degradados.
- **Botones píldora**: negro relleno para la acción principal (WhatsApp), blanco con borde para la secundaria.
- **Franja negra arriba** con texto corriendo (se detiene con movimiento reducido).
- **Cinta azul inflada** detrás del titular: SVG de tres trazos (negro, azul, brillo celeste), no 3D renderizado.
- **Stickers con borde negro, girados**: globo de chat, moneda con "L" (lempira), campana de pedido, visto bueno. Son cosas de nuestro negocio, no los cohetes ni billeteras de Slush.

## Lo que ajustamos

- **Interlineado 0.9 (0.88 en la portada)** en vez de 0.75–0.80: con 0.8 las tildes y la Ñ chocan con la línea de arriba ("DUEÑOS" se leía "DUENOS").
- **El chat de WhatsApp y la pantalla de cocina** conservan el aspecto del producto (`data-ui`), metidos en un marco de color con borde negro.
- **Pantallazos reales** del panel en tarjetas de color; Slush no usa fotos, pero nuestro producto real es la mejor prueba.
- **Celular**: la cinta baja al final de la portada para no pasar detrás del texto; solo dos stickers.
- Nada de 3D con three.js (rodrigo lo rechazó el 2026-11-17).

## Revisar antes de entregar

- Ninguna tilde ni Ñ tapada en titulares de varias líneas.
- Sin desborde horizontal en 390 px.
- Ningún texto encima de la cinta en el celular.
- Azul `#4DA2FF` y verde menta solo decorativos, nunca como botón o estado.
