from ..kubernetes_client import KubernetesBase
from kubernetes import client
from typing import Optional, Dict


class DeploymentResource(KubernetesBase):
    def __init__(self, namespace: Optional[str] = "default", labels: Optional[Dict[str, str]] = None):
        super().__init__(namespace, labels)
        self.api = client.AppsV1Api()  

    def get_count(self) -> str:
        try:
            deployments = self.api.list_namespaced_deployment(namespace=self.namespace, label_selector=self.label_selector)
            return str(len(deployments.items))
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error querying deployment count"

    def get_status(self, deployment_name: str) -> str:
        try:
            deployment = self.api.read_namespaced_deployment(name=deployment_name, namespace=self.namespace)
            simple_name = deployment_name
            conditions = deployment.status.conditions
            if conditions:
                return f"{simple_name} is {conditions[-1].type}: {conditions[-1].status}"
            else:
                return f"{simple_name} has no status conditions."
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error querying deployment status"

    def get_creation_time(self, deployment_name: str) -> str:
        try:
            deployment = self.api.read_namespaced_deployment(name=deployment_name, namespace=self.namespace)
            simple_name = deployment_name
            creation_time = deployment.metadata.creation_timestamp
            return f"{simple_name} was created on {creation_time}"
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error querying deployment creation time"

    def exists(self) -> str:
        try:
            deployments = self.api.list_namespaced_deployment(namespace=self.namespace, label_selector=self.label_selector)
            if deployments.items:
                return f"Deployment(s) exist in the namespace '{self.namespace}' with the specified criteria."
            else:
                return f"No deployments found in the namespace '{self.namespace}' with the specified criteria."
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error checking deployment existence"

    def list_deployments(self, status_filter: Optional[str] = "all") -> str:
        try:
            deployments = self.api.list_namespaced_deployment(namespace=self.namespace, label_selector=self.label_selector)
            if not deployments.items:
                return "No deployments found."

            filtered_deployments = []

            for deployment in deployments.items:
                available_replicas = deployment.status.available_replicas or 0
                total_replicas = deployment.spec.replicas or 0

                # Apply filter based on status_filter value
                if status_filter == "active" and available_replicas == 0:
                    continue
                elif status_filter == "terminated" and available_replicas > 0:
                    continue

                simple_name = deployment.metadata.name
                filtered_deployments.append(f"{simple_name} (Replicas: {available_replicas}/{total_replicas})")

            if not filtered_deployments:
                return f"No {status_filter} deployments found."
            
            return ", ".join(filtered_deployments)
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error listing deployments"

def deployment_handler(query):
    deployment_resource = DeploymentResource(namespace=query.namespace, labels=query.filters.labels)

    # Route based on the action specified in the query
    if query.action == "count":
        return deployment_resource.get_count()
    
    elif query.action == "status" and query.specific_name:
        return deployment_resource.get_status(query.specific_name)
    
    elif query.action == "creation_time" and query.specific_name:
        return deployment_resource.get_creation_time(query.specific_name)
    
    elif query.action == "exists":
        return deployment_resource.exists()
    
    elif query.action == "list":
        # Use `status` in filters to list active, terminated, or all deployments
        status_filter = query.filters.status if len(query.filters.status) else "all"
        return deployment_resource.list_deployments(status_filter=status_filter)
    
    else:
        return "Unsupported action or missing required parameters."
        