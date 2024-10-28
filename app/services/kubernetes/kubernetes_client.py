
from kubernetes import client, config

import logging

class KubernetesBase:
    def __init__(self, namespace: str = "default"):
        config.load_kube_config()  # Load Kubernetes configuration
        self.namespace = namespace
    
    def log_error(self, message: str):
        logging.error(message)

    def count_items(self, items):
        return str(len(items))
