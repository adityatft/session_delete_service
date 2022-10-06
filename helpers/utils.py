"""
    Helper functions
"""

import inspect
import json
import time
import typing as t

import boto3
import requests

from datetime import datetime
from flask import current_app
from commons import env_info
from k8s import k8s_client


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
    print(f"Function Name ==>> {inspect.stack()[0][3]}")
    retry_count = 0
    while retry_count < retry_limit:
        try:
            if retry_count > 0:
                print(f"RETRY FUNC WORKING COUNT : {retry_count}")

            func_res = func(**kwargs)  # function calling

            if func_res.status_code == 200:
                print(f" Func Response : {func_res}")
                return func_res
            print(f"Retrying to call API : {kwargs['url']}")
        except Exception as err:
            print(err)
        retry_count += 1
        time.sleep(pause_time)


def update_session(url: str = None, data: dict = None):
    """
        :param : url: endpoint for calling API
        :type: url: str
        :param : data: payload data for PUT request
        :type: data: dict
        :return response from API
        :rtype: json object
    """
    print(f"Function Name ==>> {inspect.stack()[0][3]}")

    return retry_func(func=generic_api_call,
                      retry_limit=env_info.FUNC_RETRY_LIMIT,
                      pause_time=env_info.FUNC_RETRY_PAUSE_TIME,
                      url=url,
                      data=data,
                      method="PUT")


def get_session_details(url: str = None):
    """
        :param : url: endpoint for calling session_details API
        :type: url: str
        :return response from API
        :rtype: json object
    """
    current_app.logger.info(f"Function Name ==>> {inspect.stack()[0][3]}")
    return retry_func(func=generic_api_call,
                      retry_limit=env_info.FUNC_RETRY_LIMIT,
                      pause_time=env_info.FUNC_RETRY_PAUSE_TIME,
                      url=url,
                      method="GET")


def stop_video_recording_api(url: str = None):
    """
        :param : url: endpoint for stop video recorder API
        :type: url: str
        :return response from API
        :rtype: json object
    """
    print(f"Function Name ==>> {inspect.stack()[0][3]}")
    return retry_func(func=generic_api_call,
                      retry_limit=env_info.FUNC_RETRY_LIMIT,
                      pause_time=env_info.FUNC_RETRY_PAUSE_TIME,
                      url=url,
                      method="GET")


def upload_to_s3(key, data):
    """
        :param : key: path on S3 bucket
        :type: key: str
        :param : data: data to be uploaded to S3 bucket.
        :type: data: str
    """
    print(f"Function Name ==>> {inspect.stack()[0][3]}")
    print(f"Uploading data to S3 for organization : {env_info.ORG_NAME}.")
    try:
        s3_obj = boto3.resource(service_name="s3",
                                aws_access_key_id=env_info.AWS_ACCESS_KEY,
                                aws_secret_access_key=env_info.AWS_SECRET_KEY)
        s3_obj.Bucket(env_info.S3_BUCKET).put_object(Key=key,
                                                     Body=data,
                                                     ContentType="text/plain")
        print(f"Successfully uploaded logs data to S3 for organization : {env_info.ORG_NAME}.")
    except Exception as err:
        print(f"Exception when calling S3 Boto3 API: {err}")


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
        session_details_url = f"{env_info.ROOT_URL}/get-session-details/session/{session_id}"
        update_url = f"{env_info.ROOT_URL}/update-session-status/session/{session_id}"
    else:
        session_details_url = f"{env_info.ROOT_URL}/get-session-details/request/{request_id}"
        update_url = f"{env_info.ROOT_URL}/update-session-status/request/{request_id}"

    return session_details_url, update_url


def save_video_log_k8d_pods(data: dict = None):
    """
        :param : data: dict of session_data, pod_name, pod_ip, update_url, status_data
        :type: data: dict
    """
    print(data)

    session_data = data['session_data']
    pod_name = data['pod_name']
    pod_ip = data['pod_ip']
    # update_url = data['update_url']  # Future use case for handling multiple status states.

    try:
        if "enable_video" in session_data and session_data["enable_video"]:
            print(f"/stop-recording api called with pod_name: {pod_name}")
            stop_recording_url = f"http://{pod_ip}:9092/stop-recording"

            start_time = datetime.now()

            recording_res = stop_video_recording_api(url=stop_recording_url)

            total_time_diff = (datetime.now() - start_time).total_seconds()
            print(f"Total time for video to stop and upload : {total_time_diff}")

            if recording_res.status_code == 200:
                print("Video recording successfully stopped.")
            else:
                print("Couldn't stop video recorder.")

        if "enable_logs" in session_data and session_data["enable_logs"]:
            start_time = datetime.now()
            logs_data = k8s_client.get_pod_logs(namespace=env_info.ORG_NAME, pod_name=pod_name, container_name="browser")

            print(f"s3 put_object called for pod_name: {pod_name}")
            upload_to_s3(key=session_data["log_name"], data=logs_data)
            total_time_diff = (datetime.now() - start_time).total_seconds()
            print(f"Total time to fetch logs and upload : {total_time_diff}")

        # FUTURE USE-CASE : for putting session in COMPLETED Status after background task is successful.
        # print(f"Calling update_session. pod_name: {pod_name}")
        # update_session(url=update_url, data=status_data)

    except Exception as err:
        print(f"Exception in save_video_log_k8d_pods : {err}")

        # print(f"Calling update_session. pod_name: {pod_name}")
        # FUTURE USE-CASE : for putting session in FAILED completion state after background task is successful.
        # status_data = {"status": "Failed Completion"}
        # update_session(url=update_url, data=status_data)
    finally:
        print(f"Deleting pod with pod_name: {pod_name}")
        k8s_client.delete_pod(namespace=env_info.ORG_NAME, pod_name=pod_name)


def generic_api_call(**kwargs):
    """
        :param : method: HTTP API method type[e.g: GET, POST, PUT, DELETE]
        :type: method: str
        :param : url: endpoint for API
        :type: url: str
        :param : data: payload data for PUT request
        :type: data: dict
        :return API response
        :rtype: json
    """

    try:
        if "method" in kwargs and kwargs["method"] == "GET":
            return requests.get(url=kwargs["url"], headers=env_info.HEADERS)

        elif "method" in kwargs and kwargs["method"] == "POST":
            return requests.post(url=kwargs["url"], data=json.dumps(kwargs["data"]), headers=env_info.HEADERS)

        elif "method" in kwargs and kwargs["method"] == "PUT":
            return requests.put(url=kwargs["url"], data=json.dumps(kwargs["data"]), headers=env_info.HEADERS)

        elif "method" in kwargs and kwargs["method"] == "DELETE":
            pass

    except Exception as err:
        raise f"Required information for API not correct. Error : {err}"
