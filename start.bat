@echo off
set "VENV_DIR=%CD%\.venv"
set "PYTHON_EXEC=%VENV_DIR%\Scripts\python.exe"
set "CELERY_SCRIPT=%VENV_DIR%\Scripts\celery.exe"


cd /d %PROJECT_DIR%
start /b %PYTHON_EXEC% run.py
start /b %CELERY_SCRIPT% -A RemindMeClient.Client.celery worker --loglevel=DEBUG
wait
