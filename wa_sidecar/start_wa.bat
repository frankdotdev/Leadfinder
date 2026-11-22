@echo off
cd /d "%~dp0"
if not exist "node_modules" (
  echo Installing Baileys WhatsApp Sidecar dependencies...
  call npm install
)
echo Starting LeadFinder WhatsApp Sidecar on http://127.0.0.1:3001 ...
node server.js
pause
