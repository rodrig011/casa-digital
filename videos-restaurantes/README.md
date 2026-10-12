# Videos y archivos de marca por restaurante

Genera un proyecto de HyperFrames por restaurante (video vertical de 40 s) y su archivo de marca.

- `restaurants.json`: datos, paleta y tipografía de cada restaurante.
- `gen.py`: arma `videos/<slug>/index.html`. Los cortes caen en los golpes del tema (120 BPM, compás cada 2 s, primer golpe fuerte en 0:08.017, detectado con `hyperframes beats`).
- `brand.py`: escribe `marca.md` por restaurante en la carpeta compartida del proyecto.

Requisitos junto a los scripts: `musica.mp3`, `logo-clientia.jpeg` y `deps/` con `npm i gsap@3.14.2 @fontsource/{inter,fraunces,archivo-black,bebas-neue,dm-serif-display,cormorant-garamond}`.

```bash
npm i -g hyperframes@0.8.150 && hyperframes browser ensure
python3 gen.py            # o: python3 gen.py el-patio
cd videos/el-patio && hyperframes render . -o ../el-patio.mp4 -q high
python3 brand.py
```

## v2 (estilo Apple)

`gen2.py` hace la versión de 64 s: fondo negro, texto que entra con desenfoque, iPhone en 3D, estelas de luz al inicio y logo de Clientia Tech redibujado en vector (`clientia-mark.svg`) que se dibuja en la pausa del tema (0:56) y se llena en el golpe de 0:58. Necesita además `npm i @fontsource/inter-tight`.

```bash
python3 gen2.py && cd videos2/el-patio && hyperframes render . -o ../el-patio.mp4 -q high
```
