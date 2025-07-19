from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db import create_db_and_tables
from app.schemas import UserCreate, UserRead, UserUpdate
from app.users import auth_backend, current_active_user, fastapi_users
from app.routes import router as user_routes


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Create database tables on startup
    await create_db_and_tables()
    yield


app = FastAPI(
    title="JobQuest Navigator - User Service",
    description="User management microservice for JobQuest Navigator",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include FastAPI Users routers
app.include_router(
    fastapi_users.get_auth_router(auth_backend), 
    prefix="/auth/jwt", 
    tags=["auth"]
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)

# Include custom user routes
app.include_router(
    user_routes,
    prefix="/users",
    tags=["user-profile"]
)

# Include admin routes
from app.admin_routes import router as admin_routes
app.include_router(
    admin_routes,
    tags=["admin"]
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "JobQuest Navigator User Service", 
        "status": "healthy",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "service": "user-service",
        "version": "1.0.0",
        "environment": settings.environment
    }


@app.get("/protected-route")
async def protected_route(user = Depends(current_active_user)):
    """Example protected route"""
    return {"message": f"Hello {user.email}!", "user_id": str(user.id)}