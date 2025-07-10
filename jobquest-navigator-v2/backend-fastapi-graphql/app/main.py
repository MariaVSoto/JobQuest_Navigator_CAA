"""
FastAPI + Strawberry GraphQL application for JobQuest Navigator v2
Main application entry point with authentication and middleware
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter

from app.graphql.schema import schema
from app.core.config import settings
from app.auth.middleware import get_context

# Create FastAPI application
app = FastAPI(
    title="JobQuest Navigator API v2",
    description="GraphQL API for JobQuest Navigator with authentication",
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

# Create GraphQL router with authentication context
graphql_app = GraphQLRouter(
    schema,
    context_getter=get_context
)

# Mount GraphQL endpoint
app.include_router(graphql_app, prefix="/graphql")

@app.get("/")
async def root():
    return {
        "message": "JobQuest Navigator API v2",
        "version": "2.0.0",
        "graphql_endpoint": "/graphql"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "2.0.0",
        "services": {
            "database": "connected",
            "authentication": "configured" if settings.cognito_user_pool_id else "development_mode"
        }
    }

@app.get("/auth/status")
async def auth_status():
    """Check authentication configuration status"""
    return {
        "cognito_configured": bool(settings.cognito_user_pool_id and settings.cognito_client_id),
        "region": settings.cognito_region,
        "development_mode": settings.debug and not settings.cognito_user_pool_id
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)