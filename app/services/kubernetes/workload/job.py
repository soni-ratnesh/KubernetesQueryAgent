from app.services.kubernetes.kubernetes_client import KubernetesBase

from kubernetes import client
from typing import Optional, Dict

class JobResource(KubernetesBase):
    def __init__(self, namespace: Optional[str] = "default", labels: Optional[Dict[str, str]] = None):
        super().__init__(namespace, labels)
        self.api = client.BatchV1Api()  # BatchV1Api client for Jobs

    def list_jobs(self) -> str:
        """List all jobs in the namespace with basic details."""
        try:
            jobs = self.api.list_namespaced_job(namespace=self.namespace, label_selector=self.label_selector)
            if not jobs.items:
                return "No jobs found."

            job_list = []
            for job in jobs.items:
                simple_name = "-".join(job.metadata.name.split("-")[:-2])  # Remove unique identifier suffixes
                status = "Running" if job.status.active else "Succeeded" if job.status.succeeded else "Failed"
                job_info = f"{simple_name} (Status: {status})"
                job_list.append(job_info)

            return ", ".join(job_list)
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error listing jobs"

    def get_job_status(self, job_name: str) -> str:
        """Retrieve the status of a specific job (Succeeded, Failed, Running)."""
        try:
            job = self.api.read_namespaced_job(name=job_name, namespace=self.namespace)
            if job.status.succeeded:
                return "Succeeded"
            elif job.status.failed:
                return "Failed"
            elif job.status.active:
                return "Running"
            return "Unknown"
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error retrieving job status"

    def get_last_execution_time(self, job_name: str) -> str:
        """Retrieve the last execution time of a job."""
        try:
            job = self.api.read_namespaced_job(name=job_name, namespace=self.namespace)
            if job.status.completion_time:
                return f"Last executed on {job.status.completion_time}"
            elif job.status.start_time:
                return f"Job started on {job.status.start_time}, but has not completed yet."
            return "No execution time available"
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error retrieving job execution time"

    def get_job_details(self, job_name: str) -> str:
        """Retrieve comprehensive details about a job, such as start time, completion time, and completions."""
        try:
            job = self.api.read_namespaced_job(name=job_name, namespace=self.namespace)
            start_time = job.status.start_time or "Not started"
            completion_time = job.status.completion_time or "Not completed"
            completions = job.status.succeeded or 0
            active = job.status.active or 0
            failed = job.status.failed or 0

            details = (
                f"Job '{job_name}':\n"
                f"  Start Time: {start_time}\n"
                f"  Completion Time: {completion_time}\n"
                f"  Succeeded Completions: {completions}\n"
                f"  Active Pods: {active}\n"
                f"  Failed Pods: {failed}\n"
            )
            return details
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error retrieving job details"
    def get_pods_for_job(self, job_name: str) -> str:
        try:
            # Step 1: Fetch the job and retrieve its label selector
            job = self.api.read_namespaced_job(name=job_name, namespace=self.namespace)
            if not job.spec.selector:
                return f"No selector found for job '{job_name}'."

            # Convert the job's selector to a label selector string
            label_selector = ",".join([f"{k}={v}" for k, v in job.spec.selector.match_labels.items()])

            # Step 2: List pods using the job's label selector
            pods = self.core_v1_api.list_namespaced_pod(namespace=self.namespace, label_selector=label_selector)
            if not pods.items:
                return f"No pods found for job '{job_name}'."

            # Remove identifiers from pod names and prepare the result
            pod_names = ["-".join(pod.metadata.name.split("-")[:-2]) for pod in pods.items]
            unique_pod_names = set(pod_names)  # Use a set to remove duplicates

            # Return a comma-separated string of pod names
            return ", ".join(unique_pod_names)
        except client.ApiException as e:
            self.log_error(f"Kubernetes API exception: {e}")
            return "Error fetching pods for job"
