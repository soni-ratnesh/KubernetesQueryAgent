from pydantic import BaseModel
from typing import Optional, Dict, Any, List

class Label(BaseModel):
    key : str
    value: str

class QueryFilters(BaseModel):
    status: str
    labels: List [Label]


class KubernetesQuery(BaseModel):
    resource_category: str  
    resource_type: str      
    action: str             
    namespace: str 
    specific_name: str
    filters: QueryFilters
