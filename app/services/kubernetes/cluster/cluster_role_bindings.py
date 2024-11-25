"""1. List all cluster role bindings in the cluster.
2. Show details of the cluster role binding named 'admin-binding'.
3. Which subjects are associated with the cluster role binding 'admin-binding'?
4. What cluster role is assigned in 'admin-binding'?
5. Find all cluster role bindings that include user 'john.doe'.
6. List cluster role bindings associated with service account 'default'.
7. Which cluster role bindings grant the 'cluster-admin' role?
8. Show cluster role bindings that include group 'developers'.
9. Are there any cluster role bindings without any subjects?
10. Find cluster role bindings with annotations 'environment=production'.
11. Show annotations of cluster role binding 'system:node'.
12. List cluster role bindings that reference role 'view'.
13. Find cluster role bindings including service account 'kube-system/default'.
14. Which cluster role bindings are associated with group 'system:masters'?
15. Display subjects of cluster role binding 'cluster-readers'.

"""

from typing import Optional, Dict, List
from kubernetes import client
from ..kubernetes_client import KubernetesBase

class ClusterRoleBindingResource(KubernetesBase):
    def __init__(self, labels: Optional[Dict[str, str]] = None):
        super().__init__(labels=labels)  # ClusterRoleBindings are cluster-scoped
        self.api = client.RbacAuthorizationV1Api()  # RBAC API client for ClusterRoleBindings

    def list_cluster_role_bindings(self) -> str:
        """List all ClusterRoleBindings in the cluster."""
        try:
            crbs = self.api.list_cluster_role_binding(label_selector=self.label_selector)
            if not crbs.items:
                return "No cluster role bindings found."

            crb_list = [crb.metadata.name for crb in crbs.items]
            return ", ".join(crb_list)
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error listing cluster role bindings"

    def get_crb_details(self, crb_name: str) -> str:
        """Retrieve detailed information about a specific ClusterRoleBinding."""
        try:
            crb = self.api.read_cluster_role_binding(name=crb_name)
            details = f"ClusterRoleBinding '{crb_name}' details:\n"
            details += f"  Role Ref: {crb.role_ref.kind}/{crb.role_ref.name}\n"
            if crb.subjects:
                details += "  Subjects:\n"
                for subject in crb.subjects:
                    details += f"    - Kind: {subject.kind}, Name: {subject.name}, Namespace: {subject.namespace or 'N/A'}\n"
            else:
                details += "  Subjects: None\n"
            return details
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error retrieving cluster role binding details"

    def get_subjects(self, crb_name: str) -> str:
        """Get the subjects associated with a ClusterRoleBinding."""
        try:
            crb = self.api.read_cluster_role_binding(name=crb_name)
            if crb.subjects:
                subjects_info = []
                for subject in crb.subjects:
                    subject_info = f"Kind: {subject.kind}, Name: {subject.name}, Namespace: {subject.namespace or 'N/A'}"
                    subjects_info.append(subject_info)
                return f"Subjects for ClusterRoleBinding '{crb_name}':\n" + "\n".join(subjects_info)
            else:
                return f"ClusterRoleBinding '{crb_name}' has no subjects."
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error retrieving subjects"

    def get_role_ref(self, crb_name: str) -> str:
        """Get the role reference associated with a ClusterRoleBinding."""
        try:
            crb = self.api.read_cluster_role_binding(name=crb_name)
            role_ref = crb.role_ref
            return f"ClusterRoleBinding '{crb_name}' references role: {role_ref.kind}/{role_ref.name}"
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error retrieving role reference"

    def find_crbs_by_subject(self, subject_kind: str, subject_name: str) -> str:
        """Find ClusterRoleBindings that include a specific subject."""
        try:
            crbs = self.api.list_cluster_role_binding().items
            matching_crbs = []
            for crb in crbs:
                if crb.subjects:
                    for subject in crb.subjects:
                        if subject.kind.lower() == subject_kind.lower() and subject.name == subject_name:
                            matching_crbs.append(crb.metadata.name)
                            break
            if matching_crbs:
                return f"ClusterRoleBindings including {subject_kind} '{subject_name}':\n" + "\n".join(matching_crbs)
            else:
                return f"No ClusterRoleBindings found including {subject_kind} '{subject_name}'."
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error finding cluster role bindings by subject"

    def find_crbs_by_role(self, role_name: str) -> str:
        """Find ClusterRoleBindings that reference a specific ClusterRole."""
        try:
            crbs = self.api.list_cluster_role_binding().items
            matching_crbs = [crb.metadata.name for crb in crbs if crb.role_ref.kind == 'ClusterRole' and crb.role_ref.name == role_name]
            if matching_crbs:
                return f"ClusterRoleBindings referencing ClusterRole '{role_name}':\n" + "\n".join(matching_crbs)
            else:
                return f"No ClusterRoleBindings found referencing ClusterRole '{role_name}'."
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error finding cluster role bindings by role"

    def get_annotations(self, crb_name: str) -> str:
        """Retrieve annotations associated with a ClusterRoleBinding."""
        try:
            crb = self.api.read_cluster_role_binding(name=crb_name)
            annotations = crb.metadata.annotations
            if annotations:
                annotations_info = "\n".join([f"{k}: {v}" for k, v in annotations.items()])
                return f"ClusterRoleBinding '{crb_name}' annotations:\n{annotations_info}"
            else:
                return f"ClusterRoleBinding '{crb_name}' has no annotations."
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error retrieving cluster role binding annotations"

    def find_crbs_without_subjects(self) -> str:
        """Find ClusterRoleBindings that have no subjects."""
        try:
            crbs = self.api.list_cluster_role_binding().items
            crbs_without_subjects = [crb.metadata.name for crb in crbs if not crb.subjects]
            if crbs_without_subjects:
                return "ClusterRoleBindings without subjects:\n" + "\n".join(crbs_without_subjects)
            else:
                return "All ClusterRoleBindings have subjects."
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error finding cluster role bindings without subjects"




def crb_handler(query) -> str:
    crb_resource = ClusterRoleBindingResource(labels=query.filters.labels if query.filters else None)

    # Route based on the action specified in the query
    if query.action == "list":
        return crb_resource.list_cluster_role_bindings()

    elif query.action == "details" and query.specific_name:
        return crb_resource.get_crb_details(query.specific_name)

    elif query.action == "subjects" and query.specific_name:
        return crb_resource.get_subjects(query.specific_name)

    elif query.action == "role_ref" and query.specific_name:
        return crb_resource.get_role_ref(query.specific_name)

    elif query.action == "find_by_subject" and query.filters.subject_kind and query.filters.subject_name:
        return crb_resource.find_crbs_by_subject(query.filters.subject_kind, query.filters.subject_name)

    elif query.action == "find_by_role" and query.filters.role_name:
        return crb_resource.find_crbs_by_role(query.filters.role_name)

    elif query.action == "annotations" and query.specific_name:
        return crb_resource.get_annotations(query.specific_name)

    elif query.action == "find_without_subjects":
        return crb_resource.find_crbs_without_subjects()

    else:
        return "Unsupported action or missing required parameters for cluster role binding."

