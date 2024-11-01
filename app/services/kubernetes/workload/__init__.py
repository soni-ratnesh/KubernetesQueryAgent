from .deployment import deployment_handler


def workload_handler(query):
    if query.resource_type=="deployment":
           return deployment_handler(query)
    else:
           return "Unknown Resource Type"


    