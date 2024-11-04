from app.services.kubernetes.kubernetes_client import KubernetesBase
from kubernetes import client
from typing import Optional, Dict

class CronJobResource(KubernetesBase):
    def __init__(self, namespace: Optional[str] = "default", labels: Optional[Dict[str, str]] = None):
        super().__init__(namespace, labels)
        self.api = client.BatchV1beta1Api()  # BatchV1beta1Api client for CronJobs
        self.core_v1_api = client.CoreV1Api()  # CoreV1Api for fetching pods associated with CronJobs

    def list_cronjobs(self) -> str:
        """List all CronJobs in the namespace with basic details."""
        try:
            cronjobs = self.api.list_namespaced_cron_job(namespace=self.namespace, label_selector=self.label_selector)
            if not cronjobs.items:
                return "No cronjobs found."

            cronjob_list = []
            for cronjob in cronjobs.items:
                simple_name = "-".join(cronjob.metadata.name.split("-")[:-2])  # Remove unique identifier suffixes
                schedule = cronjob.spec.schedule
                cronjob_info = f"{simple_name} (Schedule: {schedule})"
                cronjob_list.append(cronjob_info)

            return ", ".join(cronjob_list)
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error listing cronjobs"

    def get_cronjob_status(self, cronjob_name: str) -> str:
        """Check if a CronJob is active, succeeded, or failed."""
        try:
            cronjob = self.api.read_namespaced_cron_job(name=cronjob_name, namespace=self.namespace)
            active_jobs = len(cronjob.status.active) if cronjob.status.active else 0
            last_schedule_time = cronjob.status.last_schedule_time

            if active_jobs > 0:
                return f"Active with {active_jobs} running instance(s)."
            elif last_schedule_time:
                return f"Last scheduled at {last_schedule_time}"
            return "Inactive"
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error retrieving cronjob status"

    def get_next_scheduled_run(self, cronjob_name: str) -> str:
        """Calculate the next scheduled run time for a CronJob."""
        try:
            cronjob = self.api.read_namespaced_cron_job(name=cronjob_name, namespace=self.namespace)
            schedule = cronjob.spec.schedule

            # Convert schedule to human-readable format
            # NOTE: To calculate next scheduled time accurately, a cron library would be ideal.
            return f"Scheduled to run according to '{schedule}'"
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error retrieving next scheduled run for cronjob"

    def get_last_scheduled_run(self, cronjob_name: str) -> str:
        """Retrieve the last scheduled run time of a CronJob."""
        try:
            cronjob = self.api.read_namespaced_cron_job(name=cronjob_name, namespace=self.namespace)
            last_schedule_time = cronjob.status.last_schedule_time
            if last_schedule_time:
                return f"Last scheduled at {last_schedule_time}"
            return "No runs found for this CronJob."
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error retrieving last scheduled run for cronjob"

    def get_pods_for_cronjob(self, cronjob_name: str) -> str:
        """Retrieve all pods spawned by the most recent Job of a CronJob."""
        try:
            # Step 1: Fetch the CronJob to retrieve its label selector
            cronjob = self.api.read_namespaced_cron_job(name=cronjob_name, namespace=self.namespace)
            label_selector = ",".join([f"{k}={v}" for k, v in cronjob.spec.job_template.spec.selector.match_labels.items()])

            # Step 2: List jobs associated with the CronJob's label selector
            jobs = self.api.list_namespaced_job(namespace=self.namespace, label_selector=label_selector)
            if not jobs.items:
                return f"No jobs found for cronjob '{cronjob_name}'."

            # Step 3: Get pods associated with the most recent job
            recent_job = sorted(jobs.items, key=lambda job: job.status.start_time, reverse=True)[0]
            pod_label_selector = ",".join([f"{k}={v}" for k, v in recent_job.spec.selector.match_labels.items()])
            pods = self.core_v1_api.list_namespaced_pod(namespace=self.namespace, label_selector=pod_label_selector)
            if not pods.items:
                return f"No pods found for the most recent job of cronjob '{cronjob_name}'."

            # Remove identifiers from pod names and prepare the result
            pod_names = ["-".join(pod.metadata.name.split("-")[:-2]) for pod in pods.items]
            unique_pod_names = set(pod_names)  # Use a set to remove duplicates

            # Return a comma-separated string of pod names
            return ", ".join(unique_pod_names)
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error fetching pods for cronjob"

def cronjob_handler(query):
    cronjob_resource = CronJobResource(namespace=query.namespace)
        
    # Route based on the action specified in the query
    if query.action == "list":
        return cronjob_resource.list_cronjobs()
    
    elif query.action == "status" and query.specific_name:
        status = cronjob_resource.get_cronjob_status(query.specific_name)
        return f"Status of cronjob '{query.specific_name}': {status}"
    
    elif query.action == "next_run" and query.specific_name:
        next_run = cronjob_resource.get_next_scheduled_run(query.specific_name)
        return f"Next scheduled run for cronjob '{query.specific_name}': {next_run}"
    
    elif query.action == "last_run" and query.specific_name:
        last_run = cronjob_resource.get_last_scheduled_run(query.specific_name)
        return f"Last scheduled run for cronjob '{query.specific_name}': {last_run}"
    
    elif query.action == "pods" and query.specific_name:
        pods = cronjob_resource.get_pods_for_cronjob(query.specific_name)
        return f"Pods for cronjob '{query.specific_name}': {pods}"
    
    else:
        return "Unsupported action or missing required parameters for cronjob."
