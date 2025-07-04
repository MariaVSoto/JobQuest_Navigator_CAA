"""
Email service for sending notifications and user communications
"""
import asyncio
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import Dict, List, Optional
import logging
from datetime import datetime
import aiofiles
from jinja2 import Environment, FileSystemLoader

from app.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails with template support"""
    
    def __init__(self):
        self.smtp_host = settings.smtp_host
        self.smtp_port = settings.smtp_port
        self.smtp_username = settings.smtp_username
        self.smtp_password = settings.smtp_password
        self.from_email = settings.smtp_from_email
        self.from_name = settings.smtp_from_name
        self.use_tls = settings.smtp_use_tls
        self.use_ssl = settings.smtp_use_ssl
        self.frontend_url = settings.frontend_url
        
        # Initialize Jinja2 environment for templates
        template_dir = Path(settings.email_templates_dir)
        self.jinja_env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=True
        )
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        to_name: Optional[str] = None
    ) -> bool:
        """Send an email with HTML and optional text content"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            
            # Add text content if provided
            if text_content:
                text_part = MIMEText(text_content, 'plain')
                msg.attach(text_part)
            
            # Add HTML content
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Send email in a thread to avoid blocking
            await asyncio.get_event_loop().run_in_executor(
                None, self._send_smtp_email, msg
            )
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    def _send_smtp_email(self, msg: MIMEMultipart):
        """Send email via SMTP (blocking, run in executor)"""
        if not self.smtp_username or not self.smtp_password:
            logger.warning("SMTP credentials not configured, email not sent")
            return
            
        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            if self.use_tls:
                server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            server.send_message(msg)
    
    async def render_template(
        self, 
        template_name: str, 
        context: Dict
    ) -> str:
        """Render Jinja2 template with context"""
        try:
            template = self.jinja_env.get_template(template_name)
            return template.render(**context)
        except Exception as e:
            logger.error(f"Failed to render template {template_name}: {str(e)}")
            return ""
    
    async def send_welcome_email(
        self,
        user_email: str,
        user_name: str,
        verification_token: Optional[str] = None
    ) -> bool:
        """Send welcome email to new users"""
        context = {
            'user_name': user_name,
            'frontend_url': self.frontend_url,
            'verification_token': verification_token,
            'verification_url': f"{self.frontend_url}/verify-email?token={verification_token}" if verification_token else None,
            'company_name': self.from_name,
            'current_year': datetime.now().year
        }
        
        html_content = await self.render_template('welcome.html', context)
        if not html_content:
            return False
            
        return await self.send_email(
            to_email=user_email,
            subject=f"Welcome to {self.from_name}! 🎯",
            html_content=html_content,
            to_name=user_name
        )
    
    async def send_verification_email(
        self,
        user_email: str,
        user_name: str,
        verification_token: str
    ) -> bool:
        """Send email verification"""
        context = {
            'user_name': user_name,
            'verification_url': f"{self.frontend_url}/verify-email?token={verification_token}",
            'frontend_url': self.frontend_url,
            'company_name': self.from_name,
            'expiry_hours': settings.email_verification_expire_hours,
            'current_year': datetime.now().year
        }
        
        html_content = await self.render_template('email_verification.html', context)
        if not html_content:
            return False
            
        return await self.send_email(
            to_email=user_email,
            subject="Please verify your email address",
            html_content=html_content,
            to_name=user_name
        )
    
    async def send_password_reset_email(
        self,
        user_email: str,
        user_name: str,
        reset_token: str
    ) -> bool:
        """Send password reset email"""
        context = {
            'user_name': user_name,
            'reset_url': f"{self.frontend_url}/reset-password?token={reset_token}",
            'frontend_url': self.frontend_url,
            'company_name': self.from_name,
            'expiry_hours': settings.password_reset_expire_hours,
            'current_year': datetime.now().year
        }
        
        html_content = await self.render_template('password_reset.html', context)
        if not html_content:
            return False
            
        return await self.send_email(
            to_email=user_email,
            subject="Reset your password",
            html_content=html_content,
            to_name=user_name
        )
    
    async def send_account_locked_email(
        self,
        user_email: str,
        user_name: str,
        lockout_duration_minutes: int
    ) -> bool:
        """Send account locked notification"""
        context = {
            'user_name': user_name,
            'lockout_duration': lockout_duration_minutes,
            'frontend_url': self.frontend_url,
            'company_name': self.from_name,
            'support_email': self.from_email,
            'current_year': datetime.now().year
        }
        
        html_content = await self.render_template('account_locked.html', context)
        if not html_content:
            return False
            
        return await self.send_email(
            to_email=user_email,
            subject="Account Security Alert - Temporary Lockout",
            html_content=html_content,
            to_name=user_name
        )
    
    async def send_account_suspended_email(
        self,
        user_email: str,
        user_name: str,
        reason: str,
        suspension_until: Optional[datetime] = None
    ) -> bool:
        """Send account suspension notification"""
        context = {
            'user_name': user_name,
            'reason': reason,
            'suspension_until': suspension_until,
            'is_permanent': suspension_until is None,
            'frontend_url': self.frontend_url,
            'company_name': self.from_name,
            'support_email': self.from_email,
            'current_year': datetime.now().year
        }
        
        html_content = await self.render_template('account_suspended.html', context)
        if not html_content:
            return False
            
        return await self.send_email(
            to_email=user_email,
            subject="Account Suspension Notice",
            html_content=html_content,
            to_name=user_name
        )
    
    async def send_job_alert_email(
        self,
        user_email: str,
        user_name: str,
        job_matches: List[Dict],
        preferences: Dict
    ) -> bool:
        """Send job alert with matching positions"""
        context = {
            'user_name': user_name,
            'job_matches': job_matches,
            'job_count': len(job_matches),
            'preferences': preferences,
            'frontend_url': self.frontend_url,
            'company_name': self.from_name,
            'unsubscribe_url': f"{self.frontend_url}/settings/notifications",
            'current_year': datetime.now().year
        }
        
        html_content = await self.render_template('job_alert.html', context)
        if not html_content:
            return False
            
        subject = f"🎯 {len(job_matches)} new job matches for you!"
        return await self.send_email(
            to_email=user_email,
            subject=subject,
            html_content=html_content,
            to_name=user_name
        )


# Global email service instance
email_service = EmailService()