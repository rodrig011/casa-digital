# Con Sabor a Pueblo en DigitalOcean (con el crédito de estudiante)

Es la alternativa a Render. Con el crédito del GitHub Student Developer Pack, el servidor sale gratis mientras dure el crédito.
Después cuesta unos $7.20 al mes ($6 del Droplet más $1.20 de respaldos). Se hace una sola vez, en unos 25 minutos, **mejor desde la laptop**.

**Use Render o DigitalOcean, no los dos.** Con DigitalOcean no se crea nada en Render para el bot de Con Sabor a Pueblo.

## 1. Cobrar el crédito (desde el 19 de noviembre de 2026)
1. Entre a https://education.github.com/pack/offers y busque **DigitalOcean**.
2. Toque el enlace de la oferta y cree la cuenta de DigitalOcean desde ahí, para que se aplique el crédito.
3. En DigitalOcean > **Billing** confirme que aparece el crédito. Puede pedir una tarjeta para verificar: no cobra mientras haya crédito.
4. **Settings > Security**: active la verificación en dos pasos.

## 2. Crear el Droplet (el servidor)
**Create > Droplets** y escoja:
- **Region:** New York (NYC1). Atlanta también sirve si aparece.
- **Image:** Ubuntu **24.04 (LTS)**.
- **Size:** Basic > Regular > **$6/mes (1 GB / 1 CPU)**.
- **Authentication:** **Password**. Use una contraseña larga y guárdela en su gestor de contraseñas.
- **Backups:** actívelos (semanales). Si el servidor se daña, se restaura con un clic.
- **Hostname:** `con-sabor-a-pueblo`.

Toque **Create Droplet** y espere a que salga su IP (unos 30 segundos).

## 3. Instalar (un solo comando)
1. Abra el Droplet y toque **Console** (se abre una terminal en el navegador; ya entra como root).
2. Pegue esto y Enter:
   ```
   curl -fsSL https://raw.githubusercontent.com/rodrig011/casa-digital/main/con-sabor-a-pueblo/droplet/instalar.sh | bash
   ```
3. Tarda unos 5 minutos. Al final dice `✓ El bot está corriendo.` y le da la dirección del panel. Es algo como
   `https://164-90-1-2.sslip.io/panel` (su IP con guiones). El HTTPS es real y gratis, no hace falta comprar dominio.

Si después quiere `bot.clientiatech.com`: en Namecheap cree un registro **A** `bot` con la IP del Droplet y vuelva a correr
el instalador con el dominio al final (`... | bash -s -- bot.clientiatech.com`). Luego, en `con-sabor editar`, cambie
`PUBLIC_URL` a `https://bot.clientiatech.com`.

## 4. Dejarlo listo (en la misma consola)
```
con-sabor editar
```
Se abre el archivo de configuración. Baje con las flechas hasta `NEGOCIO_PRIVADO=` y pegue el JSON del archivo privado
del proyecto (`restaurantes/con-sabor-a-pueblo/privado/datos-privados.md`, el bloque que empieza con `{"sucursales"`),
**entre comillas simples**: `NEGOCIO_PRIVADO='{"sucursales":...}'`. Guarde con **Ctrl+O**, Enter, y salga con **Ctrl+X**. Se reinicia solo.

```
con-sabor usuario agregar su@correo.com "Rodrigo" 504XXXXXXXX
con-sabor revisar
con-sabor llave
```
- `usuario agregar` le pide una contraseña de al menos 10 caracteres (no se ve al escribir).
- `revisar` marca ✗ en lo de Meta mientras WhatsApp no esté conectado. Es lo esperado.
- `llave` muestra `DATA_KEY`. **Cópiela a su gestor de contraseñas.** Sin ella no se abren los pedidos guardados.

Abra el panel. Mientras no haya WhatsApp se entra con correo y contraseña, y arriba dice «WhatsApp todavía no está conectado».

## 5. Cuando Meta ya lo deje
`con-sabor editar` y llene `META_TOKEN`, `META_PHONE_ID`, `META_NUMERO`, `META_APP_SECRET`, `OWNER_WHATSAPP` y
`ANTHROPIC_API_KEY`. Luego siga la guía principal (`con-sabor-a-pueblo/PUESTA-EN-MARCHA.md`) desde **2.1 Conectar el webhook**.
La URL del webhook es la de su panel cambiando `/panel` por `/meta`. El token de verificación es el `META_VERIFY_TOKEN`
que está en `con-sabor editar`.

## Día a día
| Para | Escriba en la consola |
|---|---|
| Ver si está corriendo | `con-sabor estado` |
| Ver qué pasó (errores) | `con-sabor logs` |
| Bajar la última versión del bot | `con-sabor actualizar` |
| Cambiar claves o datos privados | `con-sabor editar` |
| Agregar o quitar a alguien del panel | `con-sabor usuario agregar ...` / `con-sabor usuario quitar correo` |
| Todas las órdenes | `con-sabor` |

Lo que el servidor ya hace solo: se levanta si se cae o se reinicia, renueva el HTTPS, instala los parches de seguridad
de Ubuntu, bloquea todo menos la web y SSH, y guarda los datos cifrados con `DATA_KEY`. Los respaldos los hace DigitalOcean (paso 2).

## Si algo falla
- **El panel no abre:** `con-sabor estado`. Si dice `failed`, vea `con-sabor logs`. Un error como `Revise el archivo del negocio` es casi siempre el JSON de `NEGOCIO_PRIVADO` mal pegado (le faltan las comillas simples o le falta un pedazo).
- **El navegador dice que el sitio no es seguro:** espere un minuto la primera vez. Si sigue igual, revise que el puerto 80 no lo bloquee un *Cloud Firewall* de DigitalOcean.
- **Se acabó el crédito:** DigitalOcean empieza a cobrar a la tarjeta (unos $7.20 al mes). No hay que mover nada.
