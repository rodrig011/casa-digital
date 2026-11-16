# Con Sabor a Pueblo en Microsoft Azure (crédito de estudiante del GitHub Student Developer Pack)

DigitalOcean ya no viene en el pack (revisado el 16-nov-2026). Azure sí: **$100 de crédito y servicios gratis por 12 meses, sin tarjeta**.
Se usa **el mismo instalador** que en DigitalOcean (`instalar.sh` sirve para cualquier Ubuntu 24.04). Unos 30 minutos, **mejor desde la laptop**.

## 1. Activar Azure for Students (desde el 19 de noviembre de 2026)
1. En https://education.github.com/pack/offers busque **Microsoft Azure** y toque la oferta. O entre directo a https://azure.microsoft.com/free/students
2. Entre con su correo de Ivy Tech y siga los pasos. No pide tarjeta.
3. En https://portal.azure.com, busque **Subscriptions** y confirme que aparece **Azure for Students** con el crédito.

## 2. Crear la máquina virtual
En el portal: **Create a resource > Virtual machine** (o busque «Virtual machines» > **Create**).
- **Subscription:** Azure for Students. **Resource group:** *Create new* → `con-sabor-a-pueblo`.
- **Virtual machine name:** `con-sabor-a-pueblo`.
- **Region:** **(US) East US**. Si dice que no hay capacidad, pruebe East US 2 o South Central US.
- **Image:** **Ubuntu Server 24.04 LTS - x64 Gen2**.
- **Size:** **B1s** (1 vCPU, 1 GiB). Tiene que decir que entra en el plan gratis (*free services eligible*). Si no aparece, use **B1ms**, que se paga del crédito.
- **Authentication type:** **Password**. Usuario `azureuser` y una contraseña larga. Guárdela en su gestor de contraseñas (1Password también viene gratis en el pack).
- **Inbound ports:** marque **SSH (22)**, **HTTP (80)** y **HTTPS (443)**.
- **Disks:** **Standard SSD**, 30 GB (el tamaño gratis es de 64 GB).
- **Management:** active **Auto-shutdown = Off**. Si se apaga sola, el bot deja de contestar.

Toque **Review + create > Create**. En 1 o 2 minutos aparece la **Public IP address** de la máquina. Cópiela.

## 3. Instalar (un solo comando)
1. En el portal, arriba a la derecha, toque el ícono **>_ (Cloud Shell)**. Escoja **Bash**. Si pregunta por almacenamiento, acepte lo que propone.
2. Conéctese a la máquina (cambie la IP por la suya). Pide la contraseña del paso 2 y, la primera vez, que escriba `yes`:
   ```
   ssh azureuser@20.1.2.3
   ```
3. Pegue esto y Enter:
   ```
   curl -fsSL https://raw.githubusercontent.com/rodrig011/casa-digital/main/con-sabor-a-pueblo/droplet/instalar.sh | sudo bash
   ```
4. Tarda unos 5 minutos. Al final dice `✓ El bot está corriendo.` y le da la dirección del panel, del tipo `https://20-1-2-3.sslip.io/panel`.

## 4. Dejarlo listo
Igual que en [README.md](README.md) paso 4, pero cada orden con `sudo` adelante:
```
sudo con-sabor editar
sudo con-sabor usuario agregar su@correo.com "Rodrigo" 504XXXXXXXX
sudo con-sabor revisar
sudo con-sabor llave
```

## IP fija (importante)
En el portal: máquina > **Networking** > la IP pública > **Configuration** > **Assignment: Static** > Save.
Si no lo hace, la IP puede cambiar al reiniciar y el panel y el webhook de Meta dejan de funcionar.

## Lo que cuesta
- **Mientras dure Azure for Students (12 meses):** la B1s y el disco entran en lo gratis. La IP pública cuesta unos $3-4 al mes, que salen de los $100 de crédito. Total para usted: $0.
- **Si se acaba el crédito o pasan los 12 meses:** Azure apaga la máquina en vez de cobrarle. Unas semanas antes, pásela a pago por uso (unos $10 al mes) o múdese a Render con la guía principal. Los datos se mueven con `respaldo.js`.
- Para ver el gasto: portal > **Cost Management**. Ponga una alerta en **Budgets**, por ejemplo $10.

## Si algo falla
- **No abre el panel:** revise en la máquina > **Networking** que estén abiertos los puertos 80 y 443. Luego `sudo con-sabor estado`.
- **`ssh` no conecta:** revise que la máquina esté en **Running** y que el puerto 22 esté abierto.
- Todo lo demás: la sección «Si algo falla» de [README.md](README.md).
