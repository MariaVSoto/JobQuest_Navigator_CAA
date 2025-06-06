from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    resumes = relationship('Resume', back_populates='user')

class Resume(Base):
    __tablename__ = 'resumes'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    versions = relationship('ResumeVersion', back_populates='resume')
    user = relationship('User', back_populates='resumes')

class ResumeVersion(Base):
    __tablename__ = 'resume_versions'
    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey('resumes.id'))
    file_path = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    comment = Column(Text)
    resume = relationship('Resume', back_populates='versions') 