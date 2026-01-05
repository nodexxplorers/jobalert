# backend/app/services/notification_service.py

from sqlalchemy.orm import Session
from app.models.user import User
from app.models.job import Job
from app.models.notification import Notification
from datetime import datetime, timezone
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings
from datetime import datetime as _dt
import asyncio
from telegram import Bot
from telegram.constants import ParseMode
from typing import List

class NotificationService:
    """Handle sending notifications via email, telegram, push"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def send_job_notification(self, user: User, job: Job):
        """Send notification about new job to user (Database Only)"""
        category = job.category or "general"
        username = job.username or "Unknown"
        text = job.text or "No description available"
        
        notification = Notification(
            user_id=user.id,
            job_id=job.id,
            title=f"New {category.replace('_', ' ').title()} Job!",
            message=f"@{username}: {text[:200]}{'...' if len(text) > 200 else ''}",
            notification_type='job_alert',
            job_title=text[:100],
            job_category=category,
            job_url=job.tweet_url,
            is_read=False,
            is_clicked=False,
            sent_at=datetime.now(timezone.utc)
        )
        
        try:
            self.db.add(notification)
            self.db.commit()
            return notification
        except Exception as e:
            print(f"    ❌ Failed to save notification: {e}")
            self.db.rollback()
            return None

    def send_batch_job_notification(self, user: User, jobs: List[Job]):
        """Send a summary email with multiple jobs to user"""
        if not jobs:
            return

        # Mark which ones we sent via email
        display_name = user.display_name or user.username
        
        try:
            if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
                return

            msg = MIMEMultipart('alternative')
            msg['From'] = settings.SMTP_USER
            msg['To'] = user.email or ""
            msg['Subject'] = f"🎯 {len(jobs)} New Job Opportunities Found!"

            # Build HTML body
            jobs_html = ""
            for job in jobs:
                jobs_html += f"""
                <div style="margin-bottom: 20px; padding: 15px; border: 1px solid #e2e8f0; rounded: 8px;">
                    <h3 style="margin-top: 0; color: #1a202c;">{job.category.replace('_', ' ').title()}</h3>
                    <p style="color: #4a5568;"><b>@{job.username}</b>: {job.text[:300]}...</p>
                    <a href="{job.tweet_url}" style="background-color: #4299e1; color: white; padding: 8px 16px; text-decoration: none; border-radius: 4px; display: inline-block;">View on X</a>
                </div>
                """

            html_body = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; color: #2d3748;">
                <h2>Hello {display_name}!</h2>
                <p>We found {len(jobs)} new job opportunities matching your preferences:</p>
                {jobs_html}
                <hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 20px 0;">
                <p style="font-size: 0.875rem;">X Job Bot - Never miss an opportunity</p>
                <p style="font-size: 0.875rem;">Manage your alerts: <a href="{settings.FRONTEND_URL}/settings">{settings.FRONTEND_URL}/settings</a></p>
            </div>
            """

            msg.attach(MIMEText(html_body, 'html'))

            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)

            # Update notifications to indicate they were sent via email
            self.db.query(Notification).filter(
                Notification.user_id == user.id,
                Notification.job_id.in_([j.id for j in jobs])
            ).update({Notification.sent_via_email: True}, synchronize_session=False)
            self.db.commit()

            print(f"    ✉️ Sent summary email to {user.username} with {len(jobs)} jobs")
            
        except Exception as e:
            print(f"    ❌ Batch email error: {e}")
            self.db.rollback()
    
    def _send_email(self, user: User, job: Job) -> bool:
        """Send email notification"""
        try:
            if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
                return False
            
            # Safe defaults for optional fields
            category = job.category or "general"
            username = job.username or "Unknown"
            text = job.text or "No description available"
            display_name = user.display_name or user.username
            
            msg = MIMEMultipart()
            msg['From'] = settings.SMTP_USER
            msg['To'] = user.email or ""
            msg['Subject'] = f"🎯 New {category.replace('_', ' ').title()} Job on X!"
            
            body = f"""
Hello {display_name}!

A new job matching your preferences was just posted on X:

👤 Posted by: @{username}
📝 Job: {text[:300]}{'...' if len(text) > 300 else ''}

🔗 Apply now: {job.tweet_url}

⚡ This alert was sent within minutes of the job being posted. Be quick to apply!

---
X Job Bot - Never miss an opportunity
Manage your alerts: {settings.FRONTEND_URL}/settings
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            print(f"    ❌ Email error: {e}")
            return False
    
    async def _send_telegram(self, user: User, job: Job) -> bool:
        """Send a single telegram notification (async)"""
        try:
            if not settings.TELEGRAM_BOT_TOKEN or not user.telegram_chat_id:
                return False
            
            bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
            
            # Escape special characters for MarkdownV2 if needed, or use HTML
            message = (
                f"🎯 <b>New Job opportunity!</b>\n\n"
                f"👤 <b>@{job.username}</b>\n"
                f"📝 {job.text[:200]}...\n\n"
                f"🔗 <a href='{job.tweet_url}'>View on X</a>"
            )
            
            await bot.send_message(
                chat_id=user.telegram_chat_id,
                text=message,
                parse_mode=ParseMode.HTML
            )
            return True
            
        except Exception as e:
            print(f"    ❌ Telegram error: {e}")
            return False

    async def send_telegram_summary(self, user: User, jobs: List[Job]):
        """Send a summary telegram message with multiple jobs"""
        if not jobs or not settings.TELEGRAM_BOT_TOKEN or not user.telegram_chat_id:
            return

        try:
            bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
            
            job_count = len(jobs)
            header = f"🎯 <b>Found {job_count} new jobs matching your preferences!</b>\n\n"
            
            # Combine jobs into one or multiple messages if too long
            current_message = header
            for job in jobs:
                job_text = (
                    f"📂 <b>{job.category.replace('_', ' ').title()}</b>\n"
                    f"👤 @{job.username}\n"
                    f"📝 {job.text[:150]}...\n"
                    f"🔗 <a href='{job.tweet_url}'>Link</a>\n\n"
                )
                
                # Telegram has a 4096 char limit
                if len(current_message) + len(job_text) > 4000:
                    await bot.send_message(chat_id=user.telegram_chat_id, text=current_message, parse_mode=ParseMode.HTML)
                    current_message = job_text
                else:
                    current_message += job_text
            
            if current_message:
                await bot.send_message(chat_id=user.telegram_chat_id, text=current_message, parse_mode=ParseMode.HTML)
            
            # Update notifications
            self.db.query(Notification).filter(
                Notification.user_id == user.id,
                Notification.job_id.in_([j.id for j in jobs])
            ).update({Notification.sent_via_telegram: True}, synchronize_session=False)
            self.db.commit()
            
            print(f"    📱 Sent Telegram summary to {user.username}")
            
        except Exception as e:
            print(f"    ❌ Telegram batch error: {e}")
            self.db.rollback()
    def send_admin_scrape_report(self, admin_user: User, stats: dict):
        """Send a summary report of the scraping cycle to an admin"""
        subject = f"📊 Scraper Report: {stats.get('new_jobs', 0)} new jobs found"
        
        message = f"""
Hello {admin_user.display_name or admin_user.username},

The hourly scraping cycle has completed.

📈 Summary:
- New jobs found: {stats.get('new_jobs', 0)}
- Categories searched: {stats.get('categories_count', 0)}
- Start time: {stats.get('start_time', 'N/A')}
- End time: {stats.get('end_time', 'N/A')}
- Errors encountered: {stats.get('errors_count', 0)}

{f"⚠️ Latest Error: {stats.get('last_error')}" if stats.get('last_error') else "✅ All categories processed successfully."}

---
X Job Bot - Admin Panel: {settings.FRONTEND_URL}/admin
        """
        
        # Send via Email
        if admin_user.email:
            try:
                if settings.SMTP_USER and settings.SMTP_PASSWORD:
                    msg = MIMEMultipart()
                    msg['From'] = settings.SMTP_USER
                    msg['To'] = admin_user.email
                    msg['Subject'] = subject
                    msg.attach(MIMEText(message, 'plain'))
                    
                    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                        server.starttls()
                        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                        server.send_message(msg)
                    print(f"    ✉️ Sent admin report email to {admin_user.username}")
            except Exception as e:
                print(f"    ❌ Admin report email error: {e}")

        # Send via Telegram
        if admin_user.telegram_chat_id and settings.TELEGRAM_BOT_TOKEN:
            try:
                bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
                asyncio.run(bot.send_message(
                    chat_id=admin_user.telegram_chat_id,
                    text=f"<b>{subject}</b>\n\n{message.strip()}",
                    parse_mode=ParseMode.HTML
                ))
                print(f"    📱 Sent admin report telegram to {admin_user.username}")
            except Exception as e:
                print(f"    ❌ Admin report telegram error: {e}")

    def send_simple_notification(self, user: User, subject: str, message: str):
        """Send a general notification (not job-specific)"""
        
        # Create notification record
        notification = Notification(
            user_id=user.id,
            title=subject,
            message=message,
            notification_type='system_alert',
            is_read=False,
            is_clicked=False,
            sent_at=_dt.utcnow()
        )
        
        # Send via email
        if user.email and user.email != f"{user.username}@twitter.placeholder":
            try:
                if settings.SMTP_USER and settings.SMTP_PASSWORD:
                    display_name = user.display_name or user.username
                    
                    msg = MIMEMultipart()
                    msg['From'] = settings.SMTP_USER
                    msg['To'] = user.email or ""
                    msg['Subject'] = subject
                    
                    body = f"""
Hello {display_name}!

{message}

---
X Job Bot
Manage your alerts: {settings.FRONTEND_URL}/settings
                    """
                    
                    msg.attach(MIMEText(body, 'plain'))
                    
                    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                        server.starttls()
                        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                        server.send_message(msg)
                    
                    notification.sent_via_email = True
            except Exception as e:
                print(f"    ❌ System Email error: {e}")
                notification.sent_via_email = False
        
        # Send via telegram
        if user.telegram_chat_id:
            try:
                # TODO: Implement telegram bot sending for general messages
                notification.sent_via_telegram = True
            except Exception as e:
                print(f"    ❌ System Telegram error: {e}")
                notification.sent_via_telegram = False
        
        # Save notification
        try:
            self.db.add(notification)
            self.db.commit()
            print(f"    ✉️ Sent system alert to {user.username}")
        except Exception as e:
            print(f"    ❌ Failed to save system notification: {e}")
            self.db.rollback()
            raise