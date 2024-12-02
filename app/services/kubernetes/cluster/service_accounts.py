"""
1. List all service accounts in the 'default' namespace.
2. Show details of the service account named 'my-service-account'.
3. Which secrets are associated with service account 'default'?
4. Find service accounts with annotations 'team=backend' in 'production'.
5. What is the image pull secret for service account 'registry-access'?
6. Show service accounts with label 'environment=testing'.
7. Are there any service accounts without secrets?
8. List service accounts in namespace 'kube-system'.
9. What tokens are associated with service account 'my-service-account'?
10. Show annotations for service account 'builder' in 'development'.
11. Which service accounts are used by deployments in 'staging'?
12. Find service accounts with automount of tokens disabled.
13. What is the default service account in 'default' namespace?
14. List service accounts with image pull secrets.
15. Show service accounts that are used by pods in 'production'.
16. Get the creation time of service account 'monitoring'.
17. Which service accounts have no tokens?
18. Find service accounts with label 'app=frontend'.
19. Show service accounts with custom secrets.
20. List service accounts used in 'secure' namespace.
"""

from typing import Optional, Dict
from kubernetes import client
from ..kubernetes_client import KubernetesBase

class ServiceAccountResource(KubernetesBase):
    def __init__(self, namespace: Optional[str] = "default", labels: Optional[Dict[str, str]] = None):
        super().__init__(namespace=namespace, labels=labels)
        self.api = client.CoreV1Api()  # CoreV1Api client for ServiceAccounts

    def list_service_accounts(self) -> str:
        """List all ServiceAccounts in the namespace."""
        try:
            sas = self.api.list_namespaced_service_account(namespace=self.namespace, label_selector=self.label_selector)
            if not sas.items:
                return f"No service accounts found in namespace '{self.namespace}'."

            sa_list = [sa.metadata.name for sa in sas.items]
            return f"ServiceAccounts in namespace '{self.namespace}':\n" + "\n".join(sa_list)
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return f"Error listing service accounts in namespace '{self.namespace}'"

    def get_service_account_details(self, sa_name: str) -> str:
        """Retrieve detailed information about a specific ServiceAccount."""
        try:
            sa = self.api.read_namespaced_service_account(name=sa_name, namespace=self.namespace)
            details = f"ServiceAccount '{sa_name}' details in namespace '{self.namespace}':\n"
            secrets = sa.secrets or []
            secrets_info = ", ".join([secret.name for secret in secrets]) if secrets else 'None'
            details += f"  Secrets: {secrets_info}\n"
            image_pull_secrets = sa.image_pull_secrets or []
            ips_info = ", ".join([ips.name for ips in image_pull_secrets]) if image_pull_secrets else 'None'
            details += f"  Image Pull Secrets: {ips_info}\n"
            details += f"  Automount Service Account Token: {sa.automount_service_account_token}\n"
            return details
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return f"Error retrieving details for service account '{sa_name}' in namespace '{self.namespace}'"

    def get_sa_annotations(self, sa_name: str) -> str:
        """Retrieve annotations associated with a ServiceAccount."""
        try:
            sa = self.api.read_namespaced_service_account(name=sa_name, namespace=self.namespace)
            annotations = sa.metadata.annotations or {}
            if annotations:
                annotations_info = "\n".join([f"{k}: {v}" for k, v in annotations.items()])
                return f"Annotations for ServiceAccount '{sa_name}' in namespace '{self.namespace}':\n{annotations_info}"
            else:
                return f"No annotations found for service account '{sa_name}' in namespace '{self.namespace}'."
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return f"Error retrieving annotations for service account '{sa_name}' in namespace '{self.namespace}'"

    def find_sas_without_secrets(self) -> str:
        """Find ServiceAccounts that have no secrets."""
        try:
            sas = self.api.list_namespaced_service_account(namespace=self.namespace).items
            sas_without_secrets = [sa.metadata.name for sa in sas if not sa.secrets]
            if sas_without_secrets:
                return f"ServiceAccounts without secrets in namespace '{self.namespace}':\n" + "\n".join(sas_without_secrets)
            else:
                return f"All ServiceAccounts have secrets in namespace '{self.namespace}'."
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return f"Error finding service accounts without secrets in namespace '{self.namespace}'"

    def list_sas_with_image_pull_secrets(self) -> str:
        """List ServiceAccounts that have image pull secrets."""
        try:
            sas = self.api.list_namespaced_service_account(namespace=self.namespace).items
            sas_with_ips = [sa.metadata.name for sa in sas if sa.image_pull_secrets]
            if sas_with_ips:
                return f"ServiceAccounts with image pull secrets in namespace '{self.namespace}':\n" + "\n".join(sas_with_ips)
            else:
                return f"No ServiceAccounts with image pull secrets found in namespace '{self.namespace}'."
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return f"Error listing service accounts with image pull secrets in namespace '{self.namespace}'"



def sa_handler(query) -> str:
    sa_resource = ServiceAccountResource(
        namespace=query.namespace or "default",
        labels=query.filters.labels if query.filters else None
    )

    # Route based on the action specified in the query
    if query.action == "list":
        return sa_resource.list_service_accounts()

    elif query.action == "details" and query.specific_name:
        return sa_resource.get_service_account_details(query.specific_name)

    elif query.action == "annotations" and query.specific_name:
        return sa_resource.get_sa_annotations(query.specific_name)

    elif query.action == "find_without_secrets":
        return sa_resource.find_sas_without_secrets()

    elif query.action == "list_with_image_pull_secrets":
        return sa_resource.list_sas_with_image_pull_secrets()

    else:
        return "Unsupported action or missing required parameters for service account."
