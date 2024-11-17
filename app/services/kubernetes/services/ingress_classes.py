# app/services/resources/services/ingress_class.py

from typing import Optional, Dict
from kubernetes import client
from ..kubernetes_client import KubernetesBase

class IngressClassResource(KubernetesBase):
    def __init__(self, labels: Optional[Dict[str, str]] = None):
        super().__init__(labels=labels)  # No namespace for cluster-scoped resources
        self.api = client.NetworkingV1Api()  # NetworkingV1Api client for IngressClasses

    def list_ingress_classes(self) -> str:
        """List all IngressClasses in the cluster."""
        try:
            ingress_classes = self.api.list_ingress_class(label_selector=self.label_selector)
            if not ingress_classes.items:
                return "No ingress classes found."

            ingress_class_list = []
            for ingress_class in ingress_classes.items:
                name = ingress_class.metadata.name
                controller = ingress_class.spec.controller
                ingress_class_info = f"{name} (Controller: {controller})"
                ingress_class_list.append(ingress_class_info)

            return "; ".join(ingress_class_list)
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error listing ingress classes"

    def get_ingress_class_details(self, ingress_class_name: str) -> str:
        """Retrieve detailed information about a specific IngressClass."""
        try:
            ingress_class = self.api.read_ingress_class(name=ingress_class_name)
            details = f"Ingress Class '{ingress_class_name}' details:\n"
            details += f"  Controller: {ingress_class.spec.controller}\n"
            if ingress_class.spec.parameters:
                params = ingress_class.spec.parameters
                details += f"  Parameters: API Group: {params.api_group}, Kind: {params.kind}, Name: {params.name}\n"
            else:
                details += "  Parameters: None\n"
            return details
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error retrieving ingress class details"

    def get_controller(self, ingress_class_name: str) -> str:
        """Get the controller name associated with an IngressClass."""
        try:
            ingress_class = self.api.read_ingress_class(name=ingress_class_name)
            controller = ingress_class.spec.controller
            return f"Ingress Class '{ingress_class_name}' uses controller: {controller}"
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error retrieving ingress class controller"

    def get_parameters(self, ingress_class_name: str) -> str:
        """Get parameters associated with an IngressClass."""
        try:
            ingress_class = self.api.read_ingress_class(name=ingress_class_name)
            if ingress_class.spec.parameters:
                params = ingress_class.spec.parameters
                return (f"Ingress Class '{ingress_class_name}' parameters:\n"
                        f"  API Group: {params.api_group}\n"
                        f"  Kind: {params.kind}\n"
                        f"  Name: {params.name}")
            else:
                return f"Ingress Class '{ingress_class_name}' has no parameters."
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error retrieving ingress class parameters"

    def get_annotations(self, ingress_class_name: str) -> str:
        """Retrieve annotations associated with an IngressClass."""
        try:
            ingress_class = self.api.read_ingress_class(name=ingress_class_name)
            annotations = ingress_class.metadata.annotations
            if annotations:
                annotations_info = "\n".join([f"{k}: {v}" for k, v in annotations.items()])
                return f"Ingress Class '{ingress_class_name}' annotations:\n{annotations_info}"
            else:
                return f"Ingress Class '{ingress_class_name}' has no annotations."
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error retrieving ingress class annotations"

def ingress_class_handler(query):
    
    
    ingress_class_resource = IngressClassResource()

    # Route based on the action specified in the query
    if query.action == "list":
        return ingress_class_resource.list_ingress_classes()
    
    elif query.action == "details" and query.specific_name:
        return ingress_class_resource.get_ingress_class_details(query.specific_name)
    
    elif query.action == "controller" and query.specific_name:
        return ingress_class_resource.get_controller(query.specific_name)
    
    elif query.action == "parameters" and query.specific_name:
        return ingress_class_resource.get_parameters(query.specific_name)
    
    elif query.action == "annotations" and query.specific_name:
        return ingress_class_resource.get_annotations(query.specific_name)
    
    else:
        return "Unsupported action or missing required parameters for ingress class."
    