@echo off
rem Inicia Harvey con los certificados de certifi (sin esto, SMTP falla con
rem CERTIFICATE_VERIFY_FAILED), abre el panel si no esta abierto y arranca
rem los avisos al celular (avisos.py: correo a Rodrigo cuando alguien responde o pide precio).
cd /d C:\Users\rodri\harvey
set "SSL_CERT_FILE=C:\Users\rodri\harvey\.venv\Lib\site-packages\certifi\cacert.pem"
rem Si un prospecto pide precio, Harvey no contesta: pasa a Rodrigo (ver parches\precio_a_rodrigo.py).
.venv\Scripts\python parches\precio_a_rodrigo.py .

netstat -ano | findstr /R /C:":5555 .*LISTENING" >nul
if errorlevel 1 start "Harvey panel" /min cmd /c ".venv\Scripts\harvey dashboard >> data\dashboard.log 2>> data\dashboard.err.log"

start "Harvey avisos" /min cmd /c ".venv\Scripts\python avisos.py >> data\avisos.log 2>> data\avisos.err.log"

.venv\Scripts\harvey run >> data\run.log 2>> data\run.err.log
