from ..kubernetes_client import KubernetesBase
from kubernetes import client
from typing import Optional, Dict

class PodResource(KubernetesBase):
    def __init__(self, namespace: Optional[str] = "default", labels: Optional[Dict[str, str]] = None):
        super().__init__(namespace, labels)
        self.api = client.CoreV1Api()  # CoreV1Api client for pods

    def get_count(self) -> str:
        try:
            pods = self.api.list_namespaced_pod(namespace=self.namespace, label_selector=self.label_selector)
            return str(len(pods.items))
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error querying pod count"

    def get_status(self, pod_name: str) -> str:
        try:
            pod = self.api.read_namespaced_pod(name=pod_name, namespace=self.namespace)
            restart_counts = sum(cs.restart_count for cs in pod.status.container_statuses)
            simple_name = "-".join(pod_name.split("-")[:-2])
            return f"{simple_name} is {pod.status.phase}, Restarts: {restart_counts}"
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error querying pod status"

    def get_creation_time(self, pod_name: str) -> str:
        try:
            pod = self.api.read_namespaced_pod(name=pod_name, namespace=self.namespace)
            simple_name = "-".join(pod_name.split("-")[:-2])
            return f"{simple_name} was created on {pod.metadata.creation_timestamp}"
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error querying pod creation time"

    def get_logs(self, pod_name: str) -> str:
        try:
            pod_log = self.api.read_namespaced_pod_log(name=pod_name, namespace=self.namespace)
            return pod_log
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error querying pod logs"

    def list_pods(self, status_filter: Optional[str] = "all") -> str:
        try:
            pods = self.api.list_namespaced_pod(namespace=self.namespace, label_selector=self.label_selector)
            if not pods.items:
                return "No pods found."

            filtered_pods = []
            for pod in pods.items:
                pod_status = pod.status.phase
                if status_filter == "running" and pod_status != "Running":
                    continue
                elif status_filter == "terminated" and pod_status != "Succeeded":
                    continue

                # Sum the restart counts for all containers in the pod
                restart_counts = sum(cs.restart_count for cs in pod.status.container_statuses)

                # Remove any identifier suffix from the pod name
                simple_name = "-".join(pod.metadata.name.split("-")[:-2])
                filtered_pods.append(f"{simple_name} (Status: {pod_status}, Restarts: {restart_counts})")
            if not filtered_pods:
                return f"No {status_filter} pods found."
            
            return ", ".join(filtered_pods)
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error listing pods"
