from .deployment import deployment_handler
from .pod import pod_handler 
from .cronjob import cronjob_handler




def workload_handler(query):
    if query.resource_type=="deployment":
           return deployment_handler(query)
    elif query.resource_type == "pod":
           return pod_handler(query)
    elif query.resource_type == "cronjob":
           return cronjob_handler(query)
    else:
           return "Unknown Resource Type"


    