"""
1. List all namespaces in the cluster.
2. Show details of the namespace 'production'.
3. What resources are running in the namespace 'staging'?
4. List all pods in the namespace 'development'.
5. What is the status of the namespace 'testing'?
6. Find namespaces with label 'environment=production'.
7. Show annotations for the namespace 'kube-system'.
8. Which namespaces have active workloads?
9. Are there any empty namespaces in the cluster?
10. Get the resource quotas set for the namespace 'development'.
11. What are the network policies applied in the namespace 'secure'?
12. List all services in the namespace 'frontend'.
13. Find namespaces without any deployments.
14. Show events related to the namespace 'production'.
15. Which namespaces are terminating?
16. Get the list of namespaces with annotations 'team=backend'.
17. Find namespaces without any pods.
18. What is the creation time of the namespace 'default'?
19. Show labels for the namespace 'staging'.
20. List namespaces used for testing purposes.
"""

from typing import Optional, Dict
from kubernetes import client
from..kubernetes_client import KubernetesBase

class NamespaceResource(KubernetesBase):
    def __init__(self, labels: Optional[Dict[str, str]] = None):
        super().__init__(labels=labels)  # Namespaces are cluster-scoped
        self.core_api = client.CoreV1Api()  # CoreV1Api client for Namespaces
        self.apps_api = client.AppsV1Api()
        self.extensions_api = client.ExtensionsV1beta1Api()
        self.batch_api = client.BatchV1Api()
        self.networking_api = client.NetworkingV1Api()

    def list_namespaces(self) -> str:
        """List all namespaces in the cluster."""
        try:
            namespaces = self.core_api.list_namespace(label_selector=self.label_selector)
            if not namespaces.items:
                return "No namespaces found."

            namespace_list = [ns.metadata.name for ns in namespaces.items]
            return ", ".join(namespace_list)
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error listing namespaces"

    def get_namespace_details(self, namespace_name: str) -> str:
        """Retrieve detailed information about a specific Namespace."""
        try:
            ns = self.core_api.read_namespace(name=namespace_name)
            details = f"Namespace '{namespace_name}' details:\n"
            details += f"  Status: {ns.status.phase}\n"
            annotations = ns.metadata.annotations or {}
            annotations_info = "\n".join([f"    {k}: {v}" for k, v in annotations.items()])
            details += f"  Annotations:\n{annotations_info if annotations_info else '    None'}\n"
            labels = ns.metadata.labels or {}
            labels_info = ", ".join([f"{k}={v}" for k, v in labels.items()])
            details += f"  Labels: {labels_info if labels_info else 'None'}"
            return details
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return f"Error retrieving namespace '{namespace_name}' details"

    def get_resources_in_namespace(self, namespace_name: str) -> str:
        """List resources running in a specific Namespace."""
        try:


            pods = self.core_api.list_namespaced_pod(namespace=namespace_name).items
            services = self.core_api.list_namespaced_service(namespace=namespace_name).items
            deployments = self.apps_api.list_namespaced_deployment(namespace=namespace_name).items
            statefulsets = self.apps_api.list_namespaced_stateful_set(namespace=namespace_name).items
            daemonsets = self.apps_api.list_namespaced_daemon_set(namespace=namespace_name).items
            jobs = self.batch_api.list_namespaced_job(namespace=namespace_name).items
            cronjobs = self.batch_api.list_namespaced_cron_job(namespace=namespace_name).items
            network_policies = self.networking_api.list_namespaced_network_policy(namespace=namespace_name).items

            resources_info = f"Resources in namespace '{namespace_name}':\n"
            resources_info += f"  Pods: {[pod.metadata.name for pod in pods]}\n"
            resources_info += f"  Services: {[svc.metadata.name for svc in services]}\n"
            resources_info += f"  Deployments: {[dep.metadata.name for dep in deployments]}\n"
            resources_info += f"  StatefulSets: {[sts.metadata.name for sts in statefulsets]}\n"
            resources_info += f"  DaemonSets: {[ds.metadata.name for ds in daemonsets]}\n"
            resources_info += f"  Jobs: {[job.metadata.name for job in jobs]}\n"
            resources_info += f"  CronJobs: {[cj.metadata.name for cj in cronjobs]}\n"
            resources_info += f"  Network Policies: {[np.metadata.name for np in network_policies]}"
            return resources_info
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return f"Error retrieving resources in namespace '{namespace_name}'"

    def get_namespace_status(self, namespace_name: str) -> str:
        """Get the status of a Namespace."""
        try:
            ns = self.core_api.read_namespace(name=namespace_name)
            status = ns.status.phase
            return f"Namespace '{namespace_name}' status: {status}"
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return f"Error retrieving status for namespace '{namespace_name}'"

    def find_namespaces_with_label(self, label_selector: str) -> str:
        """Find Namespaces with a specific label."""
        try:
            namespaces = self.core_api.list_namespace(label_selector=label_selector).items
            if namespaces:
                ns_list = [ns.metadata.name for ns in namespaces]
                return f"Namespaces with label '{label_selector}':\n" + "\n".join(ns_list)
            else:
                return f"No namespaces found with label '{label_selector}'."
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return f"Error finding namespaces with label '{label_selector}'"

    def get_annotations(self, namespace_name: str) -> str:
        """Retrieve annotations associated with a Namespace."""
        try:
            ns = self.core_api.read_namespace(name=namespace_name)
            annotations = ns.metadata.annotations
            if annotations:
                annotations_info = "\n".join([f"{k}: {v}" for k, v in annotations.items()])
                return f"Namespace '{namespace_name}' annotations:\n{annotations_info}"
            else:
                return f"Namespace '{namespace_name}' has no annotations."
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return f"Error retrieving annotations for namespace '{namespace_name}'"

    def find_empty_namespaces(self) -> str:
        """Find Namespaces without any workloads."""
        try:
            namespaces = self.core_api.list_namespace().items
            empty_namespaces = []
            for ns in namespaces:
                namespace_name = ns.metadata.name
                core_api = client.CoreV1Api()
                apps_api = client.AppsV1Api()
                pods = core_api.list_namespaced_pod(namespace=namespace_name).items
                deployments = apps_api.list_namespaced_deployment(namespace=namespace_name).items
                statefulsets = apps_api.list_namespaced_stateful_set(namespace=namespace_name).items
                daemonsets = apps_api.list_namespaced_daemon_set(namespace=namespace_name).items
                jobs = client.BatchV1Api().list_namespaced_job(namespace=namespace_name).items
                if not (pods or deployments or statefulsets or daemonsets or jobs):
                    empty_namespaces.append(namespace_name)
            if empty_namespaces:
                return "Empty Namespaces (no workloads):\n" + "\n".join(empty_namespaces)
            else:
                return "All namespaces have workloads."
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error finding empty namespaces"

    def get_resource_quotas(self, namespace_name: str) -> str:
        """Get the resource quotas set for a Namespace."""
        try:
            quotas = self.core_api.list_namespaced_resource_quota(namespace=namespace_name).items
            if quotas:
                quota_info = ""
                for quota in quotas:
                    quota_info += f"ResourceQuota '{quota.metadata.name}':\n"
                    hard = quota.status.hard or {}
                    used = quota.status.used or {}
                    for resource, value in hard.items():
                        used_value = used.get(resource, '0')
                        quota_info += f"  {resource}: Used {used_value} / Hard {value}\n"
                return f"Resource Quotas for namespace '{namespace_name}':\n{quota_info}"
            else:
                return f"No resource quotas set for namespace '{namespace_name}'."
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return f"Error retrieving resource quotas for namespace '{namespace_name}'"

    def get_network_policies(self, namespace_name: str) -> str:
        """List the network policies applied in a Namespace."""
        try:
            policies = self.networking_api.list_namespaced_network_policy(namespace=namespace_name).items
            if policies:
                policy_names = [policy.metadata.name for policy in policies]
                return f"Network Policies in namespace '{namespace_name}':\n" + "\n".join(policy_names)
            else:
                return f"No network policies found in namespace '{namespace_name}'."
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return f"Error retrieving network policies for namespace '{namespace_name}'"

    def get_namespace_events(self, namespace_name: str) -> str:
        """List events related to a Namespace."""
        try:
            events = self.core_api.list_namespaced_event(namespace=namespace_name).items
            if not events:
                return f"No events found in namespace '{namespace_name}'."

            event_list = []
            for event in events:
                timestamp = event.last_timestamp or event.event_time or event.metadata.creation_timestamp
                timestamp_str = timestamp.strftime('%Y-%m-%d %H:%M:%S') if timestamp else 'N/A'
                message = event.message
                involved_obj = f"{event.involved_object.kind}/{event.involved_object.name}"
                event_info = f"[{timestamp_str}] {event.type} {event.reason} on {involved_obj}: {message}"
                event_list.append(event_info)

            return f"Events in namespace '{namespace_name}':\n" + "\n".join(event_list)
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return f"Error retrieving events for namespace '{namespace_name}'"

    def find_terminating_namespaces(self) -> str:
        """Find Namespaces that are in the Terminating state."""
        try:
            namespaces = self.core_api.list_namespace().items
            terminating_namespaces = [ns.metadata.name for ns in namespaces if ns.status.phase == 'Terminating']
            if terminating_namespaces:
                return "Namespaces in 'Terminating' state:\n" + "\n".join(terminating_namespaces)
            else:
                return "No namespaces are in 'Terminating' state."
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error finding terminating namespaces"



def namespace_handler(query) -> str:
    
    namespace_resource = NamespaceResource(labels=query.filters.labels if query.filters else None)

    # Route based on the action specified in the query
    if query.action == "list":
        if query.filters and query.filters.labels:
            label_selector = ",".join([f"{k}={v}" for k, v in query.filters.labels.items()])
            return namespace_resource.find_namespaces_with_label(label_selector)
        else:
            return namespace_resource.list_namespaces()

    elif query.action == "details" and query.specific_name:
        return namespace_resource.get_namespace_details(query.specific_name)

    elif query.action == "resources" and query.specific_name:
        return namespace_resource.get_resources_in_namespace(query.specific_name)

    elif query.action == "status" and query.specific_name:
        return namespace_resource.get_namespace_status(query.specific_name)

    elif query.action == "annotations" and query.specific_name:
        return namespace_resource.get_annotations(query.specific_name)

    elif query.action == "find_empty":
        return namespace_resource.find_empty_namespaces()

    elif query.action == "resource_quotas" and query.specific_name:
        return namespace_resource.get_resource_quotas(query.specific_name)

    elif query.action == "network_policies" and query.specific_name:
        return namespace_resource.get_network_policies(query.specific_name)

    elif query.action == "events" and query.specific_name:
        return namespace_resource.get_namespace_events(query.specific_name)

    elif query.action == "find_terminating":
        return namespace_resource.find_terminating_namespaces()

    else:
        return "Unsupported action or missing required parameters for namespace."
