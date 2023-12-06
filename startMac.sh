#!/bin/bash

# Set the virtual environment and script paths
VENV_DIR="$PWD/.venv"
PYTHON_EXEC="$VENV_DIR/bin/python"
CELERY_SCRIPT="$VENV_DIR/bin/celery"
REDIS_LOCATION="/opt/homebrew"
# Navigate to the project directory (if different from the current directory)
cd "$PROJECT_DIR"
source $PWD/.venv/bin/activate

echo "Starting redis-server"
redis-server $REDIS_LOCATION/etc/redis.conf &
# Start the Python application and Celery in the background, while Redis starts.

"$CELERY_SCRIPT" -A RemindMeClient.Client.celery_worker worker --loglevel=info &
"$PYTHON_EXEC" app.py


# Wait for the background processes to finish
wait
