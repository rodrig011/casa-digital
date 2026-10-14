# Coco Chicken · video de propuesta

`gen6.py` arma el proyecto de HyperFrames (1920×1080, 1 min 41 s, "Still Buggin", cortes en los compases). Usa los helpers de `gen2.py`/`gen3.py` (copiados de `videos-restaurantes/` en la rama `claude/project-thread-ul4ahh`).

`src/` tiene recortes de las capturas que mandó rodrigo (TikTok, Facebook, PedidosYa) y el logo tomado del último cuadro de su TikTok. Falta `src/tiktok.mp4` (su video "¿Pollos A 15 lempiras?" recodificado, 17 MB, no subido) y `musica2.mp3` + `deps/` junto a los scripts.

```bash
npm i -g hyperframes@0.8.150 && hyperframes browser ensure
python3 gen6.py src && cd videos6/coco-chicken && hyperframes render . -o ../coco-chicken.mp4 -q high
```
