"""
1. List all storage classes in the cluster.
2. Show details of the storage class named 'standard'.
3. What is the provisioner for storage class 'standard'?
4. What parameters are associated with storage class 'standard'?
5. Which PVCs are using storage class 'standard'?
6. Show storage classes with annotations 'environment=production'.
7. Are there any storage classes with reclaim policy 'Delete'?
8. What is the default storage class in the cluster?
9. List storage classes that allow volume expansion.
10. Show storage classes with volume binding mode 'WaitForFirstConsumer'.
11. Which storage classes have encryption enabled?
12. Get the mount options for storage class 'fast-storage'.
13. Find storage classes with allowed topologies defined.
14. Show storage classes provided by 'kubernetes.io/aws-ebs'.
15. List storage classes that are deprecated.
16. Which storage classes have reclaim policy 'Retain'?
17. What storage classes are available in the cluster?
18. Show annotations of storage class 'premium-storage'.
19. List storage classes that do not allow volume expansion.
20. Find storage classes with volume binding mode 'Immediate'.
"""

# app/services/resources/config_storage/storage_class.py

from typing import Optional, Dict, List
from kubernetes import client
from ..kubernetes_client import KubernetesBase

class StorageClassResource(KubernetesBase):
    def __init__(self, labels: Optional[Dict[str, str]] = None):
        super().__init__(labels=labels)  # StorageClasses are cluster-scoped
        self.api = client.StorageV1Api()  # StorageV1Api client for StorageClasses

    def list_storage_classes(self) -> str:
        """List all StorageClasses in the cluster."""
        try:
            storage_classes = self.api.list_storage_class(label_selector=self.label_selector)
            if not storage_classes.items:
                return "No storage classes found."

            sc_list = [sc.metadata.name for sc in storage_classes.items]
            return ", ".join(sc_list)
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error listing storage classes"

    def get_storage_class_details(self, sc_name: str) -> str:
        """Retrieve detailed information about a specific StorageClass."""
        try:
            sc = self.api.read_storage_class(name=sc_name)
            details = f"StorageClass '{sc_name}' details:\n"
            details += f"  Provisioner: {sc.provisioner}\n"
            parameters = sc.parameters or {}
            parameters_info = "\n".join([f"    {k}: {v}" for k, v in parameters.items()])
            details += f"  Parameters:\n{parameters_info if parameters_info else '    None'}\n"
            details += f"  Reclaim Policy: {sc.reclaim_policy}\n"
            details += f"  Volume Binding Mode: {sc.volume_binding_mode}\n"
            details += f"  Allow Volume Expansion: {sc.allow_volume_expansion}\n"
            return details
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error retrieving storage class details"

    def get_provisioner(self, sc_name: str) -> str:
        """Get the provisioner of a StorageClass."""
        try:
            sc = self.api.read_storage_class(name=sc_name)
            provisioner = sc.provisioner
            return f"StorageClass '{sc_name}' uses provisioner: {provisioner}"
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error retrieving provisioner"

    def get_parameters(self, sc_name: str) -> str:
        """Get the parameters associated with a StorageClass."""
        try:
            sc = self.api.read_storage_class(name=sc_name)
            parameters = sc.parameters or {}
            if parameters:
                parameters_info = "\n".join([f"{k}: {v}" for k, v in parameters.items()])
                return f"Parameters for StorageClass '{sc_name}':\n{parameters_info}"
            else:
                return f"StorageClass '{sc_name}' has no parameters."
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error retrieving parameters"

    def get_pvcs_using_storage_class(self, sc_name: str) -> str:
        """Find PVCs that are using a specific StorageClass."""
        try:
            core_api = client.CoreV1Api()
            pvcs = core_api.list_persistent_volume_claim_for_all_namespaces(field_selector=f"spec.storageClassName={sc_name}").items
            if pvcs:
                pvc_list = [f"{pvc.metadata.namespace}/{pvc.metadata.name}" for pvc in pvcs]
                return f"PVCs using StorageClass '{sc_name}':\n" + "\n".join(pvc_list)
            else:
                return f"No PVCs are using StorageClass '{sc_name}'."
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error retrieving PVCs using storage class"

    def get_annotations(self, sc_name: str) -> str:
        """Retrieve annotations associated with a StorageClass."""
        try:
            sc = self.api.read_storage_class(name=sc_name)
            annotations = sc.metadata.annotations
            if annotations:
                annotations_info = "\n".join([f"{k}: {v}" for k, v in annotations.items()])
                return f"StorageClass '{sc_name}' annotations:\n{annotations_info}"
            else:
                return f"StorageClass '{sc_name}' has no annotations."
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error retrieving storage class annotations"

    def list_storage_classes_by_reclaim_policy(self, reclaim_policy: str) -> str:
        """List StorageClasses with a specific reclaim policy."""
        try:
            storage_classes = self.api.list_storage_class(label_selector=self.label_selector).items
            sc_list = [sc.metadata.name for sc in storage_classes if sc.reclaim_policy == reclaim_policy]
            if sc_list:
                return f"StorageClasses with reclaim policy '{reclaim_policy}':\n" + "\n".join(sc_list)
            else:
                return f"No StorageClasses with reclaim policy '{reclaim_policy}' found."
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error listing storage classes by reclaim policy"

    def get_default_storage_class(self) -> str:
        """Get the default StorageClass in the cluster."""
        try:
            storage_classes = self.api.list_storage_class().items
            default_scs = [sc.metadata.name for sc in storage_classes if sc.metadata.annotations and sc.metadata.annotations.get("storageclass.kubernetes.io/is-default-class") == "true"]
            if default_scs:
                return f"Default StorageClass: {default_scs[0]}"
            else:
                return "No default StorageClass is set."
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error retrieving default storage class"

    def list_storage_classes_with_volume_expansion(self) -> str:
        """List StorageClasses that allow volume expansion."""
        try:
            storage_classes = self.api.list_storage_class().items
            sc_list = [sc.metadata.name for sc in storage_classes if sc.allow_volume_expansion]
            if sc_list:
                return "StorageClasses that allow volume expansion:\n" + "\n".join(sc_list)
            else:
                return "No StorageClasses allow volume expansion."
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error listing storage classes with volume expansion"

    def list_storage_classes_by_volume_binding_mode(self, binding_mode: str) -> str:
        """List StorageClasses with a specific volume binding mode."""
        try:
            storage_classes = self.api.list_storage_class().items
            sc_list = [sc.metadata.name for sc in storage_classes if sc.volume_binding_mode == binding_mode]
            if sc_list:
                return f"StorageClasses with volume binding mode '{binding_mode}':\n" + "\n".join(sc_list)
            else:
                return f"No StorageClasses with volume binding mode '{binding_mode}' found."
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error listing storage classes by volume binding mode"



def handle_query(query) -> str:
   
    sc_resource = StorageClassResource(labels=query.filters.labels if query.filters else None)

    # Route based on the action specified in the query
    if query.action == "list":
        if query.filters and query.filters.reclaim_policy:
            return sc_resource.list_storage_classes_by_reclaim_policy(query.filters.reclaim_policy)
        elif query.filters and query.filters.volume_binding_mode:
            return sc_resource.list_storage_classes_by_volume_binding_mode(query.filters.volume_binding_mode)
        elif query.filters and query.filters.allow_volume_expansion is not None:
            return sc_resource.list_storage_classes_with_volume_expansion()
        else:
            return sc_resource.list_storage_classes()

    elif query.action == "details" and query.specific_name:
        return sc_resource.get_storage_class_details(query.specific_name)

    elif query.action == "provisioner" and query.specific_name:
        return sc_resource.get_provisioner(query.specific_name)

    elif query.action == "parameters" and query.specific_name:
        return sc_resource.get_parameters(query.specific_name)

    elif query.action == "used_by" and query.specific_name:
        return sc_resource.get_pvcs_using_storage_class(query.specific_name)

    elif query.action == "annotations" and query.specific_name:
        return sc_resource.get_annotations(query.specific_name)

    elif query.action == "default":
        return sc_resource.get_default_storage_class()

    else:
        return "Unsupported action or missing required parameters for storage class."
