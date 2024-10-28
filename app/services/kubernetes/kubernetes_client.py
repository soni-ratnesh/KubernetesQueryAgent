
from kubernetes import client, config
from typing import Optional, Dict

import logging

class KubernetesBase:
    def __init__(self, namespace: str = "default", labels: Optional[Dict[str, str]] = None):
        config.load_kube_config()  # Load Kubernetes configuration
        self.namespace = namespace
        self.labels = labels or {}
        self.label_selector = ",".join([f"{k}={v}" for k, v in self.labels.items()]) if self.labels else ""

    
    def log_error(self, message: str):
        logging.error(message)

    def count_items(self, items):
        return str(len(items))
