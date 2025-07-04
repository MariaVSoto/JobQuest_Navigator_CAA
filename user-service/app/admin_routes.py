"""
Admin routes for account management and system administration
"""
import uuid
from typing import Optional, List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_async_session
from app.users import current_superuser, current_active_user
from app.schemas import (
    AccountManagementAction,
    AccountSuspension,
    SuspensionReason,
    UserAccountStatus,
    AdminUserList,
    EmailNotification,
    BulkEmailRequest
)
from app.account_management import account_manager
from app.email_service import email_service

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=AdminUserList)
async def get_admin_user_list(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(50, ge=1, le=100, description="Items per page"),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    search_query: Optional[str] = Query(None, description="Search users"),
    admin_user = Depends(current_superuser),
    session: AsyncSession = Depends(get_async_session)
):
    """Get paginated list of users for admin management"""
    try:
        return await account_manager.get_admin_user_list(
            page=page,
            per_page=per_page,
            status_filter=status_filter,
            search_query=search_query,
            session=session
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve user list: {str(e)}"
        )


@router.get("/users/{user_id}/status", response_model=UserAccountStatus)
async def get_user_account_status(
    user_id: uuid.UUID,
    admin_user = Depends(current_superuser),
    session: AsyncSession = Depends(get_async_session)
):
    """Get detailed account status for a specific user"""
    try:
        status_info = await account_manager.get_user_account_status(
            user_id=user_id,
            session=session
        )
        
        if not status_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return status_info
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user status: {str(e)}"
        )


@router.post("/users/{user_id}/suspend")
async def suspend_user_account(
    user_id: uuid.UUID,
    suspension: AccountSuspension,
    admin_user = Depends(current_superuser),
    session: AsyncSession = Depends(get_async_session)
):
    """Suspend a user account"""
    try:
        # Calculate duration in hours if not permanent
        duration_hours = None
        if not suspension.is_permanent and suspension.suspended_until:
            duration = suspension.suspended_until - datetime.utcnow()
            duration_hours = int(duration.total_seconds() / 3600)
        
        success = await account_manager.suspend_user_account(
            user_id=user_id,
            reason=suspension.reason,
            description=suspension.description,
            duration_hours=duration_hours,
            admin_id=admin_user.id,
            session=session
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to suspend user account"
            )
        
        return {
            "message": "User account suspended successfully",
            "user_id": user_id,
            "suspended_until": suspension.suspended_until,
            "reason": suspension.reason.value
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to suspend user: {str(e)}"
        )


@router.post("/users/{user_id}/activate")
async def activate_user_account(
    user_id: uuid.UUID,
    admin_user = Depends(current_superuser),
    session: AsyncSession = Depends(get_async_session)
):
    """Activate/reactivate a user account"""
    try:
        success = await account_manager.activate_user_account(
            user_id=user_id,
            admin_id=admin_user.id,
            session=session
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to activate user account"
            )
        
        return {
            "message": "User account activated successfully",
            "user_id": user_id,
            "activated_at": datetime.utcnow()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to activate user: {str(e)}"
        )


@router.post("/users/{user_id}/lock")
async def lock_user_account(
    user_id: uuid.UUID,
    duration_minutes: Optional[int] = Query(None, description="Lock duration in minutes"),
    admin_user = Depends(current_superuser),
    session: AsyncSession = Depends(get_async_session)
):
    """Lock a user account temporarily"""
    try:
        # Get user email first
        user_status = await account_manager.get_user_account_status(user_id, session)
        if not user_status:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        success = await account_manager.lock_user_account(
            user_email=user_status.email,
            duration_minutes=duration_minutes,
            session=session
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to lock user account"
            )
        
        return {
            "message": "User account locked successfully",
            "user_id": user_id,
            "locked_at": datetime.utcnow(),
            "duration_minutes": duration_minutes
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to lock user: {str(e)}"
        )


@router.post("/email/send")
async def send_admin_email(
    email_notification: EmailNotification,
    admin_user = Depends(current_superuser)
):
    """Send email notification to a user"""
    try:
        success = False
        
        if email_notification.template == "welcome":
            success = await email_service.send_welcome_email(
                user_email=email_notification.to_email,
                user_name=email_notification.to_name or "User",
                verification_token=email_notification.context.get("verification_token")
            )
        elif email_notification.template == "verification":
            success = await email_service.send_verification_email(
                user_email=email_notification.to_email,
                user_name=email_notification.to_name or "User",
                verification_token=email_notification.context["verification_token"]
            )
        elif email_notification.template == "password_reset":
            success = await email_service.send_password_reset_email(
                user_email=email_notification.to_email,
                user_name=email_notification.to_name or "User",
                reset_token=email_notification.context["reset_token"]
            )
        elif email_notification.template == "job_alert":
            success = await email_service.send_job_alert_email(
                user_email=email_notification.to_email,
                user_name=email_notification.to_name or "User",
                job_matches=email_notification.context["job_matches"],
                preferences=email_notification.context["preferences"]
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown email template: {email_notification.template}"
            )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send email"
            )
        
        return {
            "message": "Email sent successfully",
            "template": email_notification.template,
            "recipient": email_notification.to_email
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send email: {str(e)}"
        )


@router.post("/email/bulk-send")
async def send_bulk_email(
    bulk_request: BulkEmailRequest,
    admin_user = Depends(current_superuser),
    session: AsyncSession = Depends(get_async_session)
):
    """Send bulk email to multiple users"""
    try:
        sent_count = 0
        failed_emails = []
        
        for user_id in bulk_request.user_ids:
            try:
                # Get user info
                user_status = await account_manager.get_user_account_status(user_id, session)
                if not user_status:
                    failed_emails.append({"user_id": str(user_id), "error": "User not found"})
                    continue
                
                # Send email based on template
                success = False
                
                if bulk_request.template == "job_alert":
                    success = await email_service.send_job_alert_email(
                        user_email=user_status.email,
                        user_name="User",  # Would need to get actual name
                        job_matches=bulk_request.context["job_matches"],
                        preferences=bulk_request.context["preferences"]
                    )
                # Add other bulk email templates as needed
                
                if success:
                    sent_count += 1
                else:
                    failed_emails.append({"user_id": str(user_id), "error": "Failed to send"})
                    
            except Exception as e:
                failed_emails.append({"user_id": str(user_id), "error": str(e)})
        
        return {
            "message": f"Bulk email operation completed",
            "sent_count": sent_count,
            "total_requested": len(bulk_request.user_ids),
            "failed_emails": failed_emails
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send bulk email: {str(e)}"
        )


@router.get("/stats/overview")
async def get_admin_stats_overview(
    admin_user = Depends(current_superuser),
    session: AsyncSession = Depends(get_async_session)
):
    """Get overview statistics for admin dashboard"""
    try:
        # This would calculate various statistics
        # For now, return mock data
        return {
            "total_users": 1234,
            "active_users": 1100,
            "verified_users": 980,
            "suspended_users": 12,
            "locked_users": 5,
            "new_users_today": 15,
            "new_users_this_week": 87,
            "login_attempts_today": 2341,
            "failed_logins_today": 23,
            "emails_sent_today": 156
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get admin stats: {str(e)}"
        )


@router.get("/activity/recent")
async def get_recent_admin_activity(
    limit: int = Query(50, ge=1, le=100),
    admin_user = Depends(current_superuser),
    session: AsyncSession = Depends(get_async_session)
):
    """Get recent administrative activities"""
    try:
        # This would fetch recent admin activities from an audit log
        # For now, return mock data
        return {
            "activities": [
                {
                    "id": "1",
                    "admin_id": str(admin_user.id),
                    "action": "user_suspended",
                    "target_user_email": "user@example.com",
                    "reason": "spam",
                    "timestamp": datetime.utcnow().isoformat()
                }
            ],
            "total_count": 1
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get admin activity: {str(e)}"
        )