# Con Sabor a Pueblo: poner el bot en vivo (guía para hacerlo solo)

Esta guía se sigue sin ayuda, en orden. Cada paso dice dónde hacer clic, qué copiar y dónde pegarlo, cómo saber que
quedó bien y qué hacer si falla. **Las claves nunca se pegan en un chat, en un correo ni en GitHub: solo en Render.**

Tiempo total: unas 3 horas de usted, más una videollamada de 45 minutos con el dueño.

| Parte | Quién | Cuánto tarda | Costo |
|---|---|---|---|
| 1. Cuentas (Claude, Render, Meta) | Usted | 40 min | $10 de crédito de Claude |
| 2. Servidor en Render | Usted | 15 min | ~$7.25 al mes |
| 3. Prueba con el número de prueba de Meta | Usted y un amigo | 1 hora | Gratis |
| 4. Videollamada con el dueño: su Meta y su número | Usted y el dueño | 45 min | Una línea nueva (~L50) si hace falta |
| 5. Prender el bot | Usted | 30 min | Gratis |

Lo que ya está hecho y probado (46 pruebas automáticas): el bot con IA, pedidos a cocina, apartados con tope,
pago con comprobante, repartidores con ubicación, panel del dueño con menú, equipo y configuración editables,
respaldo cifrado y el chequeo `npm run revisar`.

**¿Servidor en DigitalOcean con el crédito de estudiante en vez de Render?** Siga [`droplet/README.md`](droplet/README.md) en lugar de la Parte 2. El resto de esta guía es igual.

## Atajo: el panel real hoy, sin esperar a Meta (20 minutos)

El panel de verdad (no la demo) corre en el mismo servidor y **no necesita WhatsApp para funcionar**. Si Meta todavía no
lo deja (por ejemplo, «You can't make this change at the moment» por usar un aparato nuevo), suba el servidor ya y que el
dueño empiece a usar el panel: deja listo el menú con sus precios, los apartados, los pagos, los horarios y su equipo de
reparto. Todo queda guardado en el disco y el bot lo usa desde el primer mensaje cuando se conecte WhatsApp.

1. Haga el paso **1.2 (Render)**.
2. Haga la **Parte 2** con estas diferencias:
   - `META_TOKEN`, `META_PHONE_ID`, `META_NUMERO`, `META_APP_SECRET`, `META_PLANTILLA`, `META_PLANTILLA_CODIGO`: **vacíos**.
   - `ANTHROPIC_API_KEY`: vacía por ahora (sin WhatsApp no se usa; así no gasta).
   - `NEGOCIO_PRIVADO`: el JSON completo del archivo privado. Sin WhatsApp no sale ningún mensaje a nadie.
   - `OWNER_WHATSAPP`: el del dueño, o vacío.
   - `npm run revisar` va a marcar ✗ en lo de Meta (y en `OWNER_WHATSAPP` si lo dejó vacío): es lo esperado en este atajo. Lo demás debe salir ✓ o !.
3. Agregue los usuarios como en **2.2**, con su WhatsApp. Mientras no haya WhatsApp conectado se entra solo con correo
   y contraseña; cuando se conecte, el código de entrada empieza a llegar solo.
4. Abra `https://con-sabor-a-pueblo-bot.onrender.com/panel`. Arriba, en **Hoy** y en **Configuración**, dice
   «WhatsApp todavía no está conectado». Eso desaparece solo cuando se conecta.
5. Con el dueño (puede ser por videollamada): que revise **Menú** (precios), **Configuración** (máximo de apartados,
   hora de cierre, cuenta para depósitos, horario) y **Repartidores**.

Cuando Meta ya lo deje: pegue los valores de Meta y la clave de Claude en Render > **Environment** (Render reinicia solo,
los datos del disco se quedan) y siga desde **2.1**.

---

## Parte 1. Cuentas (una sola vez)

### 1.1 Claude (la IA)
1. Entre a **console.anthropic.com** con el correo de Clientia Tech.
2. **Settings > Billing > Add credits**: compre $10.
3. **Settings > Limits**: ponga un límite de gasto de **$20 al mes**. Así nunca le cobra de más.
4. **API Keys > Create Key**, nombre `con-sabor-a-pueblo`. Copie la clave (empieza con `sk-ant-`). Solo se ve una vez: péguela directo en Render en la Parte 2. Si la pierde, borre esa y cree otra.

### 1.2 Render (el servidor)
1. Entre a **dashboard.render.com** con su GitHub (rodrig011).
2. **Account Settings > Billing**: agregue una tarjeta.
3. Active la verificación en dos pasos en **Account Settings > Security**.

### 1.3 Meta (WhatsApp)
1. Entre a **developers.facebook.com** con su Facebook y toque **Comenzar / Get Started**. Si Meta no lo aprueba como desarrollador, que lo haga **Dylan** con su Facebook y le comparta acceso a la app. El resto de la guía es igual.
2. **Mis apps > Crear app**. Caso de uso: **Otro**. Tipo: **Negocio**. Nombre: `Con Sabor a Pueblo bot`.
3. En el panel de la app, en **Agregar productos**, busque **WhatsApp** y toque **Configurar**.
4. Meta le crea un **número de prueba gratis**. Lo va a usar en la Parte 3.
5. **Configuración de la app > Básica > Clave secreta de la app > Mostrar**. Es `META_APP_SECRET` (32 letras y números). Cópiela directo a Render en la Parte 2.

---

## Parte 2. Servidor en Render

1. En Render: **New + > Blueprint**.
2. Escoja el repositorio **rodrig011/casa-digital**.
3. En **Blueprint Path** escriba: `con-sabor-a-pueblo/render-produccion.yaml`
4. Render muestra el servicio **con-sabor-a-pueblo-bot** con un disco de 1 GB y le pide los valores que no están en el archivo. Llénelos así:

| Variable | Qué poner | De dónde sale |
|---|---|---|
| `NEGOCIO_PRIVADO` | El JSON del archivo privado del proyecto | `/mnt/project-files/restaurantes/con-sabor-a-pueblo/privado/datos-privados.md`, el bloque que empieza con `{"sucursales"`. Para la prueba de la Parte 3, deje los WhatsApp de sucursales y repartidores **vacíos** (`""`) para no escribirle a nadie real. |
| `META_TOKEN` | El token temporal | Meta > su app > WhatsApp > **Configuración de la API** > Token de acceso temporal (dura 24 horas; en la Parte 5 se cambia por uno permanente) |
| `META_PHONE_ID` | El identificador del número | Misma pantalla: **Identificador del número de teléfono** (un número largo, no el teléfono) |
| `META_NUMERO` | El número de prueba de Meta | Misma pantalla, con `+1` adelante |
| `META_APP_SECRET` | La clave secreta | Paso 1.3.5 |
| `META_PLANTILLA`, `META_PLANTILLA_CODIGO` | Vacío por ahora | Parte 5 |
| `OWNER_WHATSAPP` | **Su** celular para la prueba, con código de país | Usted hace de dueño en la prueba. En la Parte 5 se cambia por el del dueño |
| `PUBLIC_URL` | `https://con-sabor-a-pueblo-bot.onrender.com` | Si Render le pone otro nombre, use el que aparece arriba en el servicio |
| `ANTHROPIC_API_KEY` | La clave de Claude | Paso 1.1.4 |

5. Toque **Apply**. Espere a que diga **Live** (unos 3 minutos).
6. **Guarde una copia de `DATA_KEY`**: servicio > **Environment** > `DATA_KEY` > ojo > cópiela a su gestor de contraseñas. Sin esa llave no se abren los pedidos guardados.

**Cómo saber que quedó bien:**
- Abra `https://con-sabor-a-pueblo-bot.onrender.com/` en el navegador: dice `Con Sabor a Pueblo · bot activo`.
- Servicio > **Shell**, escriba `npm run revisar -- --en-linea` y Enter. Todo debe salir con ✓ salvo los avisos de plantilla y de usuarios del panel. Cada ✗ dice qué hacer.

**Si falla:**
- El servicio no arranca: **Logs**. Si dice `Falta DATA_KEY`, revise que exista en Environment. Si dice `Revise el archivo del negocio`, el JSON de `NEGOCIO_PRIVADO` está mal copiado: péguelo otra vez completo.
- `npm run revisar` dice que Meta no acepta el token: el temporal venció (24 h). Copie uno nuevo en Meta y péguelo en Environment (Render reinicia solo).

### 2.1 Conectar el webhook (Meta le avisa al bot cada mensaje)
1. Meta > su app > **WhatsApp > Configuración** > **Webhook > Editar**.
2. **URL de devolución de llamada**: `https://con-sabor-a-pueblo-bot.onrender.com/meta`
3. **Token de verificación**: el valor de `META_VERIFY_TOKEN` (Render > Environment > ojo).
4. **Verificar y guardar**. Si sale error, revise que el servicio esté **Live** y que copió el token sin espacios.
5. En **Campos del webhook**, active **messages** (Suscribirse).

### 2.2 Usuarios del panel
En Render > Shell, por cada persona:
```
npm run usuario -- agregar correo@ejemplo.com "Nombre" 504XXXXXXXX
```
Le pide una contraseña de al menos 10 caracteres (no se ve al escribir). El número de WhatsApp es para el código de entrada.
Para la prueba, agréguese usted. El panel está en `https://con-sabor-a-pueblo-bot.onrender.com/panel`.

---

## Parte 3. Prueba con el número de prueba de Meta (antes de tocar el número del negocio)

1. Meta > WhatsApp > Configuración de la API > **Para**: agregue su celular y el de un amigo (Meta les manda un código). Máximo 5 números.
2. Desde el celular del amigo (hace de cliente), escríbale **hola** al número de prueba. Debe contestar en menos de 10 segundos.
3. Haga un pedido completo como cliente, con sus palabras: «quiero 2 cerditos para recoger en San Pedro el sábado, a nombre de Ana».
4. Revise cada punto y márquelo:
   - [ ] Contesta el saludo y entiende el pedido.
   - [ ] Da número de pedido y total, y pide el comprobante.
   - [ ] Al mandar una foto como comprobante, a su celular (dueño) le llega el aviso.
   - [ ] Contesta **OK 1001** (con el número del pedido) desde su celular: al cliente le llega la confirmación.
   - [ ] El pedido aparece en el panel. Márquelo **Listo**: al cliente le llega el aviso.
   - [ ] Un pedido **a domicilio**: el bot pide la ubicación de WhatsApp.
   - [ ] En el panel > Configuración, ponga **pausa** y escriba desde el cliente: contesta el mensaje de pausa. Quite la pausa.
   - [ ] En Render > Environment ponga `BOT_IA=off`: contesta con el menú de opciones. Vuelva a ponerlo en `on`.
5. Si algo sale mal, **Logs** muestra `[meta]` o `[ia]` con el error. Anótelo con la hora.

---

## Parte 4. Videollamada con el dueño (45 minutos)

**Antes de la llamada, pídale por WhatsApp:**
- Foto del **RTN** y de un **recibo de luz o agua** del negocio.
- Su **WhatsApp personal** para los avisos.
- El precio en Tegucigalpa, si el tope de 50 apartados es por ciudad, y el WhatsApp y la ciudad de cada repartidor.
- Los correos de quienes van a entrar al panel.

**El número.** Con una app propia como esta, Meta solo acepta un número que **no** esté en WhatsApp. Por eso:
- **Recomendado:** una **línea nueva** (un chip Tigo o Claro) solo para pedidos. El 3169-9031 sigue igual en su celular y en la bio de TikTok se pone «pedidos por WhatsApp al nuevo número».
- **Usar el 3169-9031:** hay que borrar esa cuenta de WhatsApp Business del celular (se pierden los chats) antes de pasarlo a Meta. Solo si el dueño lo pide sabiendo eso.

**En la llamada:**
1. El dueño entra a **business.facebook.com** con su Facebook (si no tiene cuenta de negocio, la crea: nombre del negocio, su nombre, su correo).
2. **Configuración > Usuarios > Personas > Agregar**: su correo, con **acceso total / administrador**. Usted acepta la invitación desde su correo.
3. Usted, en developers.facebook.com > su app > **Configuración de la app > Básica**: en **Portfolio comercial / Business portfolio** escoja el Meta Business de Con Sabor a Pueblo.
4. WhatsApp > Configuración de la API > **Agregar número de teléfono**: nombre visible `Con Sabor a Pueblo`, categoría **Restaurante**, el número escogido. Meta manda un **código por SMS o llamada** a ese número: el dueño se lo lee.
5. **Centro de seguridad > Verificación del negocio**: suba el RTN y el recibo. Meta tarda de días a 2 semanas; el bot funciona mientras tanto.
6. **WhatsApp Manager > Configuración > Método de pago**: una tarjeta (de Clientia Tech o del dueño). Solo cobra las plantillas, centavos.

---

## Parte 5. Prender el bot con el número del negocio

### 5.1 Token permanente (el temporal vence en 24 horas)
1. business.facebook.com (del negocio) > **Configuración > Usuarios > Usuarios del sistema > Agregar**: nombre `bot`, rol **Administrador**.
2. **Asignar activos**: la app `Con Sabor a Pueblo bot` (control total) y la **cuenta de WhatsApp** (control total).
3. **Generar nuevo token**: escoja la app, caducidad **Nunca**, permisos `whatsapp_business_messaging` y `whatsapp_business_management`. Copie el token directo a Render > Environment > `META_TOKEN`.

### 5.2 Cambiar a los datos reales en Render > Environment
| Variable | Valor nuevo |
|---|---|
| `META_PHONE_ID` | El identificador del número del negocio (Configuración de la API, escogiendo ese número) |
| `META_NUMERO` | El número del negocio, `+504 ...` |
| `OWNER_WHATSAPP` | El WhatsApp personal del dueño |
| `NEGOCIO_PRIVADO` | El JSON completo del archivo privado, ya con los WhatsApp de sucursales y repartidores que confirmó el dueño |

Guarde. Render reinicia solo. Luego en Shell: `npm run revisar -- --en-linea`. Debe decir `Meta contesta: número +504 ...`.

### 5.3 Plantillas (para avisar al dueño aunque no le haya escrito en 24 horas)
WhatsApp Manager > **Plantillas de mensajes > Crear plantilla**:
1. Categoría **Utilidad**, nombre `aviso_pedido`, idioma **Español**. Cuerpo:
   `Aviso de su negocio: {{1}}. Detalle: {{2}}`
   Ejemplos: `Pedido nuevo PED-1001` y `2 cerditos · San Pedro Sula`. Enviar.
2. Categoría **Autenticación**, nombre `codigo_panel`, idioma **Español**, botón **Copiar código**. Enviar.
3. Cuando Meta las apruebe (minutos u horas), ponga `META_PLANTILLA=aviso_pedido` y `META_PLANTILLA_CODIGO=codigo_panel` en Render.

### 5.4 Usuarios del dueño y prueba final
1. Render > Shell: `npm run usuario -- agregar <correo del dueño> "Nombre" 504XXXXXXXX` (una contraseña temporal que le manda por WhatsApp). Quítese usted si no va a entrar: `npm run usuario -- quitar su@correo`.
2. Desde **su** celular (no el de un cliente), escríbale **hola** al número del negocio y haga un pedido de prueba. Cancélelo en el panel.
3. Con el dueño en llamada, entre al panel en su celular y muéstrele **Hoy, Pedidos, Cocina, Menú y Configuración**.
4. Que el dueño revise **Menú** (precios) y **Configuración** (máximo de apartados, hora de cierre, cuenta para transferencia).
5. Cambie la bio de TikTok y Facebook con el número de pedidos.

---

## Día a día

| Qué | Cómo |
|---|---|
| Un día no abren | Panel > Configuración > Recibir pedidos: apagado, con su mensaje |
| La IA contesta mal | Render > Environment > `BOT_IA=off` (contesta con el menú) y anote el chat para corregirlo |
| Respaldo semanal | En su computadora, dentro de `bot-restaurante`: `LEADS_TOKEN=<de Render> node respaldo.js bajar https://con-sabor-a-pueblo-bot.onrender.com`. Guarde el archivo junto con la copia de `DATA_KEY` |
| Ver qué pasó | Render > Logs, y en el panel > Seguridad (quién entró y qué cambió) |
| Revisar todo | Render > Shell > `npm run revisar -- --en-linea` |
| Gasto de Claude | console.anthropic.com > Usage. El tope diario por número es `LIMITE_IA_DIA` (60) |

## Si algo falla

| Síntoma | Causa probable | Arreglo |
|---|---|---|
| El bot no contesta nada | Webhook sin `messages`, token vencido o servicio caído | Revise el paso 2.1, `npm run revisar -- --en-linea` y Logs |
| Logs dice `firma inválida` | `META_APP_SECRET` mal copiado | Cópielo otra vez desde Configuración de la app > Básica |
| Logs dice `131047` | Pasaron 24 horas sin que esa persona escriba | Cree y ponga `META_PLANTILLA` (5.3) |
| Logs dice `190` o `token` | El token venció | Token permanente (5.1) |
| Contesta solo con el menú | Sin crédito en Claude o `BOT_IA=off` | Billing en console.anthropic.com; `BOT_IA=on` |
| El dueño no recibe el código del panel | Sin plantilla de código y no ha escrito en 24 horas | Que le escriba «hola» al bot y vuelva a entrar; o apruebe `codigo_panel` |
| Después de reiniciar no hay pedidos | Cambió `DATA_KEY` o se quitó el disco | Ponga la `DATA_KEY` guardada; revise Disks |

## Costo mensual por cliente (estimado)

| Qué | Costo |
|---|---|
| Render (plan con disco) | ~$7.25 |
| Claude (Haiku, con tope diario) | ~$10 a $15 |
| WhatsApp (Meta) | casi $0: contestar a quien escribió primero es gratis; las plantillas cuestan centavos |
| **Total** | **~$20 a $25 al mes**, frente a L2,500 que paga el cliente |
