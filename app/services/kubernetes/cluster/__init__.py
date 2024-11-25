from .cluster_role_bindings import crb_handler
from .cluster_roles import cr_handler



def cluster_handler(query):
    if  query.resource_type == "cluster_role_bindings":
        return crb_handler(query)

    elif query.resource_type == "cluster_role":
        return cr_handler(query)
    

    



    

    

    

    
    else:
        return "Unknown Resource Type"
    