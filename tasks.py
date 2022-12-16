import json
import requests
import watchtower
import logging
import os

from celery import Celery
# import env_file

# try:
#     env_file.load(".env")
# except Exception as err:
#     pass

ORG_NAME = os.environ.get("ORG_NAME")
LOG_GROUP_NAME = os.environ.get("LOG_GROUP_NAME")
LOG_FORMAT = os.environ.get("LOG_FORMAT")
HEADERS = {
    "Content-Type": "application/json"
}
BASE_URL = "http://" + os.environ.get("HOST") + ":" + os.environ.get("PORT")
REDIS_HOST = os.environ.get("ORG_REDIS_HOST")
REDIS_PORT = int(os.environ.get("ORG_REDIS_PORT"))


celery = Celery(
    name = "tasks",
    broker_url = f'redis://{REDIS_HOST}:{REDIS_PORT}/2',
    result_backend = f'redis://{REDIS_HOST}:{REDIS_PORT}/2',
    task_serializer = 'json',
    result_serializer = 'json',
    accept_content = ['json'],
    enable_utc = False,
    task_track_started = True
    )

logger = logging.getLogger(__name__)
handler = watchtower.CloudWatchLogHandler(log_group_name=LOG_GROUP_NAME, log_stream_name=ORG_NAME)
handler.setFormatter(
    logging.Formatter(fmt=LOG_FORMAT)
    )
logger.addHandler(handler)


@celery.task(name='tasks.background_video_k8s_pod_task')
def background_video_k8s_pod_task(data, request_id):

    logger.info(f"Celery task background_video_k8s_pod_task recieved for pod {data['pod_name']}", extra={"request_id": request_id})
    video_log_url = f"{BASE_URL}/api/v1/save_video_log_k8d_pods"

    payload = json.dumps(data)

    logger.info(f"Video log save url is {video_log_url}", extra={"request_id": request_id})
    logger.info(f"Calling save_video_log_k8d_pods_handler API with payload {payload}", extra={"request_id": request_id})
    requests.post(url=video_log_url, headers=HEADERS, data=payload)

    logger.info(f"Background task background_video_k8s_pod_task successfully completed for pod {data['pod_name']}", extra={"request_id": request_id})

if __name__ == "__main__":

    worker = celery.Worker()
    worker.start()