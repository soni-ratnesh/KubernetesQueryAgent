# schema for payloads

from pydantic import BaseModel


class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    query: str
    answer: str
