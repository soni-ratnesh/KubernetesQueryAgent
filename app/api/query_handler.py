from app.services.openai import OpenAIClient
from app.services.kubernetes.workload import deployment, pod

def handle_query(query: str, openai_client: OpenAIClient = OpenAIClient())->str:

    # extract query key information using OpenAI
    query_details = openai_client.extract(query)

    # query kube client
    if query_details.resource_category=="workload":
        
        if query_details.resource_type=="deployment":
            deployment_resource = deployment.DeploymentResource(namespace=query_details.namespace, labels=query_details.filters.labels)

            # Route based on the action specified in the query
            if query_details.action == "count":
                return deployment_resource.get_count()
            
            elif query_details.action == "status" and query_details.specific_name:
                return deployment_resource.get_status(query_details.specific_name)
            
            elif query_details.action == "creation_time" and query_details.specific_name:
                return deployment_resource.get_creation_time(query_details.specific_name)
            
            elif query_details.action == "exists":
                return deployment_resource.exists()
            
            elif query_details.action == "list":
                # Use `status` in filters to list active, terminated, or all deployments
                status_filter = query_details.filters.status if len(query_details.filters.status) else "all"
                return deployment_resource.list_deployments(status_filter=status_filter)
            
            else:
                return "Unsupported action or missing required parameters."
        
        elif query_details.resource_type == "pod":
            # Initialize PodResource with namespace and labels if provided
            pod_resource = pod.PodResource(namespace=query_details.namespace, labels=query_details.filters.labels)
            
            # Route based on action specified in the query
            if query_details.action == "count":
                return pod_resource.get_count()
            
            elif query_details.action == "status" and query_details.specific_name:
                return pod_resource.get_status(query_details.specific_name)
            
            elif query_details.action == "creation_time" and query_details.specific_name:
                return pod_resource.get_creation_time(query_details.specific_name)
            
            elif query_details.action == "details" and query_details.specific_name:
                return pod_resource.get_logs(query_details.specific_name)
            
            elif query_details.action == "list":
                status_filter = query_details.filters.status if len(query_details.filters.status) else "all"
                return pod_resource.list_pods(status_filter=status_filter)
            
            return "Unsupported action or missing required parameters for pod."




    response = "Dummy"

    return response
