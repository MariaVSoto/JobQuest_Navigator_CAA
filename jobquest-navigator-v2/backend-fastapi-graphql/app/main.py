"""
FastAPI + Strawberry GraphQL application for JobQuest Navigator v2
Main application entry point with minimal changes from Django version
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter
import strawberry

from app.graphql.schema import schema
from app.core.config import settings

# Create FastAPI application
app = FastAPI(
    title="JobQuest Navigator API v2",
    description="GraphQL API for JobQuest Navigator with minimal changes",
    version="2.0.0",
    debug=settings.debug
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_hosts,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create GraphQL router
graphql_app = GraphQLRouter(schema)

# Mount GraphQL endpoint
app.include_router(graphql_app, prefix="/graphql")

@app.get("/")
async def root():
    return {"message": "JobQuest Navigator API v2"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "2.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)