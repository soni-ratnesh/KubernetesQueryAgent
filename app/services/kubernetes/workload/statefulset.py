from app.services.kubernetes.kubernetes_client import KubernetesBase

from typing import Optional, Dict
from kubernetes import client

class StatefulSetResource(KubernetesBase):
    def __init__(self, namespace: Optional[str] = "default", labels: Optional[Dict[str, str]] = None):
        super().__init__(namespace, labels)
        self.api = client.AppsV1Api()  # AppsV1Api client for StatefulSets
        self.core_v1_api = client.CoreV1Api()  # CoreV1Api for fetching pods associated with StatefulSets

    def list_statefulsets(self) -> str:
        """List all StatefulSets in the namespace with basic details."""
        try:
            statefulsets = self.api.list_namespaced_stateful_set(namespace=self.namespace, label_selector=self.label_selector)
            if not statefulsets.items:
                return "No statefulsets found."

            statefulset_list = []
            for statefulset in statefulsets.items:
                simple_name = "-".join(statefulset.metadata.name.split("-")[:-2])  # Remove unique identifier suffixes
                desired = statefulset.spec.replicas
                ready = statefulset.status.ready_replicas or 0
                statefulset_info = f"{simple_name} (Desired: {desired}, Ready: {ready})"
                statefulset_list.append(statefulset_info)

            return ", ".join(statefulset_list)
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error listing statefulsets"

    def get_statefulset_status(self, statefulset_name: str) -> str:
        """Retrieve the status of a specific StatefulSet (desired, current, and ready replicas)."""
        try:
            statefulset = self.api.read_namespaced_stateful_set(name=statefulset_name, namespace=self.namespace)
            desired = statefulset.spec.replicas
            current = statefulset.status.current_replicas or 0
            ready = statefulset.status.ready_replicas or 0

            return f"Desired: {desired}, Current: {current}, Ready: {ready}"
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error retrieving statefulset status"

    def get_pods_for_statefulset(self, statefulset_name: str) -> str:
        """Retrieve all pods managed by a specific StatefulSet."""
        try:
            # Fetch the StatefulSet and retrieve its label selector
            statefulset = self.api.read_namespaced_stateful_set(name=statefulset_name, namespace=self.namespace)
            label_selector = ",".join([f"{k}={v}" for k, v in statefulset.spec.selector.match_labels.items()])

            # List pods using the StatefulSet's label selector
            pods = self.core_v1_api.list_namespaced_pod(namespace=self.namespace, label_selector=label_selector)
            if not pods.items:
                return f"No pods found for statefulset '{statefulset_name}'."

            # Remove identifiers from pod names and prepare the result
            pod_names = ["-".join(pod.metadata.name.split("-")[:-2]) for pod in pods.items]
            unique_pod_names = set(pod_names)  # Use a set to remove duplicates

            # Return a comma-separated string of pod names
            return ", ".join(unique_pod_names)
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error fetching pods for statefulset"

    def get_volume_claims(self, statefulset_name: str) -> str:
        """Retrieve persistent volume claims (PVCs) for a StatefulSet."""
        try:
            statefulset = self.api.read_namespaced_stateful_set(name=statefulset_name, namespace=self.namespace)
            volume_claims = statefulset.spec.volume_claim_templates

            if not volume_claims:
                return f"No volume claims found for statefulset '{statefulset_name}'."

            pvc_names = [pvc.metadata.name for pvc in volume_claims]
            return ", ".join(pvc_names)
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error retrieving volume claims for statefulset"

def statefulset_handler(query):
    # Initialize StatefulSetResource with namespace and labels if provided
    statefulset_resource = StatefulSetResource(namespace=query.namespace)
    
    # Route based on the action specified in the query
    if query.action == "list":
        return statefulset_resource.list_statefulsets()
    
    elif query.action == "status" and query.specific_name:
        status = statefulset_resource.get_statefulset_status(query.specific_name)
        return f"Status of statefulset '{query.specific_name}': {status}"
    
    elif query.action == "pods" and query.specific_name:
        pods = statefulset_resource.get_pods_for_statefulset(query.specific_name)
        return f"Pods for statefulset '{query.specific_name}': {pods}"
    
    elif query.action == "volume_claims" and query.specific_name:
        volume_claims = statefulset_resource.get_volume_claims(query.specific_name)
        return f"Volume claims for statefulset '{query.specific_name}': {volume_claims}"
    
    else:
        return "Unsupported action or missing required parameters for statefulset."
    