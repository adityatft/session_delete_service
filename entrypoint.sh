#!/bin/sh
set -e


#watch date
python main.py & celery -A tasks worker --loglevel=INFO --logfile=celery-logs.log