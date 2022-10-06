import inspect
from celery import Celery

from helpers.utils import save_video_log_k8d_pods

# Set up the celery client
celery = Celery(__name__)
# Load celery configurations from celeryconfig.py
celery.config_from_object("celeryconfig")


@celery.task(name='tasks.background_video_k8s_pod_task')
def background_video_k8s_pod_task(data):
    print(f"Function Name ==>> {inspect.stack()[0][3]}")
    save_video_log_k8d_pods(data=data)