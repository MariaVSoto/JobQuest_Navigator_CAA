"""
Base service class for common functionality
Provides database session management and common patterns
"""

from typing import Optional, TypeVar, Type
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.core.database import AsyncSessionLocal

T = TypeVar('T')


class BaseService:
    """Base service class with common database operations"""
    
    def __init__(self, db_session: Optional[AsyncSession] = None):
        self.db_session = db_session
    
    async def get_db_session(self) -> AsyncSession:
        """Get database session - use injected session or create new one"""
        if self.db_session:
            return self.db_session
        return AsyncSessionLocal()
    
    async def get_by_id(
        self, 
        model: Type[T], 
        id_value: UUID, 
        session: Optional[AsyncSession] = None
    ) -> Optional[T]:
        """Generic get by ID method"""
        db_session = session or await self.get_db_session()
        
        try:
            result = await db_session.execute(
                select(model).where(model.id == id_value)
            )
            return result.scalar_one_or_none()
        finally:
            if not session:  # Only close if we created the session
                await db_session.close()
    
    async def create(
        self, 
        model_instance: T, 
        session: Optional[AsyncSession] = None
    ) -> T:
        """Generic create method"""
        db_session = session or await self.get_db_session()
        
        try:
            db_session.add(model_instance)
            await db_session.commit()
            await db_session.refresh(model_instance)
            return model_instance
        except Exception:
            await db_session.rollback()
            raise
        finally:
            if not session:
                await db_session.close()
    
    async def update(
        self, 
        model: Type[T], 
        id_value: UUID, 
        **kwargs
    ) -> Optional[T]:
        """Generic update method"""
        async with await self.get_db_session() as session:
            try:
                result = await session.execute(
                    select(model).where(model.id == id_value)
                )
                instance = result.scalar_one_or_none()
                
                if instance:
                    for key, value in kwargs.items():
                        if hasattr(instance, key):
                            setattr(instance, key, value)
                    
                    await session.commit()
                    await session.refresh(instance)
                
                return instance
            except Exception:
                await session.rollback()
                raise
    
    async def delete(
        self, 
        model: Type[T], 
        id_value: UUID
    ) -> bool:
        """Generic soft delete method (sets is_active = False)"""
        async with await self.get_db_session() as session:
            try:
                result = await session.execute(
                    select(model).where(model.id == id_value)
                )
                instance = result.scalar_one_or_none()
                
                if instance and hasattr(instance, 'is_active'):
                    instance.is_active = False
                    await session.commit()
                    return True
                
                return False
            except Exception:
                await session.rollback()
                raise