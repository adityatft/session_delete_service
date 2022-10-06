"""
    Methods to return response for APIs
"""

from __future__ import annotations

import inspect

from flask import current_app
from commons import env_info
from k8s import k8s_client

from commons.static_messages import SESSION_DELETED_SUCCESSFULLY, SESSION_NOT_DELETED
from helpers.utils import get_session_deleted_response, update_session, get_delete_type, get_generated_urls, get_session_details
from tasks import background_video_k8s_pod_task


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
    current_app.logger.info(f"Function Name ==>> {inspect.stack()[0][3]}")
    current_app.logger.info(f"deleting pod name : {pod_name}")
    current_app.logger.info(f"pod_name: {pod_name}, session_id: {session_id}, request_id: {request_id}, delete_type: {delete_type}")

    session_data = {}

    session_details_url, update_url = get_generated_urls(session_id=session_id, request_id=request_id)
    status_data = get_delete_type(delete_type=delete_type)

    try:
        pod = k8s_client.get_pod(namespace=env_info.ORG_NAME, pod_name=pod_name)
        pod_ip = k8s_client.get_pod_ip(pod)

        current_app.logger.info(f"Pod Name: {pod_name} && Pod IP : {pod_ip}, session_id: {session_id}, request_id: {request_id}")

        current_app.logger.info(f"/get-session-details api called with pod_name: {pod_name}")
        get_session_details_res = get_session_details(url=session_details_url)

        if get_session_details_res.status_code == 200:
            get_session_details_res = get_session_details_res.json()
            session_data = get_session_details_res["data"]
            current_app.logger.info(f"Session data from backend : {session_data}")

        current_app.logger.info(get_session_details_res["msg"])

        data = {
            'session_data': session_data,
            'pod_ip': pod_ip,
            'pod_name': pod_name,
            # 'update_url': update_url,
            }
        background_video_k8s_pod_task.delay(data=data)

        current_app.logger.info(f"Calling update_session. pod_name: {pod_name}")
        update_session(url=update_url, data=status_data)

        base_response.data = get_session_deleted_response()
        base_response.msg = SESSION_DELETED_SUCCESSFULLY
        current_app.logger.info(f"session with pod name: {pod_name} successfully deleted.")

    except Exception as err:
        current_app.logger.error(err)
        update_session(url=update_url, data=status_data)

        base_response.data = get_session_deleted_response()
        base_response.msg = SESSION_NOT_DELETED
        raise f"BaseException for pod_name: {pod_name}, session_id: {session_id}, request_id: {request_id}"
