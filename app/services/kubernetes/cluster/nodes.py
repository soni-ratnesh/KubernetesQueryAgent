"""
1. List all nodes in the cluster.
2. Show details of the node named 'node-1'.
3. What is the status of node 'node-2'?
4. List nodes with label 'role=worker'.
5. Which pods are running on node 'node-3'?
6. Show taints applied to node 'node-1'.
7. List nodes that are ready.
8. What are the allocatable resources on node 'node-2'?
9. Get the annotations set on node 'node-3'.
10. Which nodes have disk pressure conditions?
11. Find nodes not ready for scheduling.
12. Show nodes with memory capacity less than 16Gi.
13. List nodes with kernel version '4.15.0'.
14. What is the kubelet version on node 'node-4'?
15. Find nodes with network unavailable conditions.
16. List nodes with operating system 'linux'.
17. What is the architecture of node 'node-5'?
18. Show labels for node 'node-1'.
19. Which nodes have unschedulable status?
20. List nodes with CPU capacity greater than 8 cores.
"""

from typing import Optional, Dict, List
from kubernetes import client
from ..kubernetes_client import KubernetesBase

class NodeResource(KubernetesBase):
    def __init__(self, labels: Optional[Dict[str, str]] = None):
        super().__init__(labels=labels)  # Nodes are cluster-scoped
        self.api = client.CoreV1Api()  # CoreV1Api client for Nodes

    def list_nodes(self) -> str:
        """List all nodes in the cluster."""
        try:
            nodes = self.api.list_node(label_selector=self.label_selector)
            if not nodes.items:
                return "No nodes found."

            node_list = [node.metadata.name for node in nodes.items]
            return "Nodes in the cluster:\n" + "\n".join(node_list)
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error listing nodes"

    def get_node_details(self, node_name: str) -> str:
        """Retrieve detailed information about a specific Node."""
        try:
            node = self.api.read_node(name=node_name)
            details = f"Node '{node_name}' details:\n"

            # Node status conditions
            conditions = node.status.conditions or []
            condition_info = ""
            for condition in conditions:
                condition_info += f"  {condition.type}: {condition.status}\n"
            details += f"Conditions:\n{condition_info}"

            # Node addresses
            addresses = node.status.addresses or []
            address_info = "\n".join([f"  {addr.type}: {addr.address}" for addr in addresses])
            details += f"Addresses:\n{address_info}\n"

            # Node capacity and allocatable resources
            capacity = node.status.capacity or {}
            allocatable = node.status.allocatable or {}
            details += "Capacity:\n"
            for resource, value in capacity.items():
                alloc_value = allocatable.get(resource, 'N/A')
                details += f"  {resource}: Capacity {value}, Allocatable {alloc_value}\n"

            # Node labels
            labels = node.metadata.labels or {}
            labels_info = ", ".join([f"{k}={v}" for k, v in labels.items()])
            details += f"Labels: {labels_info if labels_info else 'None'}\n"

            # Node taints
            taints = node.spec.taints or []
            if taints:
                taints_info = "\n".join([f"  {t.effect}: {t.key}={t.value}" for t in taints])
                details += f"Taints:\n{taints_info}"
            else:
                details += "Taints: None\n"

            # Node annotations
            annotations = node.metadata.annotations or {}
            annotations_info = ", ".join([f"{k}={v}" for k, v in annotations.items()])
            details += f"Annotations: {annotations_info if annotations_info else 'None'}"

            return details
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return f"Error retrieving details for node '{node_name}'"

    def get_node_status(self, node_name: str) -> str:
        """Get the status of a Node."""
        try:
            node = self.api.read_node(name=node_name)
            conditions = node.status.conditions or []
            for condition in conditions:
                if condition.type == 'Ready':
                    return f"Node '{node_name}' status: Ready={condition.status}"
            return f"Node '{node_name}' status: Unknown"
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return f"Error retrieving status for node '{node_name}'"

    def list_nodes_with_label(self, label_selector: str) -> str:
        """List Nodes with a specific label."""
        try:
            nodes = self.api.list_node(label_selector=label_selector).items
            if nodes:
                node_list = [node.metadata.name for node in nodes]
                return f"Nodes with label '{label_selector}':\n" + "\n".join(node_list)
            else:
                return f"No nodes found with label '{label_selector}'."
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return f"Error finding nodes with label '{label_selector}'"

    def get_pods_on_node(self, node_name: str) -> str:
        """Find Pods that are running on a specific Node."""
        try:
            field_selector = f"spec.nodeName={node_name}"
            pods = self.api.list_pod_for_all_namespaces(field_selector=field_selector).items
            if pods:
                pod_list = [f"{pod.metadata.namespace}/{pod.metadata.name}" for pod in pods]
                return f"Pods running on node '{node_name}':\n" + "\n".join(pod_list)
            else:
                return f"No pods are running on node '{node_name}'."
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return f"Error retrieving pods on node '{node_name}'"

    def get_node_taints(self, node_name: str) -> str:
        """Get the taints applied to a Node."""
        try:
            node = self.api.read_node(name=node_name)
            taints = node.spec.taints or []
            if taints:
                taints_info = "\n".join([f"{t.effect}: {t.key}={t.value}" for t in taints])
                return f"Taints on node '{node_name}':\n" + taints_info
            else:
                return f"No taints on node '{node_name}'."
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return f"Error retrieving taints for node '{node_name}'"

    def list_ready_nodes(self) -> str:
        """List nodes that are Ready."""
        try:
            nodes = self.api.list_node().items
            ready_nodes = []
            for node in nodes:
                conditions = node.status.conditions or []
                for condition in conditions:
                    if condition.type == 'Ready' and condition.status == 'True':
                        ready_nodes.append(node.metadata.name)
                        break
            if ready_nodes:
                return "Ready nodes:\n" + "\n".join(ready_nodes)
            else:
                return "No nodes are in Ready state."
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error listing ready nodes"

    def get_allocatable_resources(self, node_name: str) -> str:
        """Get the allocatable resources on a Node."""
        try:
            node = self.api.read_node(name=node_name)
            allocatable = node.status.allocatable or {}
            if allocatable:
                resources_info = "\n".join([f"{k}: {v}" for k, v in allocatable.items()])
                return f"Allocatable resources on node '{node_name}':\n" + resources_info
            else:
                return f"No allocatable resources information for node '{node_name}'."
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return f"Error retrieving allocatable resources for node '{node_name}'"

    def get_node_annotations(self, node_name: str) -> str:
        """Retrieve annotations associated with a Node."""
        try:
            node = self.api.read_node(name=node_name)
            annotations = node.metadata.annotations or {}
            if annotations:
                annotations_info = "\n".join([f"{k}: {v}" for k, v in annotations.items()])
                return f"Annotations for node '{node_name}':\n" + annotations_info
            else:
                return f"No annotations found for node '{node_name}'."
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return f"Error retrieving annotations for node '{node_name}'"

    def list_nodes_with_condition(self, condition_type: str, condition_status: str) -> str:
        """List Nodes with a specific condition."""
        try:
            nodes = self.api.list_node().items
            matching_nodes = []
            for node in nodes:
                conditions = node.status.conditions or []
                for condition in conditions:
                    if condition.type == condition_type and condition.status == condition_status:
                        matching_nodes.append(node.metadata.name)
                        break
            if matching_nodes:
                return f"Nodes with condition {condition_type}={condition_status}:\n" + "\n".join(matching_nodes)
            else:
                return f"No nodes found with condition {condition_type}={condition_status}."
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return f"Error listing nodes with condition {condition_type}={condition_status}"

    def list_nodes_by_kernel_version(self, kernel_version: str) -> str:
        """List Nodes with a specific kernel version."""
        try:
            nodes = self.api.list_node().items
            matching_nodes = []
            for node in nodes:
                node_kernel_version = node.status.node_info.kernel_version
                if node_kernel_version == kernel_version:
                    matching_nodes.append(node.metadata.name)
            if matching_nodes:
                return f"Nodes with kernel version '{kernel_version}':\n" + "\n".join(matching_nodes)
            else:
                return f"No nodes found with kernel version '{kernel_version}'."
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return f"Error listing nodes with kernel version '{kernel_version}'"

    def get_node_kubelet_version(self, node_name: str) -> str:
        """Get the kubelet version on a Node."""
        try:
            node = self.api.read_node(name=node_name)
            kubelet_version = node.status.node_info.kubelet_version
            return f"Kubelet version on node '{node_name}': {kubelet_version}"
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return f"Error retrieving kubelet version for node '{node_name}'"




def nodes_handler(query) -> str:
    
    node_resource = NodeResource(labels=query.filters.labels if query.filters else None)

    # Route based on the action specified in the query
    if query.action == "list":
        if query.filters and query.filters.labels:
            label_selector = ",".join([f"{k}={v}" for k, v in query.filters.labels.items()])
            return node_resource.list_nodes_with_label(label_selector)
        else:
            return node_resource.list_nodes()

    elif query.action == "details" and query.specific_name:
        return node_resource.get_node_details(query.specific_name)

    elif query.action == "status" and query.specific_name:
        return node_resource.get_node_status(query.specific_name)

    elif query.action == "pods_on_node" and query.specific_name:
        return node_resource.get_pods_on_node(query.specific_name)

    elif query.action == "taints" and query.specific_name:
        return node_resource.get_node_taints(query.specific_name)

    elif query.action == "list_ready":
        return node_resource.list_ready_nodes()

    elif query.action == "allocatable_resources" and query.specific_name:
        return node_resource.get_allocatable_resources(query.specific_name)

    elif query.action == "annotations" and query.specific_name:
        return node_resource.get_node_annotations(query.specific_name)

    elif query.action == "list_by_condition" and query.filters.condition_type and query.filters.condition_status:
        return node_resource.list_nodes_with_condition(query.filters.condition_type, query.filters.condition_status)

    elif query.action == "list_by_kernel_version" and query.filters.kernel_version:
        return node_resource.list_nodes_by_kernel_version(query.filters.kernel_version)

    elif query.action == "kubelet_version" and query.specific_name:
        return node_resource.get_node_kubelet_version(query.specific_name)

    else:
        return "Unsupported action or missing required parameters for node."

