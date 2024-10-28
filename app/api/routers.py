# app routers

from fastapi import APIRouter, HTTPException
from app.api.schema import QueryRequest, QueryResponse
from app.api.query_handler import handle_query

router = APIRouter()

@router.post("/query", response_model=QueryResponse)
async def query_kuberetes(request:QueryRequest):
    try:
        response = handle_query(query=request.query)

        return QueryResponse(query=request.query, answer=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))