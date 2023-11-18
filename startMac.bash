#!/bin/bash

# Set the virtual environment and script paths
VENV_DIR="$PWD/.venv"
PYTHON_EXEC="$VENV_DIR/bin/python"
CELERY_SCRIPT="$VENV_DIR/bin/celery"

# Navigate to the project directory (if different from the current directory)
cd "$PROJECT_DIR"

# Start the Python application and Celery in the background, while Redis starts.
"$PYTHON_EXEC" run.py &
"$CELERY_SCRIPT" -A RemindMeClient.Client.celery worker --loglevel=DEBUG &
redis-server

# Wait for the background processes to finish
wait