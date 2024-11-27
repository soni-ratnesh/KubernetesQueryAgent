from .cluster_role_bindings import crb_handler
from .cluster_roles import cr_handler
from .event import event_handler
from .namespace import namespace_handler



def cluster_handler(query):
    if  query.resource_type == "cluster_role_bindings":
        return crb_handler(query)

    elif query.resource_type == "cluster_role":
        return cr_handler(query)
    
    elif query.resource_type == "event":
        return event_handler(query)
    
    elif query.resource_type == "namespace":
        return namespace_handler(query)
    


    

    

    

    
    else:
        return "Unknown Resource Type"
    