from __future__ import annotations

import inspect
import typing as t

from flask import current_app
from kubernetes import config, client
from kubernetes.client import V1Pod
from kubernetes.client.exceptions import ApiException
from commons import env_info

try:
    config.load_kube_config()
except Exception as e:
    config.load_incluster_config()


V1_INSTANCE = client.CoreV1Api()


def get_pod(namespace: str, pod_name: str) -> V1Pod:
    """
        :param : namespace: namespace of k8s
        :type: namespace: str
        :param : pod_name: name of k8s pod
        :type: pod_name: str
        :return V1Pod object response
        :rtype: V1Pod
    """
    current_app.logger.info(f"Function Name ==>> {inspect.stack()[0][3]}")
    current_app.logger.info(f"Getting pod : {pod_name} in namespace : {namespace}.")
    try:
        return V1_INSTANCE.read_namespaced_pod(name=pod_name, namespace=namespace)
    except ApiException as err:
        current_app.logger.warning(f"Exception when calling CoreV1Api->read_namespaced_pod: {err}")
        if err.status == 404:
            raise Exception(f'Pod `{pod_name}` in namespace `{namespace}` not found') from err
        raise err


def delete_pod(namespace: str, pod_name: str) -> None:
    """
        :param : namespace: namespace of k8s
        :type: namespace: str
        :param : pod_name: name of k8s pod
        :type: pod_name: str
    """
    print(f"Function Name ==>> {inspect.stack()[0][3]}")
    print(f"Deleting pod : {pod_name} in namespace : {namespace}.")
    try:
        V1_INSTANCE.delete_namespaced_pod(name=pod_name, namespace=namespace)
        print(f"Successfully deleted pod : {pod_name} in namespace : {namespace}.")
    except ApiException as err:
        print(f"Exception when calling CoreV1Api->delete_namespaced_pod: {err}")
        if err.status == 403:
            raise Exception(f"Can't delete pod `{pod_name}` in namespace `{namespace}`") from err
        if err.status == 404:
            raise Exception(f'Pod `{pod_name}` in namespace `{namespace}` not found') from err
        raise err


def get_pod_logs(namespace: str, pod_name: str, container_name: str):
    """
        :param : namespace: namespace of k8s
        :type: namespace: str
        :param : pod_name: name of k8s pod
        :type: pod_name: str
        :param : container_name: name of container inside k8s pod
        :type: container_name: str
        :return logs_data from k8s pod
        :rtype: text/plain
    """
    print(f"Function Name ==>> {inspect.stack()[0][3]}")
    print(f"Fetching pod logs for: {pod_name} in namespace : {namespace}.")
    logs_data = ""
    try:
        logs_data = V1_INSTANCE.read_namespaced_pod_log(name=pod_name,
                                                        namespace=namespace,
                                                        container=container_name)
        print(f"Successfully fetched logs for pod name : `{pod_name}`")
    except ApiException as err:
        print(f"Exception when calling CoreV1Api->read_namespaced_pod_log: {err}")
    return logs_data


def get_pod_ip(pod: V1Pod) -> t.Any | None:
    """
        :param : pod: V1Pod object
        :type: V1Pod
        :return pod_ip/None from V1pod object
        :rtype: str/None
    """
    current_app.logger.info(f"Function Name ==>> {inspect.stack()[0][3]}")
    pod_ip = pod.status.pod_ip

    # In some cases K8s does not return pod IP
    if pod_ip is None:
        current_app.logger.warning(f"Pod does not have an IP")
        return None

    return pod_ip


def check_backend_pod_availability():
    """
        Check if org namespace contains backend pod
    """
    current_app.logger.info(f"Helper function for checking backend pod in given namespace {env_info.ORG_NAME}.")
    try:
        result = V1_INSTANCE.list_namespaced_pod(namespace=env_info.ORG_NAME,
                                                    label_selector='app=cloudifytests-session-be').to_dict()

        if len(result["items"]) == 0:
            current_app.logger.warning(f"No backend pod was found in the namespace {env_info.ORG_NAME}.")
            return False
        else:
            current_app.logger.warning(f"Backend pod was found in the namespace {env_info.ORG_NAME}.")
            return True

    except client.ApiException as e:
        current_app.logger.error(e)
        if e.status == 403:
            raise Exception(e)
        if e.status == 404:
            raise Exception(e)
