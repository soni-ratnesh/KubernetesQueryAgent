# app/main.py

from fastapi import FastAPI
from app.api import routers

# Initialize the FastAPI application
app = FastAPI(title="Kubernetes Query Agent")

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    pass

@app.on_event("shutdown")
async def shutdown_event():
    pass
    
@app.get("/")
async def root():
    return {"message": "Welcome to the Kubernetes Query Agent API"}
