# Harvey de Plaza Gardenias

Un Harvey aparte del de Clientia, solo para conseguir inquilinos para Plaza Gardenias (Talanga). Escribe desde el Gmail personal de Rodrigo (rodrigoherreraarita@gmail.com) mientras la plaza no tenga dominio, en español y de usted, nunca menciona renta ni condiciones, y **ningún correo sale sin que lo apruebes**. Si alguien pregunta precio, renta o condiciones, Harvey no contesta: la respuesta te llega directo a tu Gmail y la contestás vos.

No se mezcla con el de Clientia: otra carpeta (`C:\Users\rodri\harvey-plaza`), otra base de datos, otro buzón y otro panel (http://127.0.0.1:5556; el de Clientia sigue en 5555).

## Qué trae

| Archivo | Para qué |
|---|---|
| `harvey.local.yaml` | Configuración: datos de la plaza, 3 correos el primer día y +2 por día hasta 10, aprobación obligatoria, Intur y ACCIVAL en la lista de no contactar |
| `skills/product_knowledge.md` | Lo que Harvey puede y no puede decir de la plaza |
| `entrada/franquicias.csv` | Cadenas y franquicias de Honduras. Las que tienen correo se cargan en Harvey; las que no, son para WhatsApp o llamada |
| `cargar_prospectos.py` | Carga el CSV en Harvey |
| `iniciar-harvey-plaza.cmd` | Arranca el panel y Harvey |
| `instalar.sh` | Instala todo en `~/harvey-plaza` con la misma versión y parches que el Harvey de Clientia |

## Instalar (en la PC de Rodrigo)

1. `bash harvey/plaza-gardenias/instalar.sh` desde la carpeta `casa-digital`.
2. En la cuenta de Google: activar la verificación en dos pasos y crear una **contraseña de aplicación** (myaccount.google.com/apppasswords). En Gmail, Configuración > Reenvío y POP/IMAP: IMAP activado.
3. En `C:\Users\rodri\harvey-plaza\.env`, Rodrigo escribe: `SMTP_HOST=smtp.gmail.com`, `SMTP_PORT=587`, `SMTP_USERNAME=rodrigoherreraarita@gmail.com`, `SMTP_PASSWORD=<contraseña de aplicación>`, `IMAP_HOST=imap.gmail.com`. Nadie más escribe la contraseña.
4. `.venv\Scripts\python cargar_prospectos.py entrada\franquicias.csv`
5. `iniciar-harvey-plaza.cmd`. Los borradores aparecen en el Outbox del panel (puerto 5556) para aprobar.

## Agregar más prospectos

Agregar filas a `entrada/franquicias.csv` (solo correos que aparezcan en la página de la empresa) y volver a correr el paso 4. No duplica.
