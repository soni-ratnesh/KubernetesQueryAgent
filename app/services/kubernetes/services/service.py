"""
1. List all services in the 'default' namespace.
2. Show details of the service named 'my-service'.
3. What is the type of service 'my-service'?
4. Get the cluster IP of 'my-service'.
5. What ports are exposed by 'my-service'?
6. Get the selector labels for 'my-service'.
7. What annotations are set on 'my-service'?
8. List services with label app=frontend.
9. Describe endpoints for 'my-service'.
10. Is 'my-service' a LoadBalancer service?
11. Show annotations of service 'my-service'.
12. List all NodePort services in the 'production' namespace.
13. What are the endpoints of service 'my-service'?

"""
from typing import Optional, Dict
from kubernetes import client
from ..kubernetes_client import KubernetesBase

class ServiceResource(KubernetesBase):
    def __init__(self, namespace: Optional[str] = "default", labels: Optional[Dict[str, str]] = None):
        super().__init__(namespace, labels)
        self.api = client.CoreV1Api()  # CoreV1Api client for Services

    def list_services(self) -> str:
        """List all Services in the namespace with basic details."""
        try:
            services = self.api.list_namespaced_service(namespace=self.namespace, label_selector=self.label_selector)
            if not services.items:
                return "No services found."

            service_list = []
            for service in services.items:
                name = service.metadata.name
                service_type = service.spec.type
                service_info = f"{name} (Type: {service_type})"
                service_list.append(service_info)

            return "; ".join(service_list)
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error listing services"

    def get_service_details(self, service_name: str) -> str:
        """Retrieve detailed information about a specific Service."""
        try:
            service = self.api.read_namespaced_service(name=service_name, namespace=self.namespace)
            details = f"Service '{service_name}' details:\n"
            details += f"  Type: {service.spec.type}\n"
            details += f"  Cluster IP: {service.spec.cluster_ip}\n"
            ports_info = []
            for port in service.spec.ports:
                ports_info.append(f"Port: {port.port}, Protocol: {port.protocol}, Target Port: {port.target_port}")
            details += f"  Ports:\n    " + "\n    ".join(ports_info)
            if service.spec.selector:
                selectors = ", ".join([f"{k}={v}" for k, v in service.spec.selector.items()])
                details += f"\n  Selectors: {selectors}"
            else:
                details += "\n  Selectors: None"
            return details
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error retrieving service details"

    def get_service_type(self, service_name: str) -> str:
        """Get the type of a Service (ClusterIP, NodePort, LoadBalancer, etc.)."""
        try:
            service = self.api.read_namespaced_service(name=service_name, namespace=self.namespace)
            service_type = service.spec.type
            return f"Service '{service_name}' is of type: {service_type}"
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error retrieving service type"

    def get_cluster_ip(self, service_name: str) -> str:
        """Get the Cluster IP of a Service."""
        try:
            service = self.api.read_namespaced_service(name=service_name, namespace=self.namespace)
            cluster_ip = service.spec.cluster_ip
            return f"Service '{service_name}' has Cluster IP: {cluster_ip}"
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error retrieving cluster IP"

    def get_service_ports(self, service_name: str) -> str:
        """Get the ports exposed by a Service."""
        try:
            service = self.api.read_namespaced_service(name=service_name, namespace=self.namespace)
            ports_info = []
            for port in service.spec.ports:
                ports_info.append(f"Port: {port.port}, Protocol: {port.protocol}, Target Port: {port.target_port}")
            if ports_info:
                return f"Service '{service_name}' ports:\n" + "\n".join(ports_info)
            else:
                return f"Service '{service_name}' exposes no ports."
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error retrieving service ports"

    def get_selectors(self, service_name: str) -> str:
        """Get the selector labels for a Service."""
        try:
            service = self.api.read_namespaced_service(name=service_name, namespace=self.namespace)
            if service.spec.selector:
                selectors = ", ".join([f"{k}={v}" for k, v in service.spec.selector.items()])
                return f"Service '{service_name}' selectors: {selectors}"
            else:
                return f"Service '{service_name}' has no selectors."
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error retrieving service selectors"

    def get_annotations(self, service_name: str) -> str:
        """Retrieve annotations associated with a Service."""
        try:
            service = self.api.read_namespaced_service(name=service_name, namespace=self.namespace)
            annotations = service.metadata.annotations
            if annotations:
                annotations_info = "\n".join([f"{k}: {v}" for k, v in annotations.items()])
                return f"Service '{service_name}' annotations:\n{annotations_info}"
            else:
                return f"Service '{service_name}' has no annotations."
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error retrieving service annotations"

    def get_endpoints(self, service_name: str) -> str:
        """Describe the endpoints associated with a Service."""
        try:
            endpoints_api = client.CoreV1Api()
            endpoints = endpoints_api.read_namespaced_endpoints(name=service_name, namespace=self.namespace)
            if endpoints.subsets:
                endpoint_info = []
                for subset in endpoints.subsets:
                    addresses = [addr.ip for addr in subset.addresses or []]
                    ports = [str(port.port) for port in subset.ports or []]
                    endpoint_info.append(f"Addresses: {', '.join(addresses)}, Ports: {', '.join(ports)}")
                return f"Endpoints for service '{service_name}':\n" + "\n".join(endpoint_info)
            else:
                return f"No endpoints found for service '{service_name}'."
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error retrieving service endpoints"

def service_resource_handler(query) -> str:
    # Check if the query is for services

    service_resource = ServiceResource(namespace=query.namespace, labels=query.filters.labels if query.filters else None)

    # Route based on the action specified in the query
    if query.action == "list":
        return service_resource.list_services()
    
    elif query.action == "details" and query.specific_name:
        return service_resource.get_service_details(query.specific_name)
    
    elif query.action == "type" and query.specific_name:
        return service_resource.get_service_type(query.specific_name)
    
    elif query.action == "cluster_ip" and query.specific_name:
        return service_resource.get_cluster_ip(query.specific_name)
    
    elif query.action == "ports" and query.specific_name:
        return service_resource.get_service_ports(query.specific_name)
    
    elif query.action == "selectors" and query.specific_name:
        return service_resource.get_selectors(query.specific_name)
    
    elif query.action == "annotations" and query.specific_name:
        return service_resource.get_annotations(query.specific_name)
    
    elif query.action == "endpoints" and query.specific_name:
        return service_resource.get_endpoints(query.specific_name)
    
    else:
        return "Unsupported action or missing required parameters for service."
    
