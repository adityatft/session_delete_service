# Celery Configuration parameters
# Map to Redis server
from commons.env_info import DELETE_REDIS_HOST, DELETE_REDIS_PORT

broker_url = f'redis://{DELETE_REDIS_HOST}:{DELETE_REDIS_PORT}/0'
# broker_url = 'redis://127.0.0.1:6379/0'

# Backend used to store the tasks results
result_backend = f'redis://{DELETE_REDIS_HOST}:{DELETE_REDIS_PORT}/0'
# result_backend = 'redis://127.0.0.1:6379/0'

# A string identifying the default serialization to use Default json
task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']

# When set to false the local system timezone is used.
enable_utc = False

# To track the started state of a task, we should explicitly enable it
task_track_started = True

# Configure Celery to use a specific time zone.
# The timezone value can be any time zone supported by the pytz library
# timezone = 'Asia/Beirut'
# enable_utc = True
