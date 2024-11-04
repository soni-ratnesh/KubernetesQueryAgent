from app.services.kubernetes.kubernetes_client import KubernetesBase
from typing import Optional, Dict
from kubernetes import client


class DaemonSetResource(KubernetesBase):
    def __init__(self, namespace: Optional[str] = "default", labels: Optional[Dict[str, str]] = None):
        super().__init__(namespace, labels)
        self.api = client.AppsV1Api()  # AppsV1Api client for DaemonSets
        self.core_v1_api = client.CoreV1Api()  # CoreV1Api for fetching pods associated with DaemonSets

    def list_daemonsets(self) -> str:
        """List all DaemonSets in the namespace with basic details."""
        try:
            daemonsets = self.api.list_namespaced_daemon_set(namespace=self.namespace, label_selector=self.label_selector)
            if not daemonsets.items:
                return "No daemonsets found."

            daemonset_list = []
            for daemonset in daemonsets.items:
                simple_name = daemonset.metadata.name.split("-")[0]  # Remove unique identifier suffixes
                desired = daemonset.status.desired_number_scheduled
                available = daemonset.status.number_available
                daemonset_info = f"{simple_name} (Desired: {desired}, Available: {available})"
                daemonset_list.append(daemonset_info)

            return ", ".join(daemonset_list)
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error listing daemonsets"

    def get_daemonset_status(self, daemonset_name: str) -> str:
        """Retrieve the status of a specific DaemonSet (number of desired, current, and available pods)."""
        try:
            daemonset = self.api.read_namespaced_daemon_set(name=daemonset_name, namespace=self.namespace)
            desired = daemonset.status.desired_number_scheduled
            current = daemonset.status.current_number_scheduled
            available = daemonset.status.number_available

            return f"Desired: {desired}, Current: {current}, Available: {available}"
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error retrieving daemonset status"

    def get_pods_for_daemonset(self, daemonset_name: str) -> str:
        """Retrieve all pods managed by a specific DaemonSet."""
        try:
            # Step 1: Fetch the DaemonSet and retrieve its label selector
            daemonset = self.api.read_namespaced_daemon_set(name=daemonset_name, namespace=self.namespace)
            label_selector = ",".join([f"{k}={v}" for k, v in daemonset.spec.selector.match_labels.items()])

            # Step 2: List pods using the DaemonSet's label selector
            pods = self.core_v1_api.list_namespaced_pod(namespace=self.namespace, label_selector=label_selector)
            if not pods.items:
                return f"No pods found for daemonset '{daemonset_name}'."

            # Remove identifiers from pod names and prepare the result
            pod_names = [pod.metadata.name.split("-")[0] for pod in pods.items]
            unique_pod_names = set(pod_names)  # Use a set to remove duplicates

            # Return a comma-separated string of pod names
            return ", ".join(unique_pod_names)
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error fetching pods for daemonset"

    def get_node_affinity(self, daemonset_name: str) -> str:
        """Retrieve node selector or affinity rules for a DaemonSet."""
        try:
            daemonset = self.api.read_namespaced_daemon_set(name=daemonset_name, namespace=self.namespace)
            node_selector = daemonset.spec.template.spec.node_selector
            affinity = daemonset.spec.template.spec.affinity

            if node_selector:
                selectors = ", ".join([f"{k}={v}" for k, v in node_selector.items()])
                return f"Node Selector: {selectors}"
            elif affinity:
                return "Affinity rules are defined for this DaemonSet."
            return "No node affinity or selector defined."
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error retrieving node affinity for daemonset"

def daemonset_handler(query):
    daemonset_resource = DaemonSetResource(namespace=query.namespace)
        
    # Route based on the action specified in the query
    if query.action == "list":
        return daemonset_resource.list_daemonsets()
    
    elif query.action == "status" and query.specific_name:
        status = daemonset_resource.get_daemonset_status(query.specific_name)
        return f"Status of daemonset '{query.specific_name}': {status}"
    
    elif query.action == "pods" and query.specific_name:
        pods = daemonset_resource.get_pods_for_daemonset(query.specific_name)
        return f"Pods for daemonset '{query.specific_name}': {pods}"
    
    elif query.action == "node_affinity" and query.specific_name:
        affinity = daemonset_resource.get_node_affinity(query.specific_name)
        return f"Node affinity for daemonset '{query.specific_name}': {affinity}"
    
    else:
        return "Unsupported action or missing required parameters for daemonset."

