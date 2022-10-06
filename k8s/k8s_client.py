"""
    Modules to interact with Kubernetes services.
"""

from __future__ import annotations

import inspect
import typing as t

from flask import current_app
from kubernetes import config, client
from kubernetes.client import V1Pod
# from kubernetes.watch import watch
from kubernetes.client.exceptions import ApiException


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


# def get_watch_pod_status(namespace: str, pod_name: str, status_type: str, timeout: int = 120) -> bool:
#     """
#         :param : namespace: namespace of k8s
#         :type: namespace: str
#         :param : pod_name: name of k8s pod
#         :type: pod_name: str
#         :param : status_type: status of pod for which watch_pod stream should run
#         :type: status_type: str
#         :param : timeout: time for which watch_pod stream should run
#         :type: timeout: int
#         :return True/False status flag value
#         :rtype: bool
#     """
#     status = False
#     k8_func = None
#     w = watch.Watch()
#
#     if status_type == "Running":
#         k8_func = V1_INSTANCE.read_namespaced_pod
#     elif status_type == "Terminating":
#         k8_func = V1_INSTANCE.delete_namespaced_pod
#
#     for event in w.stream(func=k8_func,
#                           namespace=namespace,
#                           name=pod_name,
#                           timeout_seconds=timeout):
#         if event["object"].status.phase == status_type:
#             w.stop()
#             status = True
#             return status
#
#     w.stop()
#     return status
