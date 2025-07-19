import uuid
from typing import AsyncGenerator

from fastapi import Depends
from fastapi_users.db import SQLAlchemyBaseUserTableUUID, SQLAlchemyUserDatabase
from sqlalchemy import Column, String, Boolean, DateTime, Text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func

from app.config import settings


class Base(DeclarativeBase):
    pass


class User(SQLAlchemyBaseUserTableUUID, Base):
    """Extended User model with JobQuest specific fields"""
    
    # Basic profile information
    first_name: Mapped[str] = mapped_column(String(50), nullable=True)
    last_name: Mapped[str] = mapped_column(String(50), nullable=True)
    full_name: Mapped[str] = mapped_column(String(100), nullable=True)
    phone_number: Mapped[str] = mapped_column(String(20), nullable=True)
    
    # Profile and career information
    bio: Mapped[str] = mapped_column(Text, nullable=True)
    current_job_title: Mapped[str] = mapped_column(String(100), nullable=True)
    years_of_experience: Mapped[int] = mapped_column(nullable=True, default=0)
    industry: Mapped[str] = mapped_column(String(100), nullable=True)
    
    # Job search preferences
    career_level: Mapped[str] = mapped_column(String(20), nullable=True)  # entry, mid, senior, executive
    job_search_status: Mapped[str] = mapped_column(String(20), nullable=True)  # actively_looking, passively_looking, not_looking
    preferred_work_type: Mapped[str] = mapped_column(String(20), nullable=True)  # remote, hybrid, onsite
    preferred_location: Mapped[str] = mapped_column(String(100), nullable=True)
    desired_salary_min: Mapped[int] = mapped_column(nullable=True)
    desired_salary_max: Mapped[int] = mapped_column(nullable=True)
    salary_currency: Mapped[str] = mapped_column(String(3), nullable=True, default="USD")
    
    # Skills and interests
    skills: Mapped[str] = mapped_column(Text, nullable=True)  # JSON string of skills
    interests: Mapped[str] = mapped_column(Text, nullable=True)  # JSON string of interests
    
    # Privacy and notifications
    profile_visibility: Mapped[str] = mapped_column(String(20), nullable=True, default="private")  # public, private, recruiters_only
    email_notifications: Mapped[bool] = mapped_column(Boolean, default=True)
    job_alerts: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Timestamps
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_login: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=True)


# Database engine and session
engine = create_async_engine(settings.database_url, echo=settings.debug)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)