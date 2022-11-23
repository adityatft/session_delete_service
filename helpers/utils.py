"""
    Helper functions
"""

import inspect
import json
import time
import typing as t

import boto3
import requests

from flask import current_app
from commons import env_info


def retry_func(func: t.Callable[..., t.Any], retry_limit: int = 6, pause_time: int = 5, **kwargs: t.Any):
    """
        :param : func: function to be called
        :type: func: Callable function
        :param : retry_limit: number of tries for calling function
        :type: retry_limit: int
        :param : pause_time: sleep time after each retry
        :type: pause_time: int
        :param : **kwargs: dict of parameters to be passed while calling function
        :type: **kwargs: dict
        :return response from API
        :rtype: json object
    """
    current_app.logger.info(f"Function Name ==>> {inspect.stack()[0][3]}")
    retry_count = 0
    while retry_count < retry_limit:
        try:
            if retry_count > 0:
                current_app.logger.info(f"RETRY FUNC WORKING COUNT : {retry_count}")

            func_res = func(**kwargs)  # function calling

            if func_res.status_code == 200:
                current_app.logger.info(f" Func Response : {func_res}")
                return func_res
            current_app.logger.info(f"Retrying to call API : {kwargs['url']}")
        except Exception as err:
            current_app.logger.warning(err)
        retry_count += 1
        time.sleep(pause_time)


def update_session(**kwargs):
    """
        :param : url: endpoint for calling API
        :type: url: str
        :param : data: payload data for PUT request
        :type: data: dict
        :return response from API
        :rtype: json object
    """
    current_app.logger.info(f"Function Name ==>> {inspect.stack()[0][3]}")

    if "url" in kwargs and "data" in kwargs:
        current_app.logger.info(f"API URL : {kwargs['url']}")
        return requests.put(url=kwargs["url"], data=json.dumps(kwargs["data"]), headers=env_info.HEADERS)
    else:
        raise f"Required information for update_function API not correct."


def get_endpoint_api(**kwargs):
    """
        :param : url: endpoint for calling API
        :type: url: str
        :return response from API
        :rtype: json object
    """
    current_app.logger.info(f"Function Name ==>> {inspect.stack()[0][3]}")
    if "url" in kwargs:
        current_app.logger.info(f"API URL : {kwargs['url']}")
        return requests.get(url=kwargs["url"], headers=env_info.HEADERS)
    else:
        raise f"Required information for {kwargs['url']} API not correct."


def upload_to_s3(key, data):
    """
        :param : key: path on S3 bucket
        :type: key: str
        :param : data: data to be uploaded to S3 bucket.
        :type: data: str
    """
    current_app.logger.info(f"Function Name ==>> {inspect.stack()[0][3]}")
    current_app.logger.info(f"Uploading data to S3 for organization : {env_info.ORG_NAME}.")
    try:
        s3_obj = boto3.resource(service_name="s3",
                                aws_access_key_id=env_info.AWS_ACCESS_KEY,
                                aws_secret_access_key=env_info.AWS_SECRET_KEY)
        s3_obj.Bucket(env_info.S3_BUCKET).put_object(Key=key,
                                                     Body=data,
                                                     ContentType="text/plain")
        current_app.logger.info(f"Successfully uploaded logs data to S3 for organization : {env_info.ORG_NAME}.")
    except Exception as err:
        current_app.logger.warning(f"Exception when calling S3 Boto3 API: {err}")


def get_session_deleted_response() -> t.Dict[str, t.Any]:
    """
        https://w3c.github.io/webdriver/#delete-session
    """
    current_app.logger.info(f"Function Name ==>> {inspect.stack()[0][3]}")
    return {'value': None}


def get_delete_type(delete_type: str = None) -> t.Dict[str, t.Any]:
    """
        :param : delete_type: type of deletion from API URI
        :type: delete_type: str
        :return dict with status
        :rtype: dict
    """
    current_app.logger.info(f"Function Name ==>> {inspect.stack()[0][3]}")
    if delete_type == "aborted":
        status_data = {"status": "aborted"}
    elif delete_type == "timeout":
        status_data = {"status": "timeout"}
    else:
        status_data = {"status": "completed"}
    return status_data


def get_generated_urls(request_id: str = None, session_id: str = None) -> [t.Any, str, str]:
    """
        :param : request_id: request_id from API URI
        :type: request_id: str
        :param : session_id: webdriver session_id from API URI
        :type: session_id: str
        :return tuple of urls
        :rtype: tuple
    """
    current_app.logger.info(f"Function Name ==>> {inspect.stack()[0][3]}")
    if session_id:
        session_details_url = f"{env_info.ROOT_URL}/api/sessions/live/get-session-details/session/{session_id}"
        update_url = f"{env_info.ROOT_URL}/api/sessions/live/update-session-status/session/{session_id}"
    else:
        session_details_url = f"{env_info.ROOT_URL}/api/sessions/live/get-session-details/request/{request_id}"
        update_url = f"{env_info.ROOT_URL}/api/sessions/live/update-session-status/request/{request_id}"

    return session_details_url, update_url


# def generic_api_call(**kwargs):
#     """
#         :param : request_id: request_id from API URI
#         :type: request_id: str
#         :param : session_id: webdriver session_id from API URI
#         :type: session_id: str
#         :return tuple of urls
#         :rtype: tuple
#     """
#
#     if "method" in kwargs and kwargs["method"] == "GET":
#
#         if "url" in kwargs:
#             return requests.get(url=kwargs["url"], headers=env_info.HEADERS)
#         else:
#             raise f"Required information for {kwargs['url']} API not correct."
#
#     elif "method" in kwargs and kwargs["method"] == "POST":
#
#         if "url" in kwargs and "data" in kwargs:
#             return requests.post(url=kwargs["url"], data=kwargs["data"], headers=env_info.HEADERS)
#         else:
#             raise f"Required information for {kwargs['url']} API not correct."
#
#     elif "method" in kwargs and kwargs["method"] == "PUT":
#
#         if "url" in kwargs and "data" in kwargs:
#             return requests.put(url=kwargs["url"], data=kwargs["data"], headers=env_info.HEADERS)
#         else:
#             raise f"Required information for {kwargs['url']} API not correct."
#
#     elif "method" in kwargs and kwargs["method"] == "DELETE":
#         pass
#     else:
#         raise f"Required information for {kwargs['url']} API not correct."
