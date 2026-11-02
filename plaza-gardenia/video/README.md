# Plaza Gardenia · video vertical

`plaza-gardenia-vertical.mp4` (1080×1920, 37 s) rehace el video del papá de Rodrigo con sus mismas tomas reales: dron, rótulo, locales, interior, atardecer y la calle de Talanga. La música es "Stylish" de FASSounds (110 BPM) y los cortes caen en los compases.

Diseño según los skills del repo (`.claude/skills/taste-skill`, `impeccable`): una sola letra (Hanken Grotesk), titulares en minúscula normal y alineados a la izquierda, sin etiquetas chiquitas arriba del titular, sin cursivas, sin líneas finas, sin sombras ni degradados. El fondo es blanco y la letra es verde oscuro, los colores del logo de la plaza.

Datos que salen en pantalla (confirmados, sin precios): locales de 7 × 8 m (56 m²) con baño propio, 27 parqueos, un local con carril de drive-thru, RNP, Pollo Chilero e INCOOLL Systems en el rótulo, y el teléfono 9338-1063.

```bash
npm i -g hyperframes && npm i --prefix deps gsap@3.12.5 @fontsource/hanken-grotesk
python3 gen.py video-papa.mov salida deps
cd salida/plaza && hyperframes render . -o ../plaza-gardenia-vertical.mp4 -q high
```
