@echo off
rem Inicia el Harvey de Plaza Gardenias (aparte del de Clientia).
rem Panel en http://127.0.0.1:5556. Sale del Gmail personal de Rodrigo, asi que las
rem respuestas le llegan directo a su bandeja: no hace falta avisos.py aqui.
cd /d C:\Users\rodri\harvey-plaza
set "SSL_CERT_FILE=C:\Users\rodri\harvey-plaza\.venv\Lib\site-packages\certifi\cacert.pem"
rem Si preguntan renta, precio o condiciones, Harvey no contesta: pasa a Rodrigo.
.venv\Scripts\python parches\precio_a_rodrigo.py .

netstat -ano | findstr /R /C:":5556 .*LISTENING" >nul
if errorlevel 1 start "Harvey Plaza panel" /min cmd /c ".venv\Scripts\harvey dashboard --port 5556 >> data\dashboard.log 2>> data\dashboard.err.log"

.venv\Scripts\harvey run >> data\run.log 2>> data\run.err.log
