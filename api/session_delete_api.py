"""
    Session Manager DELETE API Endpoints
"""

from __future__ import annotations

import logging
from flask import Blueprint

from commons.base_response import BaseResponse
from methods.delete_session import delete_session

LOGGER = logging.getLogger('watchtower')

session_blueprint = Blueprint("session_blueprint", __name__)


@session_blueprint.route('/api/v1/session/<string:pod_name>/<string:session_id>/<string:delete_type>', methods=['DELETE'])
def delete_session_handler(pod_name=None, session_id=None, delete_type=None):
    """
        API(DELETE) to delete sessions and delete k8s pod.

        :param: pod_name: It contains unique user id.
        :type: pod_name: str
        :param: session_id: It contains unique org id.
        :type: session_id: str
        :param: delete_type: It contains unique org id.
        :type: delete_type: str

        :return: data:{...}, status_code: {...}
        :rtype: response dict , status code
    """
    base_response = BaseResponse()

    try:
        if "firefox" in pod_name:
            session_id = "".join(session_id.split("-"))

        LOGGER.info(f"delete_session_handler called with session_id: {session_id}")
        delete_session(base_response=base_response, pod_name=pod_name, session_id=session_id, delete_type=delete_type)
    except Exception as err:
        LOGGER.error(err)

    return base_response.data, base_response.status_code


@session_blueprint.route('/api/v1/timeout/<string:pod_name>/<string:req_id>/<string:delete_type>', methods=['DELETE'])
def timeout_session_handler(pod_name=None, req_id=None, delete_type=None):
    """
        API(DELETE) to timeout sessions and delete k8s pod.

        :param: pod_name: It contains unique user id.
        :type: pod_name: str
        :param: req_id: It contains unique org id.
        :type: req_id: str
        :param: delete_type: It contains unique org id.
        :type: delete_type: str

        :return: Base Response object{data:{...}, msg:"...", status: ...}
        :rtype: response dict , status code
    """
    base_response = BaseResponse()

    try:
        LOGGER.info(f"timeout_session_handler called with request_id: {req_id}")
        delete_session(base_response=base_response, pod_name=pod_name, request_id=req_id, delete_type=delete_type)
    except Exception as err:
        LOGGER.error(err)

    return base_response.data, base_response.status_code
