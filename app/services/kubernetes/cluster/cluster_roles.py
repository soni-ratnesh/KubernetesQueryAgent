"""
1. List all cluster roles in the cluster.
2. Show details of the cluster role named 'cluster-admin'.
3. What permissions are granted by the cluster role 'cluster-admin'?
4. Which cluster roles include 'get', 'list', and 'watch' permissions on pods?
5. Find cluster roles that can update deployments.
6. Show cluster roles with annotations 'environment=production'.
7. Are there any cluster roles that grant access to secrets?
8. Which cluster roles are associated with verbs 'create' and 'delete' on services?
9. Find cluster roles that allow 'patch' on configmaps.
10. Show resources and verbs for cluster role 'view'.
11. List cluster roles that grant 'watch' on events.
12. Which cluster roles have permissions on 'nodes' resources?
13. Find cluster roles that can 'create' 'pods/exec'.
14. Show cluster roles allowing 'list' on 'namespaces'.
15. What annotations are set on cluster role 'system:node'?
"""

from typing import Optional, Dict, List
from kubernetes import client
from ..kubernetes_client import KubernetesBase

class ClusterRoleResource(KubernetesBase):
    def __init__(self, labels: Optional[Dict[str, str]] = None):
        super().__init__(labels=labels)  # ClusterRoles are cluster-scoped
        self.api = client.RbacAuthorizationV1Api()  # RBAC API client for ClusterRoles

    def list_cluster_roles(self) -> str:
        """List all ClusterRoles in the cluster."""
        try:
            crs = self.api.list_cluster_role(label_selector=self.label_selector)
            if not crs.items:
                return "No cluster roles found."

            cr_list = [cr.metadata.name for cr in crs.items]
            return ", ".join(cr_list)
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error listing cluster roles"

    def get_cr_details(self, cr_name: str) -> str:
        """Retrieve detailed information about a specific ClusterRole."""
        try:
            cr = self.api.read_cluster_role(name=cr_name)
            details = f"ClusterRole '{cr_name}' details:\n"
            rules_info = ""
            for rule in cr.rules:
                api_groups = ', '.join(rule.api_groups or ['"'])
                resources = ', '.join(rule.resources or [])
                verbs = ', '.join(rule.verbs or [])
                rules_info += f"  - API Groups: {api_groups}\n    Resources: {resources}\n    Verbs: {verbs}\n"
            details += f"Rules:\n{rules_info}"
            return details
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error retrieving cluster role details"

    def find_crs_by_permission(self, verbs: List[str], resources: List[str]) -> str:
        """Find ClusterRoles that include specific verbs on resources."""
        try:
            crs = self.api.list_cluster_role().items
            matching_crs = []
            for cr in crs:
                for rule in cr.rules:
                    if set(verbs).issubset(set(rule.verbs)) and set(resources).issubset(set(rule.resources or [])):
                        matching_crs.append(cr.metadata.name)
                        break
            if matching_crs:
                return f"ClusterRoles with verbs {verbs} on resources {resources}:\n" + "\n".join(matching_crs)
            else:
                return f"No ClusterRoles found with verbs {verbs} on resources {resources}."
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error finding cluster roles by permission"

    def get_annotations(self, cr_name: str) -> str:
        """Retrieve annotations associated with a ClusterRole."""
        try:
            cr = self.api.read_cluster_role(name=cr_name)
            annotations = cr.metadata.annotations
            if annotations:
                annotations_info = "\n".join([f"{k}: {v}" for k, v in annotations.items()])
                return f"ClusterRole '{cr_name}' annotations:\n{annotations_info}"
            else:
                return f"ClusterRole '{cr_name}' has no annotations."
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error retrieving cluster role annotations"



def cr_handler(query) -> str:
    cr_resource = ClusterRoleResource(labels=query.filters.labels if query.filters else None)

    # Route based on the action specified in the query
    if query.action == "list":
        return cr_resource.list_cluster_roles()

    elif query.action == "details" and query.specific_name:
        return cr_resource.get_cr_details(query.specific_name)

    elif query.action == "find_by_permission" and query.filters.verbs and query.filters.resources:
        return cr_resource.find_crs_by_permission(query.filters.verbs, query.filters.resources)

    elif query.action == "annotations" and query.specific_name:
        return cr_resource.get_annotations(query.specific_name)

    else:
        return "Unsupported action or missing required parameters for cluster role."

