# app/services/resources/services/ingress.py

from typing import Optional, Dict
from kubernetes import client
from ..kubernetes_client import KubernetesBase

class IngressResource(KubernetesBase):
    def __init__(self, namespace: Optional[str] = "default", labels: Optional[Dict[str, str]] = None):
        super().__init__(namespace, labels)
        self.api = client.NetworkingV1Api()  # NetworkingV1Api client for Ingresses

    def list_ingresses(self) -> str:
        """List all Ingresses in the namespace with basic details."""
        try:
            ingresses = self.api.list_namespaced_ingress(namespace=self.namespace, label_selector=self.label_selector)
            if not ingresses.items:
                return "No ingresses found."

            ingress_list = []
            for ingress in ingresses.items:
                name = ingress.metadata.name
                hosts = [rule.host for rule in ingress.spec.rules] if ingress.spec.rules else ["None"]
                ingress_info = f"{name} (Hosts: {', '.join(hosts)})"
                ingress_list.append(ingress_info)

            return ", ".join(ingress_list)
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error listing ingresses"

    def get_ingress_details(self, ingress_name: str) -> str:
        """Retrieve detailed information about a specific Ingress."""
        try:
            ingress = self.api.read_namespaced_ingress(name=ingress_name, namespace=self.namespace)
            details = f"Ingress '{ingress_name}' details:\n"
            hosts = [rule.host for rule in ingress.spec.rules] if ingress.spec.rules else ["None"]
            details += f"  Hosts: {hosts}\n"
            tls_info = []
            if ingress.spec.tls:
                for tls in ingress.spec.tls:
                    tls_info.append(f"Hosts: {', '.join(tls.hosts)}, Secret: {tls.secret_name}")
            details += f"  TLS: {tls_info if tls_info else 'None'}\n"
            details += f"  Backend Services:\n"
            for rule in ingress.spec.rules or []:
                if rule.http:
                    for path in rule.http.paths:
                        service_name = path.backend.service.name
                        service_port = path.backend.service.port.number
                        path_value = path.path
                        details += f"    - Path: {path_value}, Service: {service_name}:{service_port}\n"
            return details
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error retrieving ingress details"

    def get_backend_services(self, ingress_name: str) -> str:
        """Retrieve backend services and paths configured in an Ingress."""
        try:
            ingress = self.api.read_namespaced_ingress(name=ingress_name, namespace=self.namespace)
            services = []
            for rule in ingress.spec.rules or []:
                if rule.http:
                    for path in rule.http.paths:
                        service_name = path.backend.service.name
                        path_value = path.path
                        services.append(f"Service: {service_name}, Path: {path_value}")
            if not services:
                return f"No backend services found for ingress '{ingress_name}'."
            return "\n".join(services)
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error retrieving backend services"

    def get_hostnames(self, ingress_name: str) -> str:
        """Get the hostnames associated with an Ingress."""
        try:
            ingress = self.api.read_namespaced_ingress(name=ingress_name, namespace=self.namespace)
            hosts = [rule.host for rule in ingress.spec.rules] if ingress.spec.rules else ["None"]
            return f"Ingress '{ingress_name}' hosts: {', '.join(hosts)}"
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error retrieving ingress hostnames"

    def get_tls_configuration(self, ingress_name: str) -> str:
        """Retrieve TLS configuration of an Ingress."""
        try:
            ingress = self.api.read_namespaced_ingress(name=ingress_name, namespace=self.namespace)
            if ingress.spec.tls:
                tls_info = []
                for tls in ingress.spec.tls:
                    tls_info.append(f"Hosts: {', '.join(tls.hosts)}, Secret: {tls.secret_name}")
                return "\n".join(tls_info)
            else:
                return f"Ingress '{ingress_name}' has no TLS configuration."
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error retrieving TLS configuration"

    def get_ingress_rules(self, ingress_name: str) -> str:
        """Get the rules configured in an Ingress."""
        try:
            ingress = self.api.read_namespaced_ingress(name=ingress_name, namespace=self.namespace)
            if ingress.spec.rules:
                rules_info = []
                for rule in ingress.spec.rules:
                    host = rule.host
                    if rule.http:
                        for path in rule.http.paths:
                            service_name = path.backend.service.name
                            service_port = path.backend.service.port.number
                            path_value = path.path
                            rules_info.append(f"Host: {host}, Path: {path_value}, Service: {service_name}:{service_port}")
                return "\n".join(rules_info)
            else:
                return f"Ingress '{ingress_name}' has no rules configured."
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error retrieving ingress rules"

    def get_ingress_status(self, ingress_name: str) -> str:
        """Get the status of an Ingress."""
        try:
            ingress = self.api.read_namespaced_ingress_status(name=ingress_name, namespace=self.namespace)
            lb_ingress = ingress.status.load_balancer.ingress
            if lb_ingress:
                addresses = [ingress.ip or ingress.hostname for ingress in lb_ingress]
                return f"Ingress '{ingress_name}' is available at addresses: {', '.join(addresses)}"
            else:
                return f"Ingress '{ingress_name}' has no available addresses."
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error retrieving ingress status"

    def get_annotations(self, ingress_name: str) -> str:
        """Retrieve annotations associated with an Ingress."""
        try:
            ingress = self.api.read_namespaced_ingress(name=ingress_name, namespace=self.namespace)
            annotations = ingress.metadata.annotations
            if annotations:
                annotations_info = "\n".join([f"{k}: {v}" for k, v in annotations.items()])
                return f"Ingress '{ingress_name}' annotations:\n{annotations_info}"
            else:
                return f"Ingress '{ingress_name}' has no annotations."
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error retrieving ingress annotations"

def ingress_handler(query):
    # Check if the query is for ingress resources
  
    ingress_resource = IngressResource(namespace=query.namespace)

    # Route based on the action specified in the query
    if query.action == "list":
        return ingress_resource.list_ingresses()
    
    elif query.action == "details" and query.specific_name:
        return ingress_resource.get_ingress_details(query.specific_name)
    
    elif query.action == "backend_services" and query.specific_name:
        return ingress_resource.get_backend_services(query.specific_name)
    
    elif query.action == "hostnames" and query.specific_name:
        return ingress_resource.get_hostnames(query.specific_name)
    
    elif query.action == "tls" and query.specific_name:
        return ingress_resource.get_tls_configuration(query.specific_name)
    
    elif query.action == "rules" and query.specific_name:
        return ingress_resource.get_ingress_rules(query.specific_name)
    
    elif query.action == "status" and query.specific_name:
        return ingress_resource.get_ingress_status(query.specific_name)
    
    elif query.action == "annotations" and query.specific_name:
        return ingress_resource.get_annotations(query.specific_name)
    
    else:
        return "Unsupported action or missing required parameters for ingress."
    