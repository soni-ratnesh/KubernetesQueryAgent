from .config_maps import config_maps_hamdler


def service_handler(query):

    if query.resource_type == "config_maps":
        return config_maps_hamdler(query)
    
    else:
        return "Unknown Resource Type"