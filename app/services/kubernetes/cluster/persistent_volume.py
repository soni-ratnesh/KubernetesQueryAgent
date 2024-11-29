"""
1. List all persistent volumes in the cluster.
2. Show details of the persistent volume named 'pv-data'.
3. What is the status of persistent volume 'pv-backup'?
4. Which persistent volumes are bound to PVCs?
5. Find persistent volumes using storage class 'fast-storage'.
6. List persistent volumes with capacity greater than '100Gi'.
7. What access modes are supported by persistent volume 'pv-logs'?
8. Show persistent volumes with reclaim policy 'Retain'.
9. Which persistent volumes are available for binding?
10. Get the annotations set on persistent volume 'pv-data'.
11. Find persistent volumes in 'Released' state.
12. Show persistent volumes with volume mode 'Block'.
13. List persistent volumes provisioned by 'kubernetes.io/aws-ebs'.
14. What is the capacity of persistent volume 'pv-mysql'?
15. Find persistent volumes with labels 'environment=production'.
16. Show storage class associated with persistent volume 'pv-backup'.
17. Which PVCs are using persistent volume 'pv-data'?
18. List persistent volumes with NFS as the storage medium.
19. Are there any persistent volumes with encryption enabled?
20. Show persistent volumes created before '2023-01-01'.
"""

from typing import Optional, Dict, List
from kubernetes import client
from ..kubernetes_client import KubernetesBase

import re

class PersistentVolumeResource(KubernetesBase):
    def __init__(self, labels: Optional[Dict[str, str]] = None):
        super().__init__(labels=labels)  # PersistentVolumes are cluster-scoped
        self.api = client.CoreV1Api()  # CoreV1Api client for PersistentVolumes

    def list_persistent_volumes(self) -> str:
        """List all PersistentVolumes in the cluster."""
        try:
            pvs = self.api.list_persistent_volume(label_selector=self.label_selector)
            if not pvs.items:
                return "No persistent volumes found."

            pv_list = [pv.metadata.name for pv in pvs.items]
            return "Persistent Volumes in the cluster:\n" + "\n".join(pv_list)
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error listing persistent volumes"

    def get_pv_details(self, pv_name: str) -> str:
        """Retrieve detailed information about a specific PersistentVolume."""
        try:
            pv = self.api.read_persistent_volume(name=pv_name)
            details = f"PersistentVolume '{pv_name}' details:\n"
            details += f"  Capacity: {pv.spec.capacity.get('storage', 'N/A')}\n"
            details += f"  Access Modes: {', '.join(pv.spec.access_modes or [])}\n"
            details += f"  Reclaim Policy: {pv.spec.persistent_volume_reclaim_policy}\n"
            details += f"  Status: {pv.status.phase}\n"
            details += f"  Volume Mode: {pv.spec.volume_mode}\n"
            details += f"  Storage Class: {pv.spec.storage_class_name}\n"
            details += f"  Claim: {pv.spec.claim_ref.name if pv.spec.claim_ref else 'N/A'}\n"
            # Add more details as needed
            return details
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return f"Error retrieving details for persistent volume '{pv_name}'"

    def get_pv_status(self, pv_name: str) -> str:
        """Get the status of a PersistentVolume."""
        try:
            pv = self.api.read_persistent_volume(name=pv_name)
            status = pv.status.phase
            return f"PersistentVolume '{pv_name}' status: {status}"
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return f"Error retrieving status for persistent volume '{pv_name}'"

    def list_pvs_bound_to_pvcs(self) -> str:
        """List PersistentVolumes that are bound to PersistentVolumeClaims."""
        try:
            pvs = self.api.list_persistent_volume().items
            bound_pvs = [pv.metadata.name for pv in pvs if pv.status.phase == 'Bound']
            if bound_pvs:
                return "PersistentVolumes bound to PVCs:\n" + "\n".join(bound_pvs)
            else:
                return "No PersistentVolumes are bound to PVCs."
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error listing bound persistent volumes"

    def find_pvs_by_storage_class(self, storage_class_name: str) -> str:
        """Find PersistentVolumes using a specific StorageClass."""
        try:
            pvs = self.api.list_persistent_volume().items
            matching_pvs = [pv.metadata.name for pv in pvs if pv.spec.storage_class_name == storage_class_name]
            if matching_pvs:
                return f"PersistentVolumes using storage class '{storage_class_name}':\n" + "\n".join(matching_pvs)
            else:
                return f"No PersistentVolumes found using storage class '{storage_class_name}'."
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return f"Error finding persistent volumes using storage class '{storage_class_name}'"

    def list_pvs_by_capacity(self, operator: str, size: str) -> str:
        """List PersistentVolumes filtered by capacity."""
        try:
            def parse_size(size_str):
                match = re.match(r'(\d+)([KMGTP]i?)?', size_str)
                if match:
                    number = int(match.group(1))
                    unit = match.group(2) or ''
                    units = {'': 1, 'Ki': 1024, 'Mi': 1024 ** 2, 'Gi': 1024 ** 3, 'Ti': 1024 ** 4, 'Pi': 1024 ** 5}
                    return number * units.get(unit, 1)
                return 0

            threshold = parse_size(size)
            pvs = self.api.list_persistent_volume().items
            matching_pvs = []

            for pv in pvs:
                capacity_str = pv.spec.capacity.get('storage', '0')
                pv_size = parse_size(capacity_str)
                if (operator == '>' and pv_size > threshold) or \
                   (operator == '<' and pv_size < threshold) or \
                   (operator == '=' and pv_size == threshold):
                    matching_pvs.append(f"{pv.metadata.name} ({capacity_str})")

            if matching_pvs:
                return f"PersistentVolumes where capacity {operator} {size}:\n" + "\n".join(matching_pvs)
            else:
                return f"No PersistentVolumes found where capacity {operator} {size}."
        except Exception as e:
            self.log_error(f"Error processing PV capacities: {e}")
            return "Error retrieving persistent volumes by capacity"

    def get_pv_access_modes(self, pv_name: str) -> str:
        """Get the access modes of a PersistentVolume."""
        try:
            pv = self.api.read_persistent_volume(name=pv_name)
            access_modes = pv.spec.access_modes or []
            return f"Access modes for PersistentVolume '{pv_name}': {', '.join(access_modes)}"
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return f"Error retrieving access modes for persistent volume '{pv_name}'"

    def list_pvs_by_reclaim_policy(self, reclaim_policy: str) -> str:
        """List PersistentVolumes with a specific reclaim policy."""
        try:
            pvs = self.api.list_persistent_volume().items
            matching_pvs = [pv.metadata.name for pv in pvs if pv.spec.persistent_volume_reclaim_policy == reclaim_policy]
            if matching_pvs:
                return f"PersistentVolumes with reclaim policy '{reclaim_policy}':\n" + "\n".join(matching_pvs)
            else:
                return f"No PersistentVolumes found with reclaim policy '{reclaim_policy}'."
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return f"Error listing persistent volumes with reclaim policy '{reclaim_policy}'"

    def get_pv_annotations(self, pv_name: str) -> str:
        """Retrieve annotations associated with a PersistentVolume."""
        try:
            pv = self.api.read_persistent_volume(name=pv_name)
            annotations = pv.metadata.annotations or {}
            if annotations:
                annotations_info = "\n".join([f"{k}: {v}" for k, v in annotations.items()])
                return f"Annotations for PersistentVolume '{pv_name}':\n{annotations_info}"
            else:
                return f"No annotations found for persistent volume '{pv_name}'."
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return f"Error retrieving annotations for persistent volume '{pv_name}'"

    def find_pvs_by_status(self, status: str) -> str:
        """Find PersistentVolumes in a specific status."""
        try:
            pvs = self.api.list_persistent_volume().items
            matching_pvs = [pv.metadata.name for pv in pvs if pv.status.phase == status]
            if matching_pvs:
                return f"PersistentVolumes in status '{status}':\n" + "\n".join(matching_pvs)
            else:
                return f"No PersistentVolumes found in status '{status}'."
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return f"Error finding persistent volumes in status '{status}'"

    def get_pv_capacity(self, pv_name: str) -> str:
        """Get the capacity of a PersistentVolume."""
        try:
            pv = self.api.read_persistent_volume(name=pv_name)
            capacity = pv.spec.capacity.get('storage', 'N/A')
            return f"Capacity of PersistentVolume '{pv_name}': {capacity}"
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return f"Error retrieving capacity for persistent volume '{pv_name}'"

    def get_pv_storage_class(self, pv_name: str) -> str:
        """Get the storage class of a PersistentVolume."""
        try:
            pv = self.api.read_persistent_volume(name=pv_name)
            storage_class = pv.spec.storage_class_name or 'N/A'
            return f"Storage Class of PersistentVolume '{pv_name}': {storage_class}"
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return f"Error retrieving storage class for persistent volume '{pv_name}'"

    def get_pvc_using_pv(self, pv_name: str) -> str:
        """Get the PVC that is using a PersistentVolume."""
        try:
            pv = self.api.read_persistent_volume(name=pv_name)
            claim_ref = pv.spec.claim_ref
            if claim_ref:
                return f"PersistentVolume '{pv_name}' is bound to PVC '{claim_ref.namespace}/{claim_ref.name}'"
            else:
                return f"PersistentVolume '{pv_name}' is not bound to any PVC."
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return f"Error retrieving PVC using persistent volume '{pv_name}'"

    def list_pvs_by_volume_mode(self, volume_mode: str) -> str:
        """List PersistentVolumes with a specific volume mode."""
        try:
            pvs = self.api.list_persistent_volume().items
            matching_pvs = [pv.metadata.name for pv in pvs if pv.spec.volume_mode == volume_mode]
            if matching_pvs:
                return f"PersistentVolumes with volume mode '{volume_mode}':\n" + "\n".join(matching_pvs)
            else:
                return f"No PersistentVolumes found with volume mode '{volume_mode}'."
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return f"Error listing persistent volumes with volume mode '{volume_mode}'"


def pv_handler(query) -> str:
    
    pv_resource = PersistentVolumeResource(labels=query.filters.labels if query.filters else None)

    # Route based on the action specified in the query
    if query.action == "list":
        if query.filters and query.filters.storage_class:
            return pv_resource.find_pvs_by_storage_class(query.filters.storage_class)
        elif query.filters and query.filters.operator and query.filters.size:
            return pv_resource.list_pvs_by_capacity(query.filters.operator, query.filters.size)
        elif query.filters and query.filters.reclaim_policy:
            return pv_resource.list_pvs_by_reclaim_policy(query.filters.reclaim_policy)
        elif query.filters and query.filters.status:
            return pv_resource.find_pvs_by_status(query.filters.status)
        elif query.filters and query.filters.volume_mode:
            return pv_resource.list_pvs_by_volume_mode(query.filters.volume_mode)
        else:
            return pv_resource.list_persistent_volumes()

    elif query.action == "details" and query.specific_name:
        return pv_resource.get_pv_details(query.specific_name)

    elif query.action == "status" and query.specific_name:
        return pv_resource.get_pv_status(query.specific_name)

    elif query.action == "list_bound":
        return pv_resource.list_pvs_bound_to_pvcs()

    elif query.action == "access_modes" and query.specific_name:
        return pv_resource.get_pv_access_modes(query.specific_name)

    elif query.action == "annotations" and query.specific_name:
        return pv_resource.get_pv_annotations(query.specific_name)

    elif query.action == "capacity" and query.specific_name:
        return pv_resource.get_pv_capacity(query.specific_name)

    elif query.action == "storage_class" and query.specific_name:
        return pv_resource.get_pv_storage_class(query.specific_name)

    elif query.action == "pvc_using_pv" and query.specific_name:
        return pv_resource.get_pvc_using_pv(query.specific_name)

    else:
        return "Unsupported action or missing required parameters for persistent volume."
