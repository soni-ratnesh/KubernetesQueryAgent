"""
1. List all secrets in the 'default' namespace.
2. Show details of the secret named 'my-secret'.
3. What type is the secret 'my-secret'?
4. Which workloads are using the secret 'my-secret'?
5. Get the keys in the secret 'my-secret'.
6. Are there any secrets not used by any workloads?
7. Show secrets used by the deployment 'my-deployment'.
8. List secrets with label app=backend.
9. What annotations are set on 'my-secret'?
10. Get the creation time of the secret 'my-secret'.
11. Which secrets are of type 'kubernetes.io/tls'?
12. Find secrets used as imagePullSecrets in 'default' namespace.
13. Show workloads using secrets as environment variables.
14. List secrets used as volumes in the 'production' namespace.
15. Get secrets of type 'Opaque' not used by any workloads.
16. Which secrets are being used in environment variables?
17. List secrets used as volumes in the 'default' namespace.
18. Show all 'docker-registry' type secrets.
19. What secrets are used by the pod 'my-pod'?
20. Are there any secrets with annotations 'env=production'?
"""


from typing import Optional, Dict, List
from kubernetes import client
from ..kubernetes_client import KubernetesBase

class SecretResource(KubernetesBase):
    def __init__(self, namespace: Optional[str] = "default", labels: Optional[Dict[str, str]] = None):
        super().__init__(namespace, labels)
        self.api = client.CoreV1Api()  # CoreV1Api client for Secrets

    def list_secrets(self) -> str:
        """List all Secrets in the namespace."""
        try:
            secrets = self.api.list_namespaced_secret(namespace=self.namespace, label_selector=self.label_selector)
            if not secrets.items:
                return "No secrets found."

            secret_list = [secret.metadata.name for secret in secrets.items]
            return ", ".join(secret_list)
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error listing secrets"

    def get_secret_details(self, secret_name: str) -> str:
        """Retrieve detailed information about a specific Secret."""
        try:
            secret = self.api.read_namespaced_secret(name=secret_name, namespace=self.namespace)
            data_keys = list(secret.data.keys()) if secret.data else []
            details = f"Secret '{secret_name}' details:\n"
            details += f"  Type: {secret.type}\n"
            details += f"  Data Keys: {', '.join(data_keys)}"
            return details
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error retrieving secret details"

    def get_secret_type(self, secret_name: str) -> str:
        """Get the type of a Secret."""
        try:
            secret = self.api.read_namespaced_secret(name=secret_name, namespace=self.namespace)
            secret_type = secret.type
            return f"Secret '{secret_name}' is of type: {secret_type}"
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error retrieving secret type"

    def get_keys(self, secret_name: str) -> str:
        """Get the keys in a Secret."""
        try:
            secret = self.api.read_namespaced_secret(name=secret_name, namespace=self.namespace)
            keys = list(secret.data.keys()) if secret.data else []
            return f"Secret '{secret_name}' keys: {', '.join(keys)}"
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error retrieving secret keys"

    def get_workloads_using_secret(self, secret_name: str) -> str:
        """Find workloads that are using a specific Secret."""
        try:
            apps_api = client.AppsV1Api()
            core_api = client.CoreV1Api()

            # List all workloads in the namespace
            deployments = apps_api.list_namespaced_deployment(namespace=self.namespace).items
            statefulsets = apps_api.list_namespaced_stateful_set(namespace=self.namespace).items
            daemonsets = apps_api.list_namespaced_daemon_set(namespace=self.namespace).items
            pods = core_api.list_namespaced_pod(namespace=self.namespace).items

            workloads_using_secret = []

            for d in deployments:
                if self._uses_secret(d.spec.template.spec, secret_name):
                    workloads_using_secret.append(f"Deployment/{d.metadata.name}")

            for s in statefulsets:
                if self._uses_secret(s.spec.template.spec, secret_name):
                    workloads_using_secret.append(f"StatefulSet/{s.metadata.name}")

            for ds in daemonsets:
                if self._uses_secret(ds.spec.template.spec, secret_name):
                    workloads_using_secret.append(f"DaemonSet/{ds.metadata.name}")

            # Optionally include pods not managed by higher-level controllers
            for p in pods:
                if not p.metadata.owner_references:
                    if self._uses_secret(p.spec, secret_name):
                        workloads_using_secret.append(f"Pod/{p.metadata.name}")

            if workloads_using_secret:
                return f"Workloads using Secret '{secret_name}':\n" + "\n".join(workloads_using_secret)
            else:
                return f"No workloads are using Secret '{secret_name}'."
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error finding workloads using secret"

    def _uses_secret(self, pod_spec, secret_name: str) -> bool:
        """Helper function to determine if a pod spec uses the Secret."""
        # Check volumes
        if pod_spec.volumes:
            for volume in pod_spec.volumes:
                if volume.secret and volume.secret.secret_name == secret_name:
                    return True

        # Check environment variables
        for container in pod_spec.containers:
            if container.env_from:
                for env_from in container.env_from:
                    if env_from.secret_ref and env_from.secret_ref.name == secret_name:
                        return True
            if container.env:
                for env_var in container.env:
                    if env_var.value_from and env_var.value_from.secret_key_ref and env_var.value_from.secret_key_ref.name == secret_name:
                        return True

        # Check imagePullSecrets
        if pod_spec.image_pull_secrets:
            for image_pull_secret in pod_spec.image_pull_secrets:
                if image_pull_secret.name == secret_name:
                    return True

        return False

    def get_annotations(self, secret_name: str) -> str:
        """Retrieve annotations associated with a Secret."""
        try:
            secret = self.api.read_namespaced_secret(name=secret_name, namespace=self.namespace)
            annotations = secret.metadata.annotations
            if annotations:
                annotations_info = "\n".join([f"{k}: {v}" for k, v in annotations.items()])
                return f"Secret '{secret_name}' annotations:\n{annotations_info}"
            else:
                return f"Secret '{secret_name}' has no annotations."
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error retrieving secret annotations"

    def get_unused_secrets(self) -> str:
        """List Secrets that are not used by any workloads."""
        try:
            secrets = self.api.list_namespaced_secret(namespace=self.namespace, label_selector=self.label_selector).items
            if not secrets:
                return "No secrets found."

            unused_secrets = []
            for secret in secrets:
                workloads_using_secret = self.get_workloads_using_secret(secret.metadata.name)
                if "No workloads are using Secret" in workloads_using_secret:
                    unused_secrets.append(secret.metadata.name)

            if unused_secrets:
                return "Unused Secrets:\n" + "\n".join(unused_secrets)
            else:
                return "All Secrets are used by workloads."
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error retrieving unused secrets"

    def list_secrets_by_type(self, secret_type: str) -> str:
        """List Secrets of a specific type."""
        try:
            secrets = self.api.list_namespaced_secret(namespace=self.namespace, label_selector=self.label_selector).items
            secrets_of_type = [secret.metadata.name for secret in secrets if secret.type == secret_type]
            if secrets_of_type:
                return f"Secrets of type '{secret_type}':\n" + "\n".join(secrets_of_type)
            else:
                return f"No secrets of type '{secret_type}' found."
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error listing secrets by type"

    def get_image_pull_secrets(self) -> str:
        """Find secrets used as imagePullSecrets in the namespace."""
        try:
            core_api = client.CoreV1Api()
            pods = core_api.list_namespaced_pod(namespace=self.namespace).items

            image_pull_secrets = set()

            for pod in pods:
                if pod.spec.image_pull_secrets:
                    for ips in pod.spec.image_pull_secrets:
                        image_pull_secrets.add(ips.name)

            if image_pull_secrets:
                return "Secrets used as imagePullSecrets:\n" + "\n".join(image_pull_secrets)
            else:
                return "No secrets used as imagePullSecrets."
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error retrieving imagePullSecrets"

    def get_workloads_using_secrets_as_env(self) -> str:
        """Find workloads that use secrets as environment variables."""
        try:
            apps_api = client.AppsV1Api()
            core_api = client.CoreV1Api()

            # List all workloads in the namespace
            deployments = apps_api.list_namespaced_deployment(namespace=self.namespace).items
            statefulsets = apps_api.list_namespaced_stateful_set(namespace=self.namespace).items
            daemonsets = apps_api.list_namespaced_daemon_set(namespace=self.namespace).items
            pods = core_api.list_namespaced_pod(namespace=self.namespace).items

            workloads_using_secrets = []

            def uses_secret_env(pod_spec):
                for container in pod_spec.containers:
                    if container.env_from:
                        for env_from in container.env_from:
                            if env_from.secret_ref:
                                return True
                    if container.env:
                        for env_var in container.env:
                            if env_var.value_from and env_var.value_from.secret_key_ref:
                                return True
                return False

            for d in deployments:
                if uses_secret_env(d.spec.template.spec):
                    workloads_using_secrets.append(f"Deployment/{d.metadata.name}")

            for s in statefulsets:
                if uses_secret_env(s.spec.template.spec):
                    workloads_using_secrets.append(f"StatefulSet/{s.metadata.name}")

            for ds in daemonsets:
                if uses_secret_env(ds.spec.template.spec):
                    workloads_using_secrets.append(f"DaemonSet/{ds.metadata.name}")

            # Optionally include pods not managed by higher-level controllers
            for p in pods:
                if not p.metadata.owner_references:
                    if uses_secret_env(p.spec):
                        workloads_using_secrets.append(f"Pod/{p.metadata.name}")

            if workloads_using_secrets:
                return "Workloads using secrets as environment variables:\n" + "\n".join(workloads_using_secrets)
            else:
                return "No workloads are using secrets as environment variables."
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error finding workloads using secrets as environment variables"



def secrets_handler(query) -> str:

    secret_resource = SecretResource(namespace=query.namespace, labels=query.filters.labels if query.filters else None)

    # Route based on the action specified in the query
    if query.action == "list":
        if query.filters and query.filters.secret_type:
            return secret_resource.list_secrets_by_type(query.filters.secret_type)
        else:
            return secret_resource.list_secrets()

    elif query.action == "details" and query.specific_name:
        return secret_resource.get_secret_details(query.specific_name)

    elif query.action == "type" and query.specific_name:
        return secret_resource.get_secret_type(query.specific_name)

    elif query.action == "keys" and query.specific_name:
        return secret_resource.get_keys(query.specific_name)

    elif query.action == "used_by" and query.specific_name:
        return secret_resource.get_workloads_using_secret(query.specific_name)

    elif query.action == "annotations" and query.specific_name:
        return secret_resource.get_annotations(query.specific_name)

    elif query.action == "unused":
        return secret_resource.get_unused_secrets()

    elif query.action == "image_pull_secrets":
        return secret_resource.get_image_pull_secrets()

    elif query.action == "used_as_env":
        return secret_resource.get_workloads_using_secrets_as_env()

    else:
        return "Unsupported action or missing required parameters for secret."
