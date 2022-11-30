from commons.env_info import REDIS_HOST, REDIS_PORT

broker_url = f'redis://{REDIS_HOST}:{REDIS_PORT}/2'
result_backend = f'redis://{REDIS_HOST}:{REDIS_PORT}/2'

task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']

enable_utc = False

task_track_started = True
