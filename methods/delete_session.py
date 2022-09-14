"""
    Methods to return response for APIs
"""

from __future__ import annotations

import inspect
import logging
from datetime import datetime

from commons import env_info
from k8s import k8s_client

from commons.static_messages import SESSION_DELETED_SUCCESSFULLY, SESSION_NOT_DELETED
from helpers.utils import get_session_deleted_response, update_session, get_endpoint_api, upload_to_s3, \
    get_delete_type, retry_func
from helpers.utils import get_generated_urls

LOGGER = logging.getLogger('watchtower')


def delete_session(pod_name: str, session_id: str = None, request_id: str = None, delete_type: str = None, base_response = None):
    """
        :param : pod_name: name of k8s pod
        :type: pod_name: str
        :param : session_id: webdriver session_id from API URI
        :type: session_id: str
        :param : request_id: request_id from API URI
        :type: request_id: str
        :param : delete_type: type of deletion from API URI
        :type: delete_type: str
        :param : base_response:  Base Response object{data:{...}, msg:"...", status: ...}
        :type: base_response: json object
    """
    LOGGER.info(f"Function Name ==>> {inspect.stack()[0][3]}")
    LOGGER.debug(f"deleting pod name : {pod_name}")
    LOGGER.info(f"pod_name: {pod_name}, session_id: {session_id}, request_id: {request_id}, delete_type: {delete_type}")

    session_data = {}

    session_details_url, update_url = get_generated_urls(session_id=session_id, request_id=request_id)
    status_data = get_delete_type(delete_type=delete_type)

    try:
        pod = k8s_client.get_pod(namespace=env_info.ORG_NAME, pod_name=pod_name)
        pod_ip = k8s_client.get_pod_ip(pod)

        LOGGER.info(f"Pod Name: {pod_name} && Pod IP : {pod_ip}, session_id: {session_id}, request_id: {request_id}")

        LOGGER.info(f"/get-session-details api called with pod_name: {pod_name}")
        get_session_details_res = retry_func(func=get_endpoint_api,
                                             retry_limit=env_info.FUNC_RETRY_LIMIT,
                                             pause_time=env_info.FUNC_RETRY_PAUSE_TIME,
                                             url=session_details_url)

        if get_session_details_res.status_code == 200:
            get_session_details_res = get_session_details_res.json()
            session_data = get_session_details_res["data"]
            LOGGER.info(f"Session data from backend : {session_data}")

            if session_data["enable_video"]:
                LOGGER.info(f"/stop-recording api called with pod_name: {pod_name}")
                stop_recording_url = f"http://{pod_ip}:9092/stop-recording"

                start_time = datetime.now()

                recording_res = retry_func(func=get_endpoint_api,
                                           retry_limit=env_info.FUNC_RETRY_LIMIT,
                                           pause_time=env_info.FUNC_RETRY_PAUSE_TIME,
                                           url=stop_recording_url)
                total_time_diff = (datetime.now() - start_time).total_seconds()
                LOGGER.info(f"Total time for video to stop and upload : {total_time_diff}")

                if recording_res.status_code == 200:
                    LOGGER.info("Video recording successfully stopped.")
                else:
                    LOGGER.info("Couldn't stop video recorder.")
        LOGGER.info(get_session_details_res["msg"])

        if "enable_logs" in session_data and session_data["enable_logs"]:
            start_time = datetime.now()
            logs_data = k8s_client.get_pod_logs(namespace=env_info.ORG_NAME, pod_name=pod_name, container_name="browser")

            LOGGER.info(f"s3 put_object called for pod_name: {pod_name}")
            upload_to_s3(key=session_data["log_name"], data=logs_data)
            total_time_diff = (datetime.now() - start_time).total_seconds()
            LOGGER.info(f"Total time to fetch logs and upload : {total_time_diff}")

        LOGGER.info(f"Calling update_session. pod_name: {pod_name}")

        retry_func(func=update_session,
                   retry_limit=env_info.FUNC_RETRY_LIMIT,
                   pause_time=env_info.FUNC_RETRY_PAUSE_TIME,
                   url=update_url,
                   data=status_data)

        k8s_client.delete_pod(namespace=env_info.ORG_NAME, pod_name=pod_name)

        base_response.data = get_session_deleted_response()
        base_response.msg = SESSION_DELETED_SUCCESSFULLY
        LOGGER.info(f"session with pod name: {pod_name} successfully deleted.")

    except Exception as err:
        LOGGER.error(err)
        retry_func(func=update_session,
                   retry_limit=env_info.FUNC_RETRY_LIMIT,
                   pause_time=env_info.FUNC_RETRY_PAUSE_TIME,
                   url=update_url,
                   data=status_data)

        base_response.data = get_session_deleted_response()
        base_response.msg = SESSION_NOT_DELETED
        raise f"BaseException for pod_name: {pod_name}, session_id: {session_id}, request_id: {request_id}"
