from .config_maps import config_maps_hamdler
from .persistent_volume import pv_handler
from .secrets import secrets_handler
from .storage_class import storage_class_handler


def config_storage_handler(query):

    if query.resource_type == "config_maps":
        return config_maps_hamdler(query)
    elif query.resource_type == "pv":
        return pv_handler(query)
    elif query.resource_type == "secrets":
        return secrets_handler(query)
    elif query.resource_type == "storage_class":
        return storage_class_handler(query)
    else:
        return "Unknown Resource Type"
    