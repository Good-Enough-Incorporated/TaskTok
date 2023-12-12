#!/bin/bash

source /home/jason/GEI/TaskTok/.venv/bin/activate

celery -A RemindMeClient.Client.celery_worker worker --loglevel=Info --beat
