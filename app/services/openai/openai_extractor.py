from .schema import KubernetesQuery

import openai

class OpenAIClient(object):
    def __init__(self, model :str="gpt-4"):
        self.openai = openai.OpenAI()
        self.model = model
    
    def _system_prompt(self):
        prompt = """
        System Message:

        You are a Kubernetes query assistant. Your role is to convert natural language queries about Kubernetes resources into a structured JSON format. Each query may pertain to resources like Deployments, Pods, ReplicaSets, Services, ConfigMaps, Nodes, or other Kubernetes objects.

        Please interpret the query and output the information in the following JSON schema:

        {
            "resource_category": "string",
            "resource_type": "string",
            "action": "string",
            "namespace": "string",
            "specific_name": "string",
            "filters": {
                "status": "string",
                "labels": {
                    "key": "value"
                },
                "other": {
                    "custom_key": "custom_value"
                }
            }
        }

        Details:
        - **resource_category**: High-level grouping of the resource type (e.g., "workload", "service", "config_storage", "cluster").
        - **resource_type**: Specific Kubernetes resource type (e.g., "pod", "deployment", "service").
        - **action**: The action to perform, such as "list", "status", "details", "count", or "get_related".
        - **namespace**: The Kubernetes namespace. If not specified, default to "default".
        - **specific_name**: The specific name of the resource, if provided.
        - **filters**: Contains additional filters, such as:
            - **status**: Filter based on status (e.g., "Running", "Failed").
            - **labels**: Filter based on labels in key-value format.
            - **other**: Any other custom filters related to the query.

        Example 1: Query - "Which pod is spawned by my-deployment?"
        {
            "resource_category": "workload",
            "resource_type": "replicaset",
            "action": "get_related",
            "namespace": "default",
            "specific_name": "my-deployment",
            "filters": {
                "status": null,
                "labels": dict,
            }
        }

        Output only the JSON response with no additional text.

        """

        return prompt
    
    def extract(self, query):
        response = self.openai.beta.chat.completions.parse(
                                                    model="gpt-4o",
                                                    messages=[
                                                        {"role": "system", "content": self._system_prompt()},
                                                        {"role": "user", "content": query}
                                                    ],
                                                    temperature=0 ,
                                                    response_format=KubernetesQuery 
                                                )
        content = response.choices[0].message.parsed
        return content