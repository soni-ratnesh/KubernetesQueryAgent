from app.services.openai import OpenAIClient
from app.services.kubernetes.workload import workload_handler

def handle_query(query: str, openai_client: OpenAIClient = OpenAIClient())->str:

    # extract query key information using OpenAI
    query_details = openai_client.extract(query)

    # query kube client
    if query_details.resource_category=="workload":
        return workload_handler(query_details)
    elif query_details.resource_category =="services":
        pass

    response = "Dummy"

    return response
