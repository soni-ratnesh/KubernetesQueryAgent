"""
1. List all persistent volume claims in the 'default' namespace.
2. Show details of the PVC named 'my-pvc'.
3. What is the status of the PVC 'my-pvc'?
4. Which workloads are using the PVC 'my-pvc'?
5. Get the storage class associated with 'my-pvc'.
6. What is the capacity requested by 'my-pvc'?
7. Show PVCs that are bound to Persistent Volumes.
8. List PVCs with label app=database.
9. Are there any PVCs not used by any workloads?
10. Get the access modes of the PVC 'my-pvc'.
11. Which Persistent Volume is 'my-pvc' bound to?
12. Show PVCs using storage class 'fast-storage'.
13. What annotations are set on 'my-pvc' PVC?
14. Get the creation time of the PVC 'my-pvc'.
15. Find all PVCs in 'default' namespace larger than 10Gi.
16. List PVCs in the 'production' namespace with capacity greater than '5Gi'.
17. Show all PVCs using storage class 'standard'.
18. What is the storage class of PVC 'data-pvc'?
19. Find PVCs that are not bound to any Persistent Volume.
20. Get PVCs with access mode 'ReadWriteMany' in 'default' namespace.

"""
from typing import Optional, Dict, List
from kubernetes import client
from ..kubernetes_client import KubernetesBase
import re

class PersistentVolumeClaimResource(KubernetesBase):
    def __init__(self, namespace: Optional[str] = "default", labels: Optional[Dict[str, str]] = None):
        super().__init__(namespace, labels)
        self.api = client.CoreV1Api()  # CoreV1Api client for PVCs

    def list_pvcs(self) -> str:
        """List all PVCs in the namespace."""
        try:
            pvcs = self.api.list_namespaced_persistent_volume_claim(namespace=self.namespace, label_selector=self.label_selector)
            if not pvcs.items:
                return "No persistent volume claims found."

            pvc_list = [pvc.metadata.name for pvc in pvcs.items]
            return ", ".join(pvc_list)
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error listing persistent volume claims"

    def get_pvc_details(self, pvc_name: str) -> str:
        """Retrieve detailed information about a specific PVC."""
        try:
            pvc = self.api.read_namespaced_persistent_volume_claim(name=pvc_name, namespace=self.namespace)
            details = f"PVC '{pvc_name}' details:\n"
            details += f"  Status: {pvc.status.phase}\n"
            details += f"  Storage Class: {pvc.spec.storage_class_name}\n"
            capacity = pvc.status.capacity.get('storage') if pvc.status.capacity else 'N/A'
            details += f"  Capacity: {capacity}\n"
            access_modes = pvc.status.access_modes if pvc.status.access_modes else 'N/A'
            details += f"  Access Modes: {access_modes}\n"
            volume_name = pvc.spec.volume_name or 'N/A'
            details += f"  Bound Volume: {volume_name}"
            return details
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error retrieving PVC details"

    def get_pvc_status(self, pvc_name: str) -> str:
        """Get the status of a PVC."""
        try:
            pvc = self.api.read_namespaced_persistent_volume_claim(name=pvc_name, namespace=self.namespace)
            status = pvc.status.phase
            return f"PVC '{pvc_name}' status: {status}"
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error retrieving PVC status"

    def get_workloads_using_pvc(self, pvc_name: str) -> str:
        """Find workloads that are using a specific PVC."""
        try:
            apps_api = client.AppsV1Api()
            core_api = client.CoreV1Api()

            # List all workloads in the namespace
            deployments = apps_api.list_namespaced_deployment(namespace=self.namespace).items
            statefulsets = apps_api.list_namespaced_stateful_set(namespace=self.namespace).items
            daemonsets = apps_api.list_namespaced_daemon_set(namespace=self.namespace).items
            pods = core_api.list_namespaced_pod(namespace=self.namespace).items

            workloads_using_pvc = []

            for d in deployments:
                if self._uses_pvc(d.spec.template.spec, pvc_name):
                    workloads_using_pvc.append(f"Deployment/{d.metadata.name}")

            for s in statefulsets:
                if self._uses_pvc(s.spec.template.spec, pvc_name):
                    workloads_using_pvc.append(f"StatefulSet/{s.metadata.name}")

            for ds in daemonsets:
                if self._uses_pvc(ds.spec.template.spec, pvc_name):
                    workloads_using_pvc.append(f"DaemonSet/{ds.metadata.name}")

            # Optionally include pods not managed by higher-level controllers
            for p in pods:
                if not p.metadata.owner_references:
                    if self._uses_pvc(p.spec, pvc_name):
                        workloads_using_pvc.append(f"Pod/{p.metadata.name}")

            if workloads_using_pvc:
                return f"Workloads using PVC '{pvc_name}':\n" + "\n".join(workloads_using_pvc)
            else:
                return f"No workloads are using PVC '{pvc_name}'."
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error finding workloads using PVC"

    def _uses_pvc(self, pod_spec, pvc_name: str) -> bool:
        """Helper function to determine if a pod spec uses the PVC."""
        if pod_spec.volumes:
            for volume in pod_spec.volumes:
                if volume.persistent_volume_claim and volume.persistent_volume_claim.claim_name == pvc_name:
                    return True
        return False

    def get_storage_class(self, pvc_name: str) -> str:
        """Get the storage class associated with a PVC."""
        try:
            pvc = self.api.read_namespaced_persistent_volume_claim(name=pvc_name, namespace=self.namespace)
            storage_class = pvc.spec.storage_class_name or 'N/A'
            return f"PVC '{pvc_name}' uses storage class: {storage_class}"
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error retrieving storage class"

    def get_capacity(self, pvc_name: str) -> str:
        """Get the capacity requested by a PVC."""
        try:
            pvc = self.api.read_namespaced_persistent_volume_claim(name=pvc_name, namespace=self.namespace)
            capacity = pvc.status.capacity.get('storage') if pvc.status.capacity else 'N/A'
            return f"PVC '{pvc_name}' capacity: {capacity}"
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error retrieving PVC capacity"

    def get_access_modes(self, pvc_name: str) -> str:
        """Get the access modes of a PVC."""
        try:
            pvc = self.api.read_namespaced_persistent_volume_claim(name=pvc_name, namespace=self.namespace)
            access_modes = pvc.spec.access_modes or 'N/A'
            return f"PVC '{pvc_name}' access modes: {', '.join(access_modes)}"
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error retrieving access modes"

    def get_bound_pv(self, pvc_name: str) -> str:
        """Get the Persistent Volume that a PVC is bound to."""
        try:
            pvc = self.api.read_namespaced_persistent_volume_claim(name=pvc_name, namespace=self.namespace)
            volume_name = pvc.spec.volume_name or 'N/A'
            return f"PVC '{pvc_name}' is bound to PV: {volume_name}"
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error retrieving bound PV"

    def get_annotations(self, pvc_name: str) -> str:
        """Retrieve annotations associated with a PVC."""
        try:
            pvc = self.api.read_namespaced_persistent_volume_claim(name=pvc_name, namespace=self.namespace)
            annotations = pvc.metadata.annotations
            if annotations:
                annotations_info = "\n".join([f"{k}: {v}" for k, v in annotations.items()])
                return f"PVC '{pvc_name}' annotations:\n{annotations_info}"
            else:
                return f"PVC '{pvc_name}' has no annotations."
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error retrieving PVC annotations"

    def list_pvcs_by_storage_class(self, storage_class_name: str) -> str:
        """List PVCs using a specific storage class."""
        try:
            pvcs = self.api.list_namespaced_persistent_volume_claim(namespace=self.namespace, label_selector=self.label_selector).items
            pvcs_using_sc = [pvc.metadata.name for pvc in pvcs if pvc.spec.storage_class_name == storage_class_name]
            if pvcs_using_sc:
                return f"PVCs using storage class '{storage_class_name}':\n" + "\n".join(pvcs_using_sc)
            else:
                return f"No PVCs are using storage class '{storage_class_name}'."
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error listing PVCs by storage class"

    def get_pvcs_larger_than(self, size: str) -> str:
        """Find all PVCs larger than a specified size (e.g., '10Gi')."""
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

            pvcs = self.api.list_namespaced_persistent_volume_claim(namespace=self.namespace, label_selector=self.label_selector).items
            matching_pvcs = []

            for pvc in pvcs:
                capacity = pvc.status.capacity.get('storage') if pvc.status.capacity else None
                if capacity:
                    pvc_size = parse_size(capacity)
                    if pvc_size > threshold:
                        matching_pvcs.append(f"{pvc.metadata.name} ({capacity})")

            if matching_pvcs:
                return f"PVCs larger than {size}:\n" + "\n".join(matching_pvcs)
            else:
                return f"No PVCs larger than {size} found."
        except Exception as e:
            self.log_error(f"Error processing PVC sizes: {e}")
            return "Error retrieving PVCs by size"
        

def pv_handler(query) -> str:
    # Check if the query is for persistent volume cla
    pvc_resource = PersistentVolumeClaimResource(namespace=query.namespace, labels=query.filters.labels if query.filters else None)

    # Route based on the action specified in the query
    if query.action == "list":
        if query.filters and query.filters.storage_class:
            return pvc_resource.list_pvcs_by_storage_class(query.filters.storage_class)
        elif query.filters and query.filters.size:
            return pvc_resource.get_pvcs_larger_than(query.filters.size)
        else:
            return pvc_resource.list_pvcs()

    elif query.action == "details" and query.specific_name:
        return pvc_resource.get_pvc_details(query.specific_name)

    elif query.action == "status" and query.specific_name:
        return pvc_resource.get_pvc_status(query.specific_name)

    elif query.action == "used_by" and query.specific_name:
        return pvc_resource.get_workloads_using_pvc(query.specific_name)

    elif query.action == "storage_class" and query.specific_name:
        return pvc_resource.get_storage_class(query.specific_name)

    elif query.action == "capacity" and query.specific_name:
        return pvc_resource.get_capacity(query.specific_name)

    elif query.action == "access_modes" and query.specific_name:
        return pvc_resource.get_access_modes(query.specific_name)

    elif query.action == "bound_pv" and query.specific_name:
        return pvc_resource.get_bound_pv(query.specific_name)

    elif query.action == "annotations" and query.specific_name:
        return pvc_resource.get_annotations(query.specific_name)

    else:
        return "Unsupported action or missing required parameters for persistent volume claim."
