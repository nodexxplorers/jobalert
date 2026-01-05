# FILE: backend/app/tasks/scraping_tasks.py
# ============================================================================

from app.core.celery_app import celery_app
from app.core.database import SessionLocal
from app.services.job_scraping_service import JobScrapingService
from datetime import datetime

@celery_app.task(name="app.tasks.scraping_tasks.scrape_all_categories")
def scrape_all_categories():
    """
    Periodic task to scrape all categories.
    Uses unified JobScrapingService for consistency.
    """
    print(f"🔄 Starting scheduled scraping task at {datetime.now()}")
    db = SessionLocal()
    
    try:
        service = JobScrapingService(db)
        new_jobs = service.scrape_all_categories()
        
        return {
            "success": True,
            "new_jobs": new_jobs,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        print(f"❌ Scheduled scraping task error: {e}")
        return {
            "success": False,
            "error": str(e)
        }
    
    finally:
        db.close()