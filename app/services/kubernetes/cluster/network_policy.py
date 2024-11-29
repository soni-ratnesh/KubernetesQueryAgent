
"""
1. List all network policies in the 'default' namespace.
2. Show details of the network policy named 'deny-all'.
3. Which pods are selected by the network policy 'allow-http'?
4. What ingress rules are defined in the network policy 'allow-ssh'?
5. Find network policies that affect pod 'web-app'.
6. Show egress rules for network policies in the 'production' namespace.
7. Are there any network policies that allow traffic from namespace 'frontend'?
8. List network policies with label 'environment=staging'.
9. What namespaces have network policies applied?
10. Find network policies that deny all ingress traffic.
11. Show network policies that allow traffic to port 80.
12. Which network policies apply to pods with label 'app=backend'?
13. Get the creation time of the network policy 'db-access'.
14. List network policies that allow ingress from pods with label 'role=monitoring'.
15. Are there any default network policies in the 'secure' namespace?
16. Show annotations for network policy 'restrict-traffic'.
17. Find network policies affecting pod 'database'.
18. List network policies with ingress rules on port 443.
19. What egress rules are defined in network policy 'allow-external'?
20. Which network policies deny all egress traffic?
"""

from typing import Optional, Dict, List
from kubernetes import client
from ..kubernetes_client import KubernetesBase

class NetworkPolicyResource(KubernetesBase):
    def __init__(self, namespace: Optional[str] = "default", labels: Optional[Dict[str, str]] = None):
        super().__init__(namespace=namespace, labels=labels)
        self.api = client.NetworkingV1Api()  # NetworkingV1Api client for Network Policies

    def list_network_policies(self) -> str:
        """List all Network Policies in the namespace."""
        try:
            policies = self.api.list_namespaced_network_policy(
                namespace=self.namespace, label_selector=self.label_selector
            )
            if not policies.items:
                return f"No network policies found in namespace '{self.namespace}'."

            policy_list = [policy.metadata.name for policy in policies.items]
            return f"Network Policies in namespace '{self.namespace}':\n" + "\n".join(policy_list)
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return f"Error listing network policies in namespace '{self.namespace}'"

    def get_network_policy_details(self, policy_name: str) -> str:
        """Retrieve detailed information about a specific Network Policy."""
        try:
            policy = self.api.read_namespaced_network_policy(
                name=policy_name, namespace=self.namespace
            )
            details = f"Network Policy '{policy_name}' details:\n"
            pod_selector = policy.spec.pod_selector.match_labels or {}
            details += f"  Pod Selector: {pod_selector}\n"
            ingress_rules = policy.spec.ingress or []
            egress_rules = policy.spec.egress or []
            policy_types = policy.spec.policy_types or []

            details += f"  Policy Types: {policy_types}\n"
            details += "  Ingress Rules:\n"
            for ingress in ingress_rules:
                from_peers = ingress.from_ or []
                ports = ingress.ports or []
                details += "    - From:\n"
                for peer in from_peers:
                    peer_info = self._format_network_policy_peer(peer)
                    details += f"      {peer_info}\n"
                details += "      Ports:\n"
                for port in ports:
                    port_info = f"Port: {port.port}, Protocol: {port.protocol}"
                    details += f"        {port_info}\n"

            details += "  Egress Rules:\n"
            for egress in egress_rules:
                to_peers = egress.to or []
                ports = egress.ports or []
                details += "    - To:\n"
                for peer in to_peers:
                    peer_info = self._format_network_policy_peer(peer)
                    details += f"      {peer_info}\n"
                details += "      Ports:\n"
                for port in ports:
                    port_info = f"Port: {port.port}, Protocol: {port.protocol}"
                    details += f"        {port_info}\n"

            return details
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return f"Error retrieving details for network policy '{policy_name}' in namespace '{self.namespace}'"

    def _format_network_policy_peer(self, peer) -> str:
        """Helper function to format network policy peer information."""
        peer_info = ""
        if peer.pod_selector:
            labels = peer.pod_selector.match_labels or {}
            peer_info += f"Pod Selector: {labels}"
        if peer.namespace_selector:
            labels = peer.namespace_selector.match_labels or {}
            peer_info += f"Namespace Selector: {labels}"
        if peer.ip_block:
            cidr = peer.ip_block.cidr
            except_ips = peer.ip_block.except_ or []
            peer_info += f"IP Block: {cidr}, Except: {except_ips}"
        return peer_info or "None"

    def get_pods_affected_by_policy(self, policy_name: str) -> str:
        """Find pods that are selected by a specific Network Policy."""
        try:
            policy = self.api.read_namespaced_network_policy(
                name=policy_name, namespace=self.namespace
            )
            pod_selector = policy.spec.pod_selector
            if not pod_selector:
                return f"Network Policy '{policy_name}' has no pod selector."

            labels = pod_selector.match_labels or {}
            label_selector = ",".join([f"{k}={v}" for k, v in labels.items()])

            core_api = client.CoreV1Api()
            pods = core_api.list_namespaced_pod(
                namespace=self.namespace, label_selector=label_selector
            ).items

            if pods:
                pod_names = [pod.metadata.name for pod in pods]
                return f"Pods affected by Network Policy '{policy_name}':\n" + "\n".join(pod_names)
            else:
                return f"No pods are selected by Network Policy '{policy_name}'."
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return f"Error finding pods affected by network policy '{policy_name}' in namespace '{self.namespace}'"

    def find_policies_affecting_pod(self, pod_name: str) -> str:
        """Find Network Policies that affect a specific Pod."""
        try:
            core_api = client.CoreV1Api()
            pod = core_api.read_namespaced_pod(name=pod_name, namespace=self.namespace)
            pod_labels = pod.metadata.labels or {}

            policies = self.api.list_namespaced_network_policy(namespace=self.namespace).items
            matching_policies = []
            for policy in policies:
                selector = policy.spec.pod_selector
                if selector.match_labels:
                    match = all(
                        pod_labels.get(k) == v for k, v in selector.match_labels.items()
                    )
                    if match:
                        matching_policies.append(policy.metadata.name)

            if matching_policies:
                return f"Network Policies affecting Pod '{pod_name}':\n" + "\n".join(matching_policies)
            else:
                return f"No Network Policies affect Pod '{pod_name}' in namespace '{self.namespace}'."
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return f"Error finding network policies affecting pod '{pod_name}' in namespace '{self.namespace}'"

    def list_policies_by_ingress_rule(self, port: Optional[int] = None) -> str:
        """List Network Policies with specific ingress rules."""
        try:
            policies = self.api.list_namespaced_network_policy(namespace=self.namespace).items
            matching_policies = []
            for policy in policies:
                for ingress in policy.spec.ingress or []:
                    ports = ingress.ports or []
                    for p in ports:
                        if port is None or p.port == port:
                            matching_policies.append(policy.metadata.name)
                            break

            if matching_policies:
                port_info = f" on port {port}" if port else ""
                return f"Network Policies with ingress rules{port_info}:\n" + "\n".join(set(matching_policies))
            else:
                return f"No Network Policies found with specified ingress rules in namespace '{self.namespace}'."
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return f"Error listing network policies by ingress rule in namespace '{self.namespace}'"

    def get_annotations(self, policy_name: str) -> str:
        """Retrieve annotations associated with a Network Policy."""
        try:
            policy = self.api.read_namespaced_network_policy(
                name=policy_name, namespace=self.namespace
            )
            annotations = policy.metadata.annotations
            if annotations:
                annotations_info = "\n".join([f"{k}: {v}" for k, v in annotations.items()])
                return f"Network Policy '{policy_name}' annotations:\n{annotations_info}"
            else:
                return f"Network Policy '{policy_name}' has no annotations."
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return f"Error retrieving annotations for network policy '{policy_name}' in namespace '{self.namespace}'"


def np_handler(query) -> str:
   
    network_policy_resource = NetworkPolicyResource(
        namespace=query.namespace or "default",
        labels=query.filters.labels if query.filters else None
    )

    # Route based on the action specified in the query
    if query.action == "list":
        return network_policy_resource.list_network_policies()

    elif query.action == "details" and query.specific_name:
        return network_policy_resource.get_network_policy_details(query.specific_name)

    elif query.action == "pods_affected" and query.specific_name:
        return network_policy_resource.get_pods_affected_by_policy(query.specific_name)

    elif query.action == "policies_affecting_pod" and query.specific_name:
        return network_policy_resource.find_policies_affecting_pod(query.specific_name)

    elif query.action == "list_by_ingress_rule":
        port = query.filters.port if query.filters else None
        return network_policy_resource.list_policies_by_ingress_rule(port=port)

    elif query.action == "annotations" and query.specific_name:
        return network_policy_resource.get_annotations(query.specific_name)

    else:
        return "Unsupported action or missing required parameters for network policy."
