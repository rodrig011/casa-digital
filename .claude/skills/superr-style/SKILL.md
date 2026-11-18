---
name: superr-style
description: Warm cream-paper look (dark ink, one orange marker, outlined pill buttons, no gradients) that rodrigo chose for clientiatech.com. Use for any visual work on the Clientia Tech site or when he asks for "el estilo Superr".
---

# Estilo Superr, adaptado a Clientia Tech

rodrigo pegó esta guía el 2026-11-17 ("Aprende de este diseño. Para la página de Clientia Tech").
La guía original completa está en [reference.md](reference.md). Este archivo dice cómo la usamos nosotros.
Úsela junto con las otras skills de diseño (impeccable, taste-skill, emil-design-eng): esta da la dirección, ellas dan el oficio.

## Lo que tomamos

- **Papel crema, tinta oscura, un solo acento.** Fondo `#FDFBF9`, segunda superficie `#F7EFE9`, tinta `#171717`, titulares en cacao `#2B1A07`.
- **Naranja marcador `#FF6F1E`** solo para: el subrayado a mano de UNA palabra, el pulgar del deslizador, y la franja final (contacto + pie). Para texto naranja sobre crema use `#B54606` (contraste 5.3:1); `#FF6F1E` sobre crema no da contraste para texto.
  El naranja también es el color del panel del producto (`--brand #FF4C00`), así que la página y el sistema se sienten de la misma casa.
- **Botones con borde, nunca rellenos:** crema, borde 1.5px tinta, píldora, sombra de 1–2px. Al pasar el mouse sube 1px y deja una sombra dura de 3px; nunca cambia a un relleno de color.
- **Superficies mate:** bordes finos oscuros en vez de rellenos, sombra de tarjeta `0 2px 20px rgba(0,0,0,.06)` como máximo, tarjetas radio 12px, franja final radio 56px arriba (32px en celular).
- **El producto real es la imagen:** pantallazos reales del panel con borde de 1.5px, como objetos puestos a mano (los teléfonos laterales girados −2.5° y 2°). Nada de ilustraciones abstractas, 3D ni fotos de banco.
- **Leyenda a mano** en la letra de titulares, color `#B54606`, girada −2°, con una flecha fina dibujada que apunta a la cosa real (en la portada: "escríbale, es el bot de verdad" → el chat).
- **Alineado a la izquierda**, mucho aire, sin centrar por costumbre.

## Lo que cambiamos o no usamos

- **Letra:** gelica es comercial. Usamos **Young Serif** (OFL, `clientia-tech/src/fonts/young-serif-latin.woff2`) para titulares y **Hanken Grotesk** (la que ya teníamos) para texto, menús y botones, en el papel que Geist tiene en la guía. No use Fraunces ni DM Serif aunque la guía los sugiera: impeccable los marca como letra de IA por defecto, y a rodrigo no le gusta la letra "tipo IA".
- **Números grandes** (el teléfono del contacto) van en Hanken Grotesk: Young Serif tiene números antiguos que bailan.
- **Mayúscula normal en los titulares**, no todo en minúscula: los clientes son dueños de restaurantes en Honduras y la minúscula total se lee como descuido en español.
- **Sin stickers** (rayos, ositos, corazones) ni el azul, rosado y verde de stickers: la guía es para una marca escolar; para nosotros quedaría infantil.
- **El chat de WhatsApp y la pantalla de cocina** conservan su propio aspecto (son el producto, marcados con `data-ui`); solo se les pone borde o sombra para que se sienten en la página.

## Tokens que usa la página (`clientia-tech/src/index.html`)

```css
--bg:#FDFBF9; --surface:#F7EFE9; --ink:#171717; --cocoa:#2B1A07; --soft:#5C5049;
--line:#171717; --hair:#E4D9CF; --marker:#FF6F1E; --accent:#B54606;
--shadow-card:0 2px 20px rgba(0,0,0,.06); --shadow-btn:0 1px 2px rgba(0,0,0,.25);
--display:"Young Serif","Hanken Grotesk",Georgia,serif;
```

## Revisar antes de entregar

- Nada de degradados, vidrio esmerilado ni neón.
- Una sola palabra subrayada a mano por pantalla.
- Ningún botón relleno de color.
- Texto naranja solo en `#B54606`.
- En el celular, sin desborde horizontal (`scrollWidth` igual al ancho de la pantalla).
