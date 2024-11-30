"""
1. List all role bindings in the 'default' namespace.
2. Show details of the role binding named 'read-secrets-binding'.
3. Which subjects are associated with the role binding 'admin-binding'?
4. What role is assigned in 'developer-binding'?
5. Find all role bindings that include user 'alice'.
6. List role bindings associated with service account 'default'.
7. Which role bindings grant the role 'pod-reader'?
8. Show role bindings that include group 'developers'.
9. Are there any role bindings without any subjects?
10. Find role bindings with annotations 'team=frontend' in the 'staging' namespace.
11. Show annotations of role binding 'read-configmaps' in 'production'.
12. List role bindings that reference role 'configmap-editor'.
13. Find role bindings including service account 'kube-system/default'.
14. Which role bindings are associated with group 'system:authenticated'?
15. Display subjects of role binding 'view-binding' in 'development'.
16. List role bindings with label 'environment=testing'.
17. Which role bindings reference role 'secret-reader'?
18. Find role bindings that include user 'bob'.
19. Show role bindings that include group 'admins'.
20. What role bindings exist in the 'kube-system' namespace?
"""

from typing import Optional, Dict
from kubernetes import client
from ..kubernetes_client import KubernetesBase

class RoleBindingResource(KubernetesBase):
    def __init__(self, namespace: Optional[str] = "default", labels: Optional[Dict[str, str]] = None):
        super().__init__(namespace=namespace, labels=labels)
        self.api = client.RbacAuthorizationV1Api()  # RBAC API client for RoleBindings

    def list_role_bindings(self) -> str:
        """List all RoleBindings in the namespace."""
        try:
            rbs = self.api.list_namespaced_role_binding(namespace=self.namespace, label_selector=self.label_selector)
            if not rbs.items:
                return f"No role bindings found in namespace '{self.namespace}'."

            rb_list = [rb.metadata.name for rb in rbs.items]
            return f"RoleBindings in namespace '{self.namespace}':\n" + "\n".join(rb_list)
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return f"Error listing role bindings in namespace '{self.namespace}'"

    def get_rb_details(self, rb_name: str) -> str:
        """Retrieve detailed information about a specific RoleBinding."""
        try:
            rb = self.api.read_namespaced_role_binding(name=rb_name, namespace=self.namespace)
            details = f"RoleBinding '{rb_name}' details in namespace '{self.namespace}':\n"
            details += f"  Role Ref: {rb.role_ref.kind}/{rb.role_ref.name}\n"
            if rb.subjects:
                details += "  Subjects:\n"
                for subject in rb.subjects:
                    details += f"    - Kind: {subject.kind}, Name: {subject.name}, Namespace: {subject.namespace or 'N/A'}\n"
            else:
                details += "  Subjects: None\n"
            return details
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return f"Error retrieving role binding details for '{rb_name}' in namespace '{self.namespace}'"

    def get_subjects(self, rb_name: str) -> str:
        """Get the subjects associated with a RoleBinding."""
        try:
            rb = self.api.read_namespaced_role_binding(name=rb_name, namespace=self.namespace)
            if rb.subjects:
                subjects_info = []
                for subject in rb.subjects:
                    subject_info = f"Kind: {subject.kind}, Name: {subject.name}, Namespace: {subject.namespace or 'N/A'}"
                    subjects_info.append(subject_info)
                return f"Subjects for RoleBinding '{rb_name}' in namespace '{self.namespace}':\n" + "\n".join(subjects_info)
            else:
                return f"RoleBinding '{rb_name}' has no subjects in namespace '{self.namespace}'."
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return f"Error retrieving subjects for role binding '{rb_name}' in namespace '{self.namespace}'"

    def get_role_ref(self, rb_name: str) -> str:
        """Get the role reference associated with a RoleBinding."""
        try:
            rb = self.api.read_namespaced_role_binding(name=rb_name, namespace=self.namespace)
            role_ref = rb.role_ref
            return f"RoleBinding '{rb_name}' references role: {role_ref.kind}/{role_ref.name} in namespace '{self.namespace}'"
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return f"Error retrieving role reference for role binding '{rb_name}' in namespace '{self.namespace}'"

    def find_rbs_by_subject(self, subject_kind: str, subject_name: str) -> str:
        """Find RoleBindings that include a specific subject."""
        try:
            rbs = self.api.list_namespaced_role_binding(namespace=self.namespace).items
            matching_rbs = []
            for rb in rbs:
                if rb.subjects:
                    for subject in rb.subjects:
                        if subject.kind.lower() == subject_kind.lower() and subject.name == subject_name:
                            matching_rbs.append(rb.metadata.name)
                            break
            if matching_rbs:
                return f"RoleBindings including {subject_kind} '{subject_name}' in namespace '{self.namespace}':\n" + "\n".join(matching_rbs)
            else:
                return f"No RoleBindings found including {subject_kind} '{subject_name}' in namespace '{self.namespace}'."
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return f"Error finding role bindings by subject in namespace '{self.namespace}'"

    def find_rbs_by_role(self, role_name: str) -> str:
        """Find RoleBindings that reference a specific Role."""
        try:
            rbs = self.api.list_namespaced_role_binding(namespace=self.namespace).items
            matching_rbs = [rb.metadata.name for rb in rbs if rb.role_ref.kind == 'Role' and rb.role_ref.name == role_name]
            if matching_rbs:
                return f"RoleBindings referencing Role '{role_name}' in namespace '{self.namespace}':\n" + "\n".join(matching_rbs)
            else:
                return f"No RoleBindings found referencing Role '{role_name}' in namespace '{self.namespace}'."
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return f"Error finding role bindings by role in namespace '{self.namespace}'"

    def get_annotations(self, rb_name: str) -> str:
        """Retrieve annotations associated with a RoleBinding."""
        try:
            rb = self.api.read_namespaced_role_binding(name=rb_name, namespace=self.namespace)
            annotations = rb.metadata.annotations or {}
            if annotations:
                annotations_info = "\n".join([f"{k}: {v}" for k, v in annotations.items()])
                return f"Annotations for RoleBinding '{rb_name}' in namespace '{self.namespace}':\n{annotations_info}"
            else:
                return f"No annotations found for role binding '{rb_name}' in namespace '{self.namespace}'."
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return f"Error retrieving annotations for role binding '{rb_name}' in namespace '{self.namespace}'"


def rb_handler(query) -> str:
    rb_resource = RoleBindingResource(
        namespace=query.namespace or "default",
        labels=query.filters.labels if query.filters else None
    )

    # Route based on the action specified in the query
    if query.action == "list":
        return rb_resource.list_role_bindings()

    elif query.action == "details" and query.specific_name:
        return rb_resource.get_rb_details(query.specific_name)

    elif query.action == "subjects" and query.specific_name:
        return rb_resource.get_subjects(query.specific_name)

    elif query.action == "role_ref" and query.specific_name:
        return rb_resource.get_role_ref(query.specific_name)

    elif query.action == "find_by_subject" and query.filters.subject_kind and query.filters.subject_name:
        return rb_resource.find_rbs_by_subject(query.filters.subject_kind, query.filters.subject_name)

    elif query.action == "find_by_role" and query.filters.role_name:
        return rb_resource.find_rbs_by_role(query.filters.role_name)

    elif query.action == "annotations" and query.specific_name:
        return rb_resource.get_annotations(query.specific_name)

    else:
        return "Unsupported action or missing required parameters for role binding."