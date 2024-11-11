from .deployment import deployment_handler
from .pod import pod_handler 
from .cronjob import cronjob_handler
from .daemonset import daemonset_handler
from .job import job_handler
from .replicaset import replicaset_handler
from .statefulset import statefulset_handler

def workload_handler(query):
    if query.resource_type=="deployment":
           return deployment_handler(query)
    elif query.resource_type == "pod":
           return pod_handler(query)
    elif query.resource_type == "cronjob":
           return cronjob_handler(query)
    elif query.resource_type == "daemonset":
           return daemonset_handler(query)
    elif query.resource_type == "job":
           return job_handler(query)
    elif query.resource_type == "replicaset":
           return replicaset_handler(query)
    elif query.resource_type == "statefulset":
           return statefulset_handler(query)
    else:
           return "Unknown Resource Type"
    