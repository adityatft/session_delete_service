#!/bin/sh
set -e

./main & ./tasks tasks worker --loglevel=INFO --logfile=celery-logs.log
