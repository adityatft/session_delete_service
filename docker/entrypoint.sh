#!/bin/sh
set -e

#watch date
./main & celery -A tasks worker --loglevel=INFO --logfile=celery-logs.log
python main.py & celery -A tasks worker --loglevel=INFO --logfile=celery-logs.log
