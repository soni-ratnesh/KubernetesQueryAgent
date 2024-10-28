# app/main.py
import logging

from fastapi import FastAPI
from app.api import routers
from app.core import logger
from app.services import openai_extractor


# Initialize the FastAPI application
app = FastAPI(title="Kubernetes Query Agent")

# Registre router
app.include_router(routers.router)

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    logger.setup_logging()
    app.state.openai_client = openai_extractor.OpenAIClient()

@app.on_event("shutdown")
async def shutdown_event():
    logger.shutdown_logging()
    del app.state.openai_client
    
@app.get("/")
async def root():
    logging.info(msg="In base route")
    return {"message": "Welcome to the Kubernetes Query Agent API"}
