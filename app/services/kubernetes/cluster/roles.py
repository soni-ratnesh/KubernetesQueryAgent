"""
1. List all roles in the 'default' namespace.
2. Show details of the role named 'pod-reader'.
3. What permissions are granted by the role 'configmap-editor'?
4. Which roles allow 'get' and 'list' on secrets?
5. Find roles that can update deployments in the 'production' namespace.
6. Show roles with annotations 'team=backend' in the 'staging' namespace.
7. Are there any roles that grant access to configmaps?
8. Which roles include 'create' and 'delete' permissions on services?
9. Find roles that allow 'watch' on pods.
10. Show resources and verbs for role 'namespace-admin'.
11. List roles that grant 'patch' on deployments.
12. Which roles have permissions on 'endpoints' resources?
13. Find roles that can 'create' 'pods/exec'.
14. Show roles allowing 'list' on 'persistentvolumeclaims'.
15. What annotations are set on role 'developer' in the 'development' namespace.
16. List roles with label 'environment=testing'.
17. Which roles have 'update' permission on configmaps?
18. Find roles that allow 'delete' on pods.
19. Show roles that grant 'get' on services.
20. What roles exist in the 'kube-system' namespace?
"""


from typing import Optional, Dict, List
from kubernetes import client
from ..kubernetes_client import KubernetesBase

class RoleResource(KubernetesBase):
    def __init__(self, namespace: Optional[str] = "default", labels: Optional[Dict[str, str]] = None):
        super().__init__(namespace=namespace, labels=labels)
        self.api = client.RbacAuthorizationV1Api()  # RBAC API client for Roles

    def list_roles(self) -> str:
        """List all Roles in the namespace."""
        try:
            roles = self.api.list_namespaced_role(namespace=self.namespace, label_selector=self.label_selector)
            if not roles.items:
                return f"No roles found in namespace '{self.namespace}'."

            role_list = [role.metadata.name for role in roles.items]
            return f"Roles in namespace '{self.namespace}':\n" + "\n".join(role_list)
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return f"Error listing roles in namespace '{self.namespace}'"

    def get_role_details(self, role_name: str) -> str:
        """Retrieve detailed information about a specific Role."""
        try:
            role = self.api.read_namespaced_role(name=role_name, namespace=self.namespace)
            details = f"Role '{role_name}' details in namespace '{self.namespace}':\n"
            rules_info = ""
            for rule in role.rules:
                api_groups = ', '.join(rule.api_groups or ['"'])
                resources = ', '.join(rule.resources or [])
                verbs = ', '.join(rule.verbs or [])
                rules_info += f"  - API Groups: {api_groups}\n    Resources: {resources}\n    Verbs: {verbs}\n"
            details += f"Rules:\n{rules_info}"
            return details
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return f"Error retrieving details for role '{role_name}' in namespace '{self.namespace}'"

    def find_roles_by_permission(self, verbs: List[str], resources: List[str]) -> str:
        """Find Roles that include specific verbs on resources."""
        try:
            roles = self.api.list_namespaced_role(namespace=self.namespace).items
            matching_roles = []
            for role in roles:
                for rule in role.rules:
                    if set(verbs).issubset(set(rule.verbs)) and set(resources).issubset(set(rule.resources or [])):
                        matching_roles.append(role.metadata.name)
                        break
            if matching_roles:
                return f"Roles with verbs {verbs} on resources {resources} in namespace '{self.namespace}':\n" + "\n".join(matching_roles)
            else:
                return f"No Roles found with verbs {verbs} on resources {resources} in namespace '{self.namespace}'."
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return f"Error finding roles by permission in namespace '{self.namespace}'"

    def get_annotations(self, role_name: str) -> str:
        """Retrieve annotations associated with a Role."""
        try:
            role = self.api.read_namespaced_role(name=role_name, namespace=self.namespace)
            annotations = role.metadata.annotations or {}
            if annotations:
                annotations_info = "\n".join([f"{k}: {v}" for k, v in annotations.items()])
                return f"Annotations for role '{role_name}' in namespace '{self.namespace}':\n{annotations_info}"
            else:
                return f"No annotations found for role '{role_name}' in namespace '{self.namespace}'."
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return f"Error retrieving annotations for role '{role_name}' in namespace '{self.namespace}'"


def roles_handler(query) -> str:
   
    role_resource = RoleResource(
        namespace=query.namespace or "default",
        labels=query.filters.labels if query.filters else None
    )

    # Route based on the action specified in the query
    if query.action == "list":
        return role_resource.list_roles()

    elif query.action == "details" and query.specific_name:
        return role_resource.get_role_details(query.specific_name)

    elif query.action == "find_by_permission" and query.filters.verbs and query.filters.resources:
        return role_resource.find_roles_by_permission(query.filters.verbs, query.filters.resources)

    elif query.action == "annotations" and query.specific_name:
        return role_resource.get_annotations(query.specific_name)

    else:
        return "Unsupported action or missing required parameters for role."

