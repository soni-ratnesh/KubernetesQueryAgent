# app routers

from fastapi import APIRouter, HTTPException
from app.api.schema import QueryRequest, QueryResponse

router = APIRouter()

@router.post("/query", response_model=QueryResponse)
async def query_kuberetes(request:QueryRequest):
    try:
        # sample response
        response = "Sample"

        return QueryResponse(query=request.query, answer=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))