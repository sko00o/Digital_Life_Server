@echo off
set SCRIPT_NAME=SocketServer.py
set PROXY=http://127.0.0.1:7890
set STREAM=False
set CHARACTER=paimon

set APIBASE=
set APIKEY=xxx
set MODEL=chatgpt-3.5

.\venv\Scripts\python.exe %SCRIPT_NAME% --stream %STREAM% --character %CHARACTER% --model %MODEL% --proxy %PROXY% --APIKey %APIKEY% --APIBase %APIBASE%
