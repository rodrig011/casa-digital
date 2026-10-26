# Harvey para Clientia Tech

[Harvey](https://github.com/ethanplusai/harvey) es un agente de ventas por correo: busca negocios, lee sus páginas, escribe correos en frío, lee las respuestas y sigue la conversación hasta conseguir una llamada. Piensa con tu plan de Claude (Claude Code), así que no cobra por uso de IA.

Esta carpeta trae su configuración para nosotros: escribe en español de Honduras y de usted, ofrece los 30 días sin pagar nada, nunca pone precios por escrito, busca la llamada de diez minutos y **ningún correo sale sin que lo apruebes**.

## Lo que ya probamos (26 de octubre de 2026)

Se instaló y se cargaron 3 negocios de `correos/` (Pollos El Hondureño, Basilio's, Coco Baleadas). Escribió esto, sin enviarlo:

> **Asunto:** whatsapp a la hora del almuerzo
>
> Buenas, equipo de Pollos El Hondureño.
>
> En una pollería, la hora del almuerzo es cuando más mensajes caen al WhatsApp y cuando menos manos hay para contestarlos.
>
> ¿Quién les contesta el WhatsApp a ustedes cuando el local está lleno o ya cerró?
>
> Rodrigo Herrera, Clientia Tech, WhatsApp +1 (765) 543-4251

Primer correo corto con una pregunta, sin vender todavía. Los seguimientos ya presentan el bot.

## Dónde sirve y dónde no

- **Sirve** para negocios con correo: hoteles, catering, panaderías, cadenas y empresas tipo Steel Works. Lleva el seguimiento y las respuestas solo.
- **No sirve** para los restaurantes que solo atienden por WhatsApp, TikTok o Facebook. Esos siguen por WhatsApp como hasta ahora.
- Su buscador gratis (OpenStreetMap) no tiene restaurantes. Para encontrar negocios en Honduras hay que usar **DataForSEO Google Maps** (te regalan $1 al registrarte, y cada búsqueda cuesta $0.002).

## Correrlo en la nube (desde el celular)

Claude lo corre en la nube de este proyecto, con el acceso a internet del entorno en Full. Ahí la única salida a internet es el proxy, y Harvey a propósito abre las páginas sin proxy; `nube.py` cambia solo eso: `python nube.py <comando>` en vez de `harvey <comando>`. Resultados en `resultados/`.

## Instalarlo en tu computadora

Harvey tiene que correr en tu computadora: se queda prendido revisando cada 15 minutos y usa tu sesión de Claude Code.

1. Ten instalado Python 3.11 o más nuevo y Claude Code (`claude login` con tu cuenta).
2. Desde la carpeta `casa-digital`: `bash harvey/instalar.sh`. Queda en `~/harvey`.

## Las claves (van en `~/harvey/.env`, nunca en el chat ni en el repo)

| Para qué | Qué poner en `.env` | Dónde se saca |
|---|---|---|
| Enviar y leer correos (obligatorio) | `GMAIL_CLIENT_ID`, `GMAIL_CLIENT_SECRET`, y luego correr `harvey gmail auth` | Google Cloud Console, activar Gmail API, credencial "Desktop app" |
| Encontrar negocios en Honduras | `DATAFORSEO_LOGIN`, `DATAFORSEO_PASSWORD` | app.dataforseo.com/api-access |
| Verificar que el correo existe | `REOON_API_KEY` (600 gratis al mes) | reoon.com/email-verifier |

El correo debe ser de un **dominio aparte** (por ejemplo `clientiatech.net` o `holaclientia.com`) y calentarse dos semanas antes de enviar en frío, para no quemar `clientiatech.com`. Cambia `persona.email` en `harvey.local.yaml` por ese buzón.

## Cómo se usa

```bash
cd ~/harvey && source .venv/bin/activate
harvey discover --provider dataforseo_maps --estimate   # cuánto costaría, sin gastar
harvey discover --provider dataforseo_maps              # buscar negocios
harvey dashboard                                        # panel en http://127.0.0.1:5555
harvey run                                              # que trabaje solo
```

En el panel, la pestaña **Outbox** es donde apruebas (A) o rechazas (R) cada correo antes de que salga.

## Pendientes antes de enviar de verdad

- Harvey solo acepta la línea de "no me escriba más" en inglés, así que la dejamos vacía y le pedimos al Writer que la ponga en español. En la prueba no la puso: revisa que cada correo la tenga antes de aprobarlo.
- `compliance.postal_address` está vacío. La ley de EE. UU. pide una dirección postal en correos en frío y nosotros enviamos desde allá: pon un apartado o buzón virtual.
- Para cambiar cómo escribe, edita `skills/product_knowledge.md` y corre `instalar.sh` otra vez.
