# backend/app/api/jobs.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.job import Job
from app.schemas.job import JobResponse

router = APIRouter(prefix="/jobs", tags=["jobs"])

from sqlalchemy import or_

@router.get("", response_model=List[JobResponse])
def get_jobs(
    category: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get recent jobs"""
    print(f"DEBUG: Fetching jobs for category: {category}")
    query = db.query(Job).order_by(Job.created_at.desc())
    
    if category:
        # Compatibility: handle both video-editing and video_editing
        alt_category = category.replace('-', '_') if '-' in category else category.replace('_', '-')
        query = query.filter(or_(Job.category == category, Job.category == alt_category))
    
    if search:
        search_filter = f"%{search}%"
        query = query.filter(Job.text.ilike(search_filter))
    
    jobs = query.limit(limit).all()
    print(f"DEBUG: Found {len(jobs)} jobs")
    return jobs

@router.get("/saved", response_model=List[JobResponse])
def get_saved_jobs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get jobs saved by the current user"""
    return current_user.saved_jobs

@router.post("/{job_id}/save")
def save_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Save a job for the current user"""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job not in current_user.saved_jobs:
        current_user.saved_jobs.append(job)
        db.commit()
    
    return {"message": "Job saved successfully"}

@router.delete("/{job_id}/unsave")
def unsave_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Unsave a job for the current user"""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job in current_user.saved_jobs:
        current_user.saved_jobs.remove(job)
        db.commit()
    
    return {"message": "Job unsaved successfully"}
