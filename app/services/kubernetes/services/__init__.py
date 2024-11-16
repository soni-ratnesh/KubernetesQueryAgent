from .ingress import ingress_handler
from .ingress_classes import ingress_class_handler
from .service import service_resource_handler

def service_handler(query):

    if query.resource_type == "ingress":
        return ingress_handler(query)

    elif query.resource_type == "ingress_class":
        return ingress_class_handler(query)
    
    elif query.resource_type == "service":
        return service_resource_handler(query)
    
    else:
        return "Unknown Resource Type"