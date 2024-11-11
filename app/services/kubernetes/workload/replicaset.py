from app.services.kubernetes.kubernetes_client import KubernetesBase
from kubernetes import client
from typing import Optional, Dict

class ReplicaSetResource(KubernetesBase):
    def __init__(self, namespace: Optional[str] = "default", labels: Optional[Dict[str, str]] = None):
        super().__init__(namespace, labels)
        self.api = client.AppsV1Api()  
        self.core_v1_api = client.CoreV1Api()  

    def get_pods_for_deployment(self, deployment_name: str) -> str:
        try:
            # Fetch the deployment and retrieve its label selector
            deployment = self.api.read_namespaced_deployment(name=deployment_name, namespace=self.namespace)
            label_selector = ",".join([f"{k}={v}" for k, v in deployment.spec.selector.match_labels.items()])

            # List replica sets associated with the deployment's label selector
            replica_sets = self.api.list_namespaced_replica_set(namespace=self.namespace, label_selector=label_selector)
            if not replica_sets.items:
                return f"No replica sets found for deployment '{deployment_name}'."

            # Select the most recent replica set and get its pod-template-hash
            replica_set = sorted(replica_sets.items, key=lambda rs: rs.metadata.creation_timestamp, reverse=True)[0]
            pod_template_hash = replica_set.metadata.labels.get("pod-template-hash")
            if not pod_template_hash:
                return "No pod template hash found for the replica set."

            # Use the pod template hash to find the associated pods
            pod_label_selector = f"pod-template-hash={pod_template_hash}"
            pods = self.core_v1_api.list_namespaced_pod(namespace=self.namespace, label_selector=pod_label_selector)
            if not pods.items:
                return f"No pods found for deployment '{deployment_name}' with the specified pod template hash."

            # Remove identifiers from pod names and prepare the result
            pod_names = ["-".join(pod.metadata.name.split("-")[:-2]) for pod in pods.items]
            unique_pod_names = set(pod_names)  # Use a set to remove duplicates

            # Return a comma-separated string of pod names
            return ", ".join(unique_pod_names)
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error fetching pods for deployment"

def replicaset_handler(query):
    # Initialize ReplicaSetResource with namespace and labels if provided
    replicaset_resource = ReplicaSetResource(namespace=query.namespace)
    
    # Route based on the action specified in the query
    if query.action == "pods" and query.specific_name:
        pods = replicaset_resource.get_pods_for_deployment(query.specific_name)
        return f"Pods for deployment '{query.specific_name}': {pods}"
    
    else:
        return "Unsupported action or missing required parameters for replicaset."
