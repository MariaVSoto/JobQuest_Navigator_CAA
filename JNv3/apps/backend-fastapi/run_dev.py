#!/usr/bin/env python3
"""
Development server runner for FastAPI + Strawberry GraphQL
"""

import uvicorn
from app.main import app

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8001,  # Use different port to avoid conflict with Django
        reload=True,
        reload_dirs=["app"],
        log_level="info"
    )