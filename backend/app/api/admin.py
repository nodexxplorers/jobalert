# backend/app/api/admin.py
"""
Admin Management API - User & System Management
"""

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, or_, update, delete, and_
from datetime import datetime, timedelta
from typing import List, Optional
from pydantic import BaseModel, EmailStr

from app.core.database import get_db, SessionLocal
from app.models.user import User
from app.models.job import Job
from app.models.notification import Notification
from app.models.system_status import SystemStatus
from app.core.security import require_admin

router = APIRouter(prefix="/admin", tags=["admin"])


# ============================================================================
# SCHEMAS
# ============================================================================

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    is_admin: Optional[bool] = None
    alert_speed: Optional[str] = None
    preferences: Optional[List[str]] = None


class BulkActionRequest(BaseModel):
    user_ids: List[int]
    action: str  # 'activate', 'deactivate', 'delete', 'verify', 'promote_admin', 'demote_admin'


class SystemSettings(BaseModel):
    scraping_enabled: bool
    scraping_interval_minutes: int
    max_jobs_per_scrape: int
    notification_rate_limit: int
    maintenance_mode: bool


# ============================================================================
# USER MANAGEMENT
# ============================================================================

@router.get("/overview")
def get_admin_overview(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get admin dashboard overview statistics with auto-reset for stuck scraping
    """
    from datetime import datetime, timedelta
    
    # Check if scraping has been stuck for more than 30 minutes
    status = db.query(SystemStatus).first()
    if status and status.is_scraping:
        # Check if updated_at is more than 30 minutes ago
        if status.updated_at:
            time_since_update = datetime.utcnow() - status.updated_at.replace(tzinfo=None)
            if time_since_update > timedelta(minutes=30):
                # Auto-reset stuck scraping
                status.is_scraping = False
                status.last_error = f"Auto-reset: Scraping appeared stuck (no update for {time_since_update.total_seconds()/60:.0f} minutes)"
                db.commit()
                print(f"⚠️ Auto-reset stuck scraping status (stuck for {time_since_update.total_seconds()/60:.0f} minutes)", flush=True)
    
    # Get admin dashboard overview statistics
    # User stats
    total_users = db.query(func.count(User.id)).scalar()
    
    # Active users (logged in last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    active_users = db.query(func.count(User.id)).filter(User.last_login >= thirty_days_ago).scalar()
    active_percentage = round((active_users / total_users * 100) if total_users > 0 else 0, 1)
    
    # New users this week
    one_week_ago = datetime.utcnow() - timedelta(days=7)
    new_users_week = db.query(func.count(User.id)).filter(User.created_at >= one_week_ago).scalar()

    # Job stats
    total_jobs = db.query(func.count(Job.id)).scalar()
    
    # Jobs today
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    jobs_today = db.query(func.count(Job.id)).filter(Job.created_at >= today_start).scalar()
    
    # Duplicate stats
    duplicate_jobs = db.query(func.count(Job.id)).filter(Job.is_duplicate == True).scalar()
    
    # Notification stats
    total_notifications = db.query(func.count(Notification.id)).scalar() or 0
    notifications_today = db.query(func.count(Notification.id)).filter(Notification.sent_at >= today_start).scalar() or 0
    
    avg_notifications = round((total_notifications / total_users) if total_users > 0 else 0, 1)

    return {
        "users": {
            "total": total_users,
            "active_percentage": active_percentage,
            "new_this_week": new_users_week
        },
        "jobs": {
            "total": total_jobs,
            "today": jobs_today,
            "duplicate_rate": duplicate_jobs
        },
        "notifications": {
            "total": total_notifications,
            "today": notifications_today,
            "avg_per_user": avg_notifications
        },
        "system": db.query(SystemStatus).first()
    }

@router.post("/system/reset-status")
def reset_system_status(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Manually reset the system scraping status (set is_scraping to False)
    Use this if scraping appears stuck
    """
    try:
        status = db.query(SystemStatus).first()
        if not status:
            status = SystemStatus(is_scraping=False)
            db.add(status)
        else:
            status.is_scraping = False
            status.last_error = "Manually reset by admin"
        
        db.commit()
        db.refresh(status)
        return {
            "message": "System status reset successfully", 
            "status": "idle",
            "is_scraping": False
        }
    except Exception as e:
        db.rollback()
        return {
            "message": f"Failed to reset status: {str(e)}",
            "status": "error"
        }

@router.get("/users")
def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = None,
    status: Optional[str] = None,  # 'active', 'inactive', 'verified', 'unverified'
    sort_by: str = Query("created_at", regex="^(created_at|last_login|email)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    List all users with filtering and pagination
    """
    
    # Build query
    query = db.query(User)
    
    # Apply filters
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                User.email.ilike(search_term),
                User.username.ilike(search_term),
                User.display_name.ilike(search_term)
            )
        )
    
    if status == 'active':
        query = query.filter(User.is_active == True)
    elif status == 'inactive':
        query = query.filter(User.is_active == False)
    
    # Apply sorting
    sort_column = getattr(User, sort_by)
    if sort_order == 'desc':
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(sort_column)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    users = query.offset(skip).limit(limit).all()
    
    # Format response
    users_data = []
    for user in users:
        users_data.append({
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "display_name": user.display_name,
            "twitter_name": user.display_name or user.username,
            "twitter_username": user.username,
            "is_active": user.is_active,
            "is_verified": getattr(user, 'is_verified', False), # Handle case where attr might be missing
            "is_admin": user.is_admin,
            "created_at": user.created_at,
            "last_login": user.last_login or user.created_at
        })
    
    return {
        "users": users_data,
        "total": total,
        "page": skip // limit + 1,
        "pages": (total + limit - 1) // limit
    }


@router.get("/users/{user_id}")
def get_user_details(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific user
    """
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user's notification stats
    notification_count = db.query(func.count(Notification.id)).filter(Notification.user_id == user_id).scalar() or 0
    
    # Get user's matched jobs count
    jobs_count = 0
    if user.preferences:
         jobs_count = db.query(func.count(Job.id)).filter(Job.category.in_(user.preferences)).scalar()
    
    # Get recent notifications
    recent_notifications = db.query(Notification)\
        .filter(Notification.user_id == user_id)\
        .order_by(desc(Notification.sent_at))\
        .limit(10).all()
    
    return {
        "user": {
            "id": user.id,
            "email": user.email,
            "twitter_id": user.twitter_id,
            "username": user.username,
            "display_name": user.display_name,
            "profile_image": user.profile_image,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "is_admin": user.is_admin,
            "preferences": user.preferences,
            "alert_speed": user.alert_speed,
            "telegram_chat_id": user.telegram_chat_id,
            "created_at": user.created_at,
            "last_login": user.last_login
        },
        "stats": {
            "total_notifications": notification_count,
            "total_jobs_matched": jobs_count,
            "days_active": (datetime.utcnow() - user.created_at).days
        },
        "recent_activity": [
            {
                "id": n.id,
                "type": n.notification_type,
                "created_at": n.sent_at,
                "status": "read" if n.is_read else "unread"
            }
            for n in recent_notifications
        ]
    }


@router.patch("/users/{user_id}")
def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Update user details
    """
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update fields
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    
    return {
        "message": "User updated successfully",
        "user": {
            "id": user.id,
            "email": user.email,
            "is_active": user.is_active
        }
    }


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Delete a user (soft delete - mark as inactive)
    """
    
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Soft delete
    user.is_active = False
    user.deleted_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "User deleted successfully"}


@router.post("/users/bulk-action")
def bulk_user_action(
    action_request: BulkActionRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Perform bulk actions on multiple users
    """
    
    user_ids = action_request.user_ids
    action = action_request.action
    
    if not user_ids:
        raise HTTPException(status_code=400, detail="No users selected")
    
    # Prevent admin from affecting themselves
    if current_user.id in user_ids and action == 'delete':
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    
    # Perform action
    if action == 'activate':
        db.query(User).filter(User.id.in_(user_ids)).update({User.is_active: True}, synchronize_session=False)
    elif action == 'deactivate':
        db.query(User).filter(User.id.in_(user_ids)).update({User.is_active: False}, synchronize_session=False)
    elif action == 'verify':
        db.query(User).filter(User.id.in_(user_ids)).update({User.is_verified: True}, synchronize_session=False)
    elif action == 'promote_admin':
        # Prevent demoting yourself
        if current_user.id in user_ids:
            raise HTTPException(status_code=400, detail="Cannot change your own admin status")
        db.query(User).filter(User.id.in_(user_ids)).update({User.is_admin: True}, synchronize_session=False)
    elif action == 'demote_admin':
        # Prevent demoting yourself
        if current_user.id in user_ids:
            raise HTTPException(status_code=400, detail="Cannot change your own admin status")
        db.query(User).filter(User.id.in_(user_ids)).update({User.is_admin: False}, synchronize_session=False)
    elif action == 'delete':
        db.query(User).filter(User.id.in_(user_ids)).update({User.is_active: False, User.deleted_at: datetime.utcnow()}, synchronize_session=False)
    else:
        raise HTTPException(status_code=400, detail="Invalid action")
    
    db.commit()
    
    return {
        "message": f"Action '{action}' performed on {len(user_ids)} users",
        "affected_users": len(user_ids)
    }


@router.get("/users/export")
def export_users(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Export all users to CSV
    """
    from fastapi.responses import Response
    import csv
    from io import StringIO
    
    users = db.query(User).all()
    
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'ID', 'Username', 'Email', 'Display Name', 'Is Active', 
        'Is Verified', 'Is Admin', 'Created At', 'Last Login', 
        'Preferences', 'Alert Speed'
    ])
    
    # Write data
    for user in users:
        writer.writerow([
            user.id,
            user.username,
            user.email or '',
            user.display_name or '',
            user.is_active,
            user.is_verified,
            user.is_admin,
            user.created_at.isoformat() if user.created_at else '',
            user.last_login.isoformat() if user.last_login else '',
            ','.join(user.preferences) if user.preferences else '',
            user.alert_speed or ''
        ])
    
    output.seek(0)
    
    return Response(
        content=output.getvalue(),
        media_type='text/csv',
        headers={
            'Content-Disposition': f'attachment; filename=users-export-{datetime.now().strftime("%Y-%m-%d")}.csv'
        }
    )


# ============================================================================
# JOB MANAGEMENT
# ============================================================================

@router.get("/jobs")
def list_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    category: Optional[str] = None,
    is_duplicate: Optional[bool] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    List all jobs with filtering
    """
    
    query = db.query(Job)
    
    # Apply filters
    if category:
        query = query.filter(Job.category == category)
    
    if is_duplicate is not None:
        query = query.filter(Job.is_duplicate == is_duplicate)
    
    if date_from:
        query = query.filter(Job.created_at >= date_from)
    
    if date_to:
        query = query.filter(Job.created_at <= date_to)
    
    # Get total count
    total = query.count()
    
    # Order by newest first
    jobs = query.order_by(desc(Job.created_at)).offset(skip).limit(limit).all()
    
    return {
        "jobs": [
            {
                "id": job.id,
                "title": f"Job {job.tweet_id}",  # Placeholder as job doesn't have title
                "description": job.text[:200] + "..." if len(job.text) > 200 else job.text,
                "category": job.category,
                "budget": None, # Job model doesnt have budget
                "url": job.tweet_url,
                "is_duplicate": job.is_duplicate,
                "created_at": job.created_at
            }
            for job in jobs
        ],
        "total": total,
        "page": skip // limit + 1,
        "pages": (total + limit - 1) // limit
    }


@router.delete("/jobs/{job_id}")
def delete_job(
    job_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Delete a job (remove spam/inappropriate content)
    """
    
    job = db.query(Job).filter(Job.id == job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    db.delete(job)
    db.commit()
    
    return {"message": "Job deleted successfully"}


@router.post("/jobs/cleanup-duplicates")
def cleanup_duplicates(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Clean up old duplicate jobs
    """
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    deleted_count = db.query(Job).filter(
        and_(
            Job.is_duplicate == True,
            Job.created_at < cutoff_date
        )
    ).delete(synchronize_session=False)
    
    db.commit()
    
    return {
        "message": f"Cleaned up duplicates older than {days} days",
        "deleted_count": deleted_count
    }


# ============================================================================
# SYSTEM SETTINGS
# ============================================================================

@router.get("/settings")
def get_system_settings(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get current system settings
    """
    
    # In production, store these in a settings table
    # For now, return defaults
    return {
        "scraping_enabled": True,
        "scraping_interval_minutes": 5,
        "max_jobs_per_scrape": 100,
        "notification_rate_limit": 50,
        "maintenance_mode": False
    }


@router.put("/settings")
def update_system_settings(
    settings: SystemSettings,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Update system settings
    """
    
    # In production, save to database
    # For now, just validate and return
    
    return {
        "message": "Settings updated successfully",
        "settings": settings.dict()
    }


# ============================================================================
# SYSTEM ACTIONS
# ============================================================================

def run_scrape_background():
    """Helper function to run scrape in background using its own session"""
    import sys
    from app.services.job_scraping_service import JobScrapingService
    from app.models.system_status import SystemStatus
    
    db = SessionLocal()
    result = 0
    try:
        print("🚀 Starting background scrape task...", flush=True)
        sys.stdout.flush()
        service = JobScrapingService(db)
        result = service.scrape_all_categories()
        print(f"✅ Background scrape completed: {result} jobs found", flush=True)
        sys.stdout.flush()
        return result
    except Exception as e:
        print(f"❌ Background scraping failed: {e}", flush=True)
        import traceback
        print(traceback.format_exc(), flush=True)
        sys.stdout.flush()
        # Ensure status is reset even on error
        try:
            status = db.query(SystemStatus).first()
            if status:
                status.is_scraping = False
                status.last_error = str(e)[:500]
                db.commit()
        except Exception as status_error:
            print(f"⚠️ Failed to reset status on error: {status_error}", flush=True)
            db.rollback()
        raise
    finally:
        # Double-check status is reset
        try:
            status = db.query(SystemStatus).first()
            if status and status.is_scraping:
                print("⚠️ Status still shows scraping=True, forcing reset...", flush=True)
                status.is_scraping = False
                db.commit()
        except:
            pass
        db.close()

@router.post("/system/trigger-scrape")
def trigger_manual_scrape(
    background_tasks: BackgroundTasks,
    sync: bool = Query(False, description="Run synchronously to see output in real-time"),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Manually trigger a scraping job.
    
    If sync=True, runs synchronously and returns results immediately (use for testing/debugging).
    If sync=False, runs in background (default for production).
    """
    if sync:
        # Run synchronously - output will be visible in console
        try:
            from app.services.job_scraping_service import JobScrapingService
            service = JobScrapingService(db)
            new_jobs = service.scrape_all_categories()
            return {
                "message": f"Scraping completed synchronously. Found {new_jobs} new jobs.",
                "status": "success",
                "new_jobs": new_jobs,
                "sync": True
            }
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"❌ Synchronous scrape error: {error_trace}", flush=True)
            return {
                "message": f"Scraping failed: {str(e)}",
                "status": "error",
                "error": str(e),
                "traceback": error_trace
            }
    else:
        # Run in background
        background_tasks.add_task(run_scrape_background)
        return {
            "message": "Scraping process started in the background. Check console for output. New jobs will appear in a few minutes.",
            "status": "success",
            "sync": False,
            "note": "To see output in real-time, use ?sync=true parameter"
        }


@router.post("/system/send-test-notification")
def send_test_notification(
    user_id: Optional[int] = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Send a test notification to a specific user or ALL users
    """
    from app.services.notification_service import NotificationService
    
    users = []
    if user_id:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        users.append(user)
    else:
        # Broadcast to all active users
        users = db.query(User).filter(User.is_active == True).all()
    
    notification_service = NotificationService(db)
    
    count = 0
    for user in users:
        print(f"📣 Sending test notification to {user.username}")
        notification_service.send_simple_notification(
            user=user,
            subject="🚀 Test Notification",
            message="This is a test notification from the Admin Dashboard. If you're seeing this, your notification channels are working correctly!"
        )
        count += 1
    
    return {
        "message": f"Test notification sent to {count} users",
        "status": "success",
        "count": count
    }


@router.post("/system/migrate-categories")
def migrate_categories(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Migrate all users and jobs to use hyphenated-categories (e.g. video_editing -> video-editing)
    """
    category_map = {
        'video_editing': 'video-editing',
        'web_development': 'web-dev',
        'content_writing': 'content-writing',
        'graphic_design': 'design',
        'motion_graphics': 'motion-graphics'
    }
    
    users_updated = 0
    jobs_updated = 0
    
    from app.models.user import User
    from app.models.job import Job
    
    # Update users
    users = db.query(User).all()
    for user in users:
        if user.preferences:
            new_prefs = []
            changed = False
            for pref in user.preferences:
                if pref in category_map:
                    new_prefs.append(category_map[pref])
                    changed = True
                else:
                    new_prefs.append(pref)
            
            if changed:
                user.preferences = new_prefs
                users_updated += 1
    
    # Update jobs
    jobs = db.query(Job).all()
    for job in jobs:
        if job.category in category_map:
            job.category = category_map[job.category]
            jobs_updated += 1
    
    db.commit()
    
    return {
        "message": "Migration completed",
        "users_updated": users_updated,
        "jobs_updated": jobs_updated
    }

@router.post("/system/update-cookies")
def update_twitter_cookies(
    payload: dict,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Update the Twitter session cookies used for scraping.
    Pasting valid exported JSON cookies allows bypassing login challenges.
    """
    try:
        cookies = payload.get("cookies")
        if not cookies:
            raise HTTPException(status_code=400, detail="No cookies provided")
            
        status = db.query(SystemStatus).first()
        if not status:
            status = SystemStatus(twitter_cookies=cookies)
            db.add(status)
        else:
            status.twitter_cookies = cookies
            
        db.commit()
        return {"message": "Twitter cookies updated successfully", "status": "success"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))