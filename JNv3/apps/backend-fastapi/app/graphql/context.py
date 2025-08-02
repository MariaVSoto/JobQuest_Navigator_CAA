"""
GraphQL context management for request lifecycle.
Handles authentication, database sessions, and DataLoader registry.
"""

from typing import Optional, Any
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dataloaders import DataLoaderRegistry
from app.models.user import User


class GraphQLContext:
    """
    GraphQL execution context that carries request-scoped data.
    Includes database session, current user, and DataLoader registry.
    """
    
    def __init__(
        self,
        request: Request,
        db_session: AsyncSession,
        user: Optional[User] = None
    ):
        self.request = request
        self.db_session = db_session
        self.user = user
        self._dataloaders: Optional[DataLoaderRegistry] = None
    
    @property
    def dataloaders(self) -> DataLoaderRegistry:
        """Lazy initialization of DataLoader registry."""
        if self._dataloaders is None:
            self._dataloaders = DataLoaderRegistry(self.db_session)
        return self._dataloaders
    
    def get_user_id(self) -> Optional[str]:
        """Get current user ID if authenticated."""
        return str(self.user.id) if self.user else None
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        return self.user is not None
    
    def clear_dataloaders(self):
        """Clear DataLoader cache to prevent memory leaks."""
        if self._dataloaders:
            self._dataloaders.clear_cache()


async def get_graphql_context(
    request: Request,
    db_session: AsyncSession,
    user: Optional[User] = None
) -> GraphQLContext:
    """
    Create GraphQL context for a request.
    This function would be called by the GraphQL endpoint setup.
    """
    return GraphQLContext(
        request=request,
        db_session=db_session,
        user=user
    )