"""
Database configuration and session management
AsyncSQLAlchemy setup for FastAPI with optimized connection pooling
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import QueuePool, NullPool
from sqlalchemy import event
import asyncio
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

def get_engine_config():
    """Get optimized engine configuration based on environment."""
    base_config = {
        "echo": settings.debug,
        "pool_pre_ping": True,  # Test connections before use
        "pool_recycle": 3600,   # Recycle connections every hour
        "echo_pool": settings.debug,  # Log pool events in debug mode
    }
    
    # Production configuration with connection pooling
    if not settings.debug and not settings.database_url.startswith("sqlite"):
        base_config.update({
            "poolclass": QueuePool,
            "pool_size": 20,        # Base number of connections
            "max_overflow": 30,     # Additional connections beyond pool_size
            "pool_timeout": 30,     # Timeout when getting connection from pool
            "pool_reset_on_return": "commit",  # Reset connections on return
        })
        logger.info("Using QueuePool for production database connections")
    else:
        # Development or SQLite - use simpler pooling
        base_config.update({
            "poolclass": NullPool,  # No pooling for SQLite or Lambda
        })
        logger.info("Using NullPool for development/SQLite database connections")
    
    return base_config

# Create async engine with optimized configuration
engine = create_async_engine(
    settings.database_url,
    **get_engine_config()
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
)

# Create declarative base
Base = declarative_base()


async def get_db():
    """
    Dependency to get database session with proper error handling
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()


# Enhanced session getter for GraphQL context
async def get_db_session() -> AsyncSession:
    """
    Get database session for GraphQL context
    """
    async with AsyncSessionLocal() as session:
        return session


# Alias for backwards compatibility
get_database = get_db


async def init_db():
    """
    Initialize database tables
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Connection pool monitoring
@event.listens_for(engine.sync_engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Set SQLite optimizations if using SQLite."""
    if settings.database_url.startswith("sqlite"):
        cursor = dbapi_connection.cursor()
        # Enable WAL mode for better concurrency
        cursor.execute("PRAGMA journal_mode=WAL")
        # Enable foreign keys
        cursor.execute("PRAGMA foreign_keys=ON")
        # Increase cache size
        cursor.execute("PRAGMA cache_size=-64000")  # 64MB
        cursor.close()


async def check_db_health() -> bool:
    """
    Check database health for monitoring endpoints.
    """
    try:
        async with AsyncSessionLocal() as session:
            await session.execute("SELECT 1")
            return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False


async def get_db_stats() -> dict:
    """
    Get database connection pool statistics.
    """
    pool = engine.pool if hasattr(engine, 'pool') else None
    if pool:
        return {
            "pool_size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "invalid": pool.invalid(),
        }
    return {"message": "No connection pool (using NullPool)"}


# Cleanup function for graceful shutdown
async def close_db():
    """
    Close database engine and connections.
    """
    await engine.dispose()
    logger.info("Database connections closed")