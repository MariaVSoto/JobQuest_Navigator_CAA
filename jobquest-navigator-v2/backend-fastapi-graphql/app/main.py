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
    """
    Comprehensive health check endpoint for load balancer and monitoring
    """
    import time
    from sqlalchemy import text
    from app.core.database import get_db
    
    start_time = time.time()
    health_status = {
        "status": "healthy",
        "timestamp": int(time.time()),
        "version": "2.0.0",
        "environment": settings.environment,
        "services": {}
    }
    
    # Database connectivity check
    try:
        async for db in get_db():
            result = await db.execute(text("SELECT 1"))
            if result.scalar() == 1:
                health_status["services"]["database"] = "connected"
            else:
                health_status["services"]["database"] = "error"
                health_status["status"] = "degraded"
            break
    except Exception as e:
        health_status["services"]["database"] = f"error: {str(e)[:50]}"
        health_status["status"] = "unhealthy"
    
    # Authentication service check
    if settings.cognito_user_pool_id and settings.cognito_client_id:
        health_status["services"]["authentication"] = "configured"
    else:
        health_status["services"]["authentication"] = "development_mode"
    
    # Redis connectivity check (if configured)
    if hasattr(settings, 'redis_url') and settings.redis_url:
        try:
            import redis.asyncio as redis
            redis_client = redis.from_url(settings.redis_url)
            await redis_client.ping()
            health_status["services"]["cache"] = "connected"
            await redis_client.close()
        except Exception as e:
            health_status["services"]["cache"] = f"error: {str(e)[:50]}"
            if health_status["status"] == "healthy":
                health_status["status"] = "degraded"
    
    # GraphQL service
    health_status["services"]["graphql"] = "available"
    
    # Response time
    health_status["response_time_ms"] = round((time.time() - start_time) * 1000, 2)
    
    return health_status

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