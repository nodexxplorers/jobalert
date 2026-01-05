# backend/app/api/notification.py

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.notification import Notification

router = APIRouter()

class NotificationUpdate(BaseModel):
    notification_ids: List[int]

@router.get("/notifications")
def get_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    notification_type: Optional[str] = None,
    is_read: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user notifications with filtering and pagination"""
    query = db.query(Notification).filter(Notification.user_id == current_user.id)
    
    if notification_type:
        query = query.filter(Notification.notification_type == notification_type)
    
    if is_read is not None:
        query = query.filter(Notification.is_read == is_read)
        
    total = query.count()
    notifications = query.order_by(desc(Notification.sent_at)).offset(skip).limit(limit).all()
    
    return notifications

@router.get("/notifications/stats")
def get_notification_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get notification statistics for current user"""
    total = db.query(func.count(Notification.id)).filter(Notification.user_id == current_user.id).scalar() or 0
    unread = db.query(func.count(Notification.id)).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).scalar() or 0
    
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today_count = db.query(func.count(Notification.id)).filter(
        Notification.user_id == current_user.id,
        Notification.sent_at >= today_start
    ).scalar() or 0
    
    # Calculate this week (last 7 days)
    week_start = datetime.now(timezone.utc) - timedelta(days=7)
    week_count = db.query(func.count(Notification.id)).filter(
        Notification.user_id == current_user.id,
        Notification.sent_at >= week_start
    ).scalar() or 0
    
    return {
        "total": total,
        "unread": unread,
        "read": total - unread,
        "today": today_count,
        "this_week": week_count
    }

@router.post("/notifications/mark-read")
def mark_as_read(
    update_data: NotificationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark specific notifications as read"""
    db.query(Notification).filter(
        Notification.id.in_(update_data.notification_ids),
        Notification.user_id == current_user.id
    ).update({"is_read": True, "read_at": func.now()}, synchronize_session=False)
    
    db.commit()
    return {"message": f"Marked {len(update_data.notification_ids)} notifications as read"}

@router.post("/notifications/mark-all-read")
def mark_all_as_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark all notifications as read for current user"""
    db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).update({"is_read": True, "read_at": func.now()}, synchronize_session=False)
    
    db.commit()
    return {"message": "All notifications marked as read"}

@router.post("/notifications/{notification_id}/click")
def mark_as_clicked(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Record notification click"""
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
        
    notification.is_clicked = True
    notification.clicked_at = func.now()
    
    # Also mark as read if not already
    if not notification.is_read:
        notification.is_read = True
        notification.read_at = func.now()
        
    db.commit()
    return {"message": "Notification click recorded"}

@router.delete("/notifications/{notification_id}")
def delete_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a notification"""
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
        
    db.delete(notification)
    db.commit()
    return {"message": "Notification deleted"}

@router.delete("/notifications")
def delete_all_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete all notifications for current user"""
    db.query(Notification).filter(Notification.user_id == current_user.id).delete(synchronize_session=False)
    db.commit()
    return {"message": "All notifications deleted"}
