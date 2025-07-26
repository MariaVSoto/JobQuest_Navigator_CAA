"""
GraphQL middleware for error handling and common functionality
"""

import logging
import traceback
from typing import Any, Dict, Optional
from datetime import datetime
from uuid import uuid4

import strawberry
from strawberry.extensions import Extension
from strawberry.types import ExecutionContext

logger = logging.getLogger(__name__)


class ErrorHandlingExtension(Extension):
    """GraphQL error handling extension for consistent error responses"""
    
    def on_request_start(self, *, execution_context: ExecutionContext) -> None:
        """Initialize request context"""
        execution_context.context["request_id"] = str(uuid4())
        execution_context.context["start_time"] = datetime.now()
    
    def on_request_end(self, *, execution_context: ExecutionContext) -> None:
        """Log request completion"""
        request_id = execution_context.context.get("request_id")
        start_time = execution_context.context.get("start_time")
        
        if start_time:
            duration = (datetime.now() - start_time).total_seconds()
            logger.info(f"GraphQL request {request_id} completed in {duration:.3f}s")
    
    def on_validation_error(
        self, 
        *, 
        execution_context: ExecutionContext, 
        error: Exception
    ) -> None:
        """Handle GraphQL validation errors"""
        request_id = execution_context.context.get("request_id")
        logger.warning(f"GraphQL validation error in request {request_id}: {error}")
    
    def on_parsing_error(
        self, 
        *, 
        execution_context: ExecutionContext, 
        error: Exception
    ) -> None:
        """Handle GraphQL parsing errors"""
        request_id = execution_context.context.get("request_id")
        logger.warning(f"GraphQL parsing error in request {request_id}: {error}")
    
    def on_execution_error(
        self, 
        *, 
        execution_context: ExecutionContext, 
        error: Exception
    ) -> None:
        """Handle GraphQL execution errors"""
        request_id = execution_context.context.get("request_id")
        logger.error(
            f"GraphQL execution error in request {request_id}: {error}",
            extra={
                "request_id": request_id,
                "error_type": type(error).__name__,
                "traceback": traceback.format_exc()
            }
        )


@strawberry.type
class ErrorInfo:
    """Structured error information"""
    code: str
    message: str
    field: Optional[str] = None
    timestamp: str = strawberry.field(default_factory=lambda: datetime.now().isoformat())


class BusinessLogicError(Exception):
    """Base exception for business logic errors"""
    
    def __init__(self, message: str, code: str = "BUSINESS_ERROR", field: Optional[str] = None):
        self.message = message
        self.code = code
        self.field = field
        super().__init__(message)


class ValidationError(BusinessLogicError):
    """Validation error"""
    
    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(message, "VALIDATION_ERROR", field)


class NotFoundError(BusinessLogicError):
    """Resource not found error"""
    
    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(message, "NOT_FOUND", field)


class AuthenticationError(BusinessLogicError):
    """Authentication error"""
    
    def __init__(self, message: str = "Authentication required"):
        super().__init__(message, "AUTHENTICATION_ERROR")


class AuthorizationError(BusinessLogicError):
    """Authorization error"""
    
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message, "AUTHORIZATION_ERROR")


def format_error(error: Exception, info: Any = None) -> Dict[str, Any]:
    """Format errors for consistent GraphQL responses"""
    
    if isinstance(error, BusinessLogicError):
        return {
            "message": error.message,
            "extensions": {
                "code": error.code,
                "field": error.field,
                "timestamp": datetime.now().isoformat()
            }
        }
    
    # Handle unexpected errors
    logger.error(f"Unexpected error: {error}", exc_info=True)
    
    return {
        "message": "An unexpected error occurred",
        "extensions": {
            "code": "INTERNAL_ERROR",
            "timestamp": datetime.now().isoformat()
        }
    }


def handle_service_errors(func):
    """Decorator to handle service layer errors in GraphQL resolvers"""
    
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except BusinessLogicError:
            # Re-raise business logic errors as-is
            raise
        except Exception as e:
            # Convert unexpected errors to internal errors
            logger.error(f"Service error in {func.__name__}: {e}", exc_info=True)
            raise BusinessLogicError("An internal error occurred", "INTERNAL_ERROR")
    
    return wrapper