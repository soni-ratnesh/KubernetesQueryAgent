"""
1. List all configmaps in the 'default' namespace.
2. Show details of the configmap named 'my-config'.
3. What are the keys in 'my-config' configmap?
4. Which workloads are using the configmap 'my-config'?
5. Get the workloads that mount 'my-config' as a volume.
6. Show configmaps used by the deployment 'my-deployment'.
7. Are there any configmaps not used by any workloads?
8. What annotations are set on 'my-config' configmap?
9. List configmaps with label app=frontend.
10. Get the creation time of the configmap 'my-config'.
11. List unused configmaps in the 'production' namespace.
12. Which pods are using the configmap 'config-app'?

"""
from typing import Optional, Dict
from kubernetes import client
from ..kubernetes_client import KubernetesBase

class ConfigMapResource(KubernetesBase):
    def __init__(self, namespace: Optional[str] = "default", labels: Optional[Dict[str, str]] = None):
        super().__init__(namespace, labels)
        self.api = client.CoreV1Api()  # CoreV1Api client for ConfigMaps

    def list_configmaps(self) -> str:
        """List all ConfigMaps in the namespace."""
        try:
            configmaps = self.api.list_namespaced_config_map(namespace=self.namespace, label_selector=self.label_selector)
            if not configmaps.items:
                return "No configmaps found."

            configmap_list = [cm.metadata.name for cm in configmaps.items]
            return ", ".join(configmap_list)
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error listing configmaps"

    def get_configmap_details(self, configmap_name: str) -> str:
        """Retrieve detailed information about a specific ConfigMap."""
        try:
            configmap = self.api.read_namespaced_config_map(name=configmap_name, namespace=self.namespace)
            data = configmap.data or {}
            data_info = "\n".join([f"{k}: {v}" for k, v in data.items()])
            return f"ConfigMap '{configmap_name}' details:\nData:\n{data_info}"
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error retrieving configmap details"

    def get_keys(self, configmap_name: str) -> str:
        """Get the keys in a ConfigMap."""
        try:
            configmap = self.api.read_namespaced_config_map(name=configmap_name, namespace=self.namespace)
            keys = list(configmap.data.keys()) if configmap.data else []
            return f"ConfigMap '{configmap_name}' keys: {', '.join(keys)}"
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error retrieving configmap keys"

    def get_workloads_using_configmap(self, configmap_name: str) -> str:
        """Find workloads that are using a specific ConfigMap."""
        try:
            apps_api = client.AppsV1Api()
            core_api = client.CoreV1Api()

            # List all workloads in the namespace
            deployments = apps_api.list_namespaced_deployment(namespace=self.namespace).items
            statefulsets = apps_api.list_namespaced_stateful_set(namespace=self.namespace).items
            daemonsets = apps_api.list_namespaced_daemon_set(namespace=self.namespace).items
            pods = core_api.list_namespaced_pod(namespace=self.namespace).items

            workloads_using_cm = []

            for d in deployments:
                if self._uses_configmap(d.spec.template.spec, configmap_name):
                    workloads_using_cm.append(f"Deployment/{d.metadata.name}")

            for s in statefulsets:
                if self._uses_configmap(s.spec.template.spec, configmap_name):
                    workloads_using_cm.append(f"StatefulSet/{s.metadata.name}")

            for ds in daemonsets:
                if self._uses_configmap(ds.spec.template.spec, configmap_name):
                    workloads_using_cm.append(f"DaemonSet/{ds.metadata.name}")

            # Optionally include pods not managed by higher-level controllers
            for p in pods:
                if not p.metadata.owner_references:
                    if self._uses_configmap(p.spec, configmap_name):
                        workloads_using_cm.append(f"Pod/{p.metadata.name}")

            if workloads_using_cm:
                return f"Workloads using ConfigMap '{configmap_name}':\n" + "\n".join(workloads_using_cm)
            else:
                return f"No workloads are using ConfigMap '{configmap_name}'."
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error finding workloads using configmap"

    def _uses_configmap(self, pod_spec, configmap_name: str) -> bool:
        """Helper function to determine if a pod spec uses the ConfigMap."""
        # Check volumes
        if pod_spec.volumes:
            for volume in pod_spec.volumes:
                if volume.config_map and volume.config_map.name == configmap_name:
                    return True

        # Check environment variables
        for container in pod_spec.containers:
            if container.env_from:
                for env_from in container.env_from:
                    if env_from.config_map_ref and env_from.config_map_ref.name == configmap_name:
                        return True
            if container.env:
                for env_var in container.env:
                    if env_var.value_from and env_var.value_from.config_map_key_ref and env_var.value_from.config_map_key_ref.name == configmap_name:
                        return True

        return False

    def get_annotations(self, configmap_name: str) -> str:
        """Retrieve annotations associated with a ConfigMap."""
        try:
            configmap = self.api.read_namespaced_config_map(name=configmap_name, namespace=self.namespace)
            annotations = configmap.metadata.annotations
            if annotations:
                annotations_info = "\n".join([f"{k}: {v}" for k, v in annotations.items()])
                return f"ConfigMap '{configmap_name}' annotations:\n{annotations_info}"
            else:
                return f"ConfigMap '{configmap_name}' has no annotations."
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error retrieving configmap annotations"

    def get_unused_configmaps(self) -> str:
        """List ConfigMaps that are not used by any workloads."""
        try:
            configmaps = self.api.list_namespaced_config_map(namespace=self.namespace, label_selector=self.label_selector).items
            if not configmaps:
                return "No configmaps found."

            unused_configmaps = []
            for cm in configmaps:
                workloads_using_cm = self.get_workloads_using_configmap(cm.metadata.name)
                if "No workloads are using ConfigMap" in workloads_using_cm:
                    unused_configmaps.append(cm.metadata.name)

            if unused_configmaps:
                return "Unused ConfigMaps:\n" + "\n".join(unused_configmaps)
            else:
                return "All ConfigMaps are used by workloads."
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error retrieving unused configmaps"



def config_maps_hamdler(query) -> str:
    configmap_resource = ConfigMapResource(namespace=query.namespace, labels=query.filters.labels if query.filters else None)

    # Route based on the action specified in the query
    if query.action == "list":
        return configmap_resource.list_configmaps()

    elif query.action == "details" and query.specific_name:
        return configmap_resource.get_configmap_details(query.specific_name)

    elif query.action == "keys" and query.specific_name:
        return configmap_resource.get_keys(query.specific_name)

    elif query.action == "used_by" and query.specific_name:
        return configmap_resource.get_workloads_using_configmap(query.specific_name)

    elif query.action == "annotations" and query.specific_name:
        return configmap_resource.get_annotations(query.specific_name)

    elif query.action == "unused":
        return configmap_resource.get_unused_configmaps()

    else:
        return "Unsupported action or missing required parameters for configmap."

