from app.services.openai import OpenAIClient
from app.services.kubernetes.workload import workload_handler
from app.services.kubernetes.services import service_handler
from app.services.kubernetes.config_storage import config_storage_handler
from app.services.kubernetes.cluster import cluster_handler

def handle_query(query: str, openai_client: OpenAIClient = OpenAIClient())->str:

    # extract query key information using OpenAI
    query_details = openai_client.extract(query)

    # query kube client based on resourse category
    if query_details.resource_category=="workload":
        return workload_handler(query_details)
    elif query_details.resource_category =="services":
        return service_handler(query_details)
    elif query_details.resource_category == "config_storage":
        return config_storage_handler(query_details)
    elif query_details.resource_category == "cluster":
        return cluster_handler(query_details)
    else:
        return "Unknown Resource Category"
    