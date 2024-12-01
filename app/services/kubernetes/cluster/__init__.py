from .cluster_role_bindings import crb_handler
from .cluster_roles import cr_handler
from .event import event_handler
from .namespace import namespace_handler
from .network_policy import np_handler
from .nodes import nodes_handler
from .persistent_volume import pv_handler
from .role_bindings import rb_handler
from .roles import roles_handler


def cluster_handler(query):
    if  query.resource_type == "cluster_role_bindings":
        return crb_handler(query)

    elif query.resource_type == "cluster_role":
        return cr_handler(query)
    
    elif query.resource_type == "event":
        return event_handler(query)
    
    elif query.resource_type == "namespace":
        return namespace_handler(query)
    
    elif query.resource_type == "network_policy":
        return np_handler(query)
    
    elif query.resource_type == "node":
        return nodes_handler(query)
    
    elif query.resource_type == "persistent_volume" :
        return pv_handler(query)
    
    elif query.resource_type == "role_binding" :
        return rb_handler(query)
    
    elif query.resource_type == "role":
        return roles_handler(query)
    

    
    else:
        return "Unknown Resource Type"
    