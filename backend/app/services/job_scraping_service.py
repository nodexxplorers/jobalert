 # FILE: backend/app/services/job_scraping_service.py
# ============================================================================

from typing import List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.job import Job
from app.models.user import User
from app.models.notification import Notification
from app.models.system_status import SystemStatus
from app.services.twitter_scraper import TwitterScraper
from app.services.notification_service import NotificationService
from datetime import datetime
import time
import sys
import asyncio
from app.config import settings

class JobScrapingService:
    """
    Orchestrates job scraping and notification delivery
    """
    
    # Search queries by category - improved with better search terms
    # Search queries by category - Expanded to 32 roles
    SEARCH_QUERIES = {
        # --- Tech & Development ---
        'software-dev': [
            'hiring software developer', 'software engineer needed', 'backend developer job', 
            'frontend developer hiring', 'full stack developer needed', 'remote developer job'
        ],
        'data-science': [
            'hiring data scientist', 'data analyst needed', 'machine learning engineer job',
            'hiring data engineer', 'AI engineer needed'
        ],
        'web-dev': [
            'hiring web developer', 'web designer needed', 'wordpress developer job',
            'shopify developer needed', 'react developer hiring'
        ],
        'blockchain': [
            'hiring blockchain developer', 'solidity developer needed', 'rust developer job',
            'web3 developer hiring', 'smart contract engineer needed'
        ],
        'smart-contract': [
            'smart contract developer', 'smart contract auditor needed', 'solidity engineer job'
        ],
        'nft-manager': [
            'hiring nft project manager', 'nft community manager needed', 'nft mod needed',
            'web3 project manager'
        ],
        'crypto-analyst': [
            'hiring crypto analyst', 'crypto researcher needed', 'tokenomics expert job',
            'web3 analyst needed'
        ],
        
        # --- Design & Creative ---
        'design': [
            'hiring graphic designer', 'graphic designer needed', 'brand designer job',
            'logo designer needed', 'illustrator needed'
        ],
        'ux-ui': [
            'hiring ui ux designer', 'product designer needed', 'ux researcher job',
            'ui designer needed', 'web designer hiring'
        ],
        'video-editing': [
            'hiring video editor', 'video editor needed', 'premiere pro editor job',
            'youtube editor needed', 'video producer hiring'
        ],
        'motion-graphics': [
            'hiring motion designer', 'motion graphics artist needed', 'after effects animator',
            '3d animator needed'
        ],
        'photographer': [
            'hiring freelance photographer', 'photographer needed', 'event photographer job',
            'product photographer needed'
        ],
        'music-producer': [
            'hiring music producer', 'sound engineer needed', 'audio engineer job',
            'beatmaker needed', 'music composer hiring'
        ],
        'artist': [
            'hiring artist', 'illustrator needed', 'concept artist job',
            'digital artist needed', 'nft artist hiring'
        ],
        'film-crew': [
            'hiring film crew', 'videographer needed', 'camera operator job',
            'production assistant needed', 'film editor hiring'
        ],

        # --- Marketing & Social ---
        'marketing': [
            'hiring marketing consultant', 'marketing manager needed', 'digital marketing job',
            'growth marketer needed', 'marketing strategist hiring'
        ],
        'social-media': [
            'hiring social media manager', 'smm needed', 'social media specialist job',
            'content creator needed', 'instagram manager hiring'
        ],
        'content-writer': [
            'hiring content writer', 'blog writer needed', 'article writer job',
            'technical writer needed', 'ghostwriter hiring'
        ],
        'copywriter': [
            'hiring copywriter', 'copywriting job', 'email copywriter needed',
            'ad copywriter hiring', 'sales copywriter needed'
        ],
        'community-manager': [
            'hiring community manager', 'discord mod needed', 'community lead job',
            'social media moderator needed'
        ],
        'dev-advocate': [
            'hiring developer advocate', 'devrel job', 'developer relations manager',
            'technical evangelist needed'
        ],
        'brand-ambassador': [
            'hiring brand ambassador', 'brand rep needed', 'influencer marketing job',
            'brand advocate needed'
        ],
        'growth-hacker': [
            'hiring growth hacker', 'growth manager needed', 'user acquisition job',
            'growth marketing manager'
        ],
        'seo-specialist': [
            'hiring seo specialist', 'seo expert needed', 'seo manager job',
            'link builder needed'
        ],
        'newsletter-writer': [
            'hiring newsletter writer', 'newsletter editor needed', 'substack writer job',
            'email marketer needed'
        ],
        'podcast-producer': [
            'hiring podcast producer', 'podcast editor needed', 'audio producer job',
            'podcast manager needed'
        ],

        # --- Business & Operations ---
        'product-manager': [
            'hiring product manager', 'product owner needed', 'head of product job',
            'technical product manager'
        ],
        'project-manager': [
            'hiring project manager', 'project coordinator needed', 'program manager job',
            'scrum master needed'
        ],
        'startup-founder': [
            'hiring cofounder', 'startup co-founder needed', 'founding engineer job',
            'partner needed startup'
        ],
        'early-stage': [
            'hiring founding member', 'early employee startup', 'join our startup',
            'startup jobs'
        ],
        'sales-rep': [
            'hiring sales representative', 'sales rep needed', 'account executive job',
            'business development manager', 'sales closer needed'
        ],
        'customer-success': [
            'hiring customer success manager', 'csm needed', 'customer support job',
            'client success manager'
        ],
        'virtual-assistant': [
            'hiring virtual assistant', 'va needed', 'executive assistant remote',
            'personal assistant needed'
        ],
        'intern': [
            'hiring interns', 'internship remote', 'marketing intern',
            'developer intern', 'design intern'
        ],
    }
    
    def __init__(self, db: Session):
        self.db = db
        self.scraper = TwitterScraper(headless=True)
        self.notification_service = NotificationService(db)
    
    def _get_status_record(self) -> SystemStatus:
        """Get or create the single status record"""
        status = self.db.query(SystemStatus).first()
        if not status:
            status = SystemStatus(is_scraping=False)
            self.db.add(status)
            self.db.commit()
            self.db.refresh(status)
        return status

    def scrape_all_categories(self):
        """Main entry point: Scrape all categories and notify users"""
        import sys
        start_time = time.time()
        
        # Force flush output to ensure it's visible
        sys.stdout.flush()
        sys.stderr.flush()
        print("\n" + "="*70, flush=True)
        print("🤖 STARTING JOB SCRAPING BOT", flush=True)
        print(f"⏰ Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", flush=True)
        print(f"📊 Will search {sum(len(q) for q in self.SEARCH_QUERIES.values())} queries across {len(self.SEARCH_QUERIES)} categories", flush=True)
        print("="*70 + "\n", flush=True)
        sys.stdout.flush()
        
        # Get or create status record
        status = self._get_status_record()
        try:
            status.is_scraping = True
            status.last_error = ""
            self.db.commit()
        except Exception as init_error:
            print(f"⚠️ Failed to initialize status: {init_error}", flush=True)
            sys.stdout.flush()
            self.db.rollback()
        
        # Login if credentials provided - CRITICAL for Twitter/X
        login_success = False
        if settings.TWITTER_USERNAME and settings.TWITTER_PASSWORD:
            print("🔐 Attempting to login to Twitter/X...", flush=True)
            print(f"   Username: {settings.TWITTER_USERNAME}", flush=True)
            print(f"   Email: {settings.TWITTER_EMAIL or 'Not provided'}", flush=True)
            sys.stdout.flush()
            login_success = self.scraper.login(
                settings.TWITTER_USERNAME,
                settings.TWITTER_PASSWORD,
                settings.TWITTER_EMAIL,
                cookies_json=status.twitter_cookies
            )
            if login_success:
                print("✅ Successfully logged in to Twitter/X - search should work now", flush=True)
            else:
                print("❌ CRITICAL: Login failed!", flush=True)
                print("   ⚠️ Twitter/X REQUIRES authentication to view search results", flush=True)
                print("   💡 Without login, you will get 0 results", flush=True)
                print("   🔧 Check your credentials in .env file:", flush=True)
                print("      - TWITTER_USERNAME", flush=True)
                print("      - TWITTER_PASSWORD", flush=True)
                print("      - TWITTER_EMAIL (may be required)", flush=True)
            sys.stdout.flush()
        else:
            print("❌ CRITICAL: No Twitter credentials found!", flush=True)
            print("   ⚠️ Twitter/X REQUIRES authentication to view search results", flush=True)
            print("   💡 Set these in your .env file:", flush=True)
            print("      - TWITTER_USERNAME=your_username", flush=True)
            print("      - TWITTER_PASSWORD=your_password", flush=True)
            print("      - TWITTER_EMAIL=your_email (may be required)", flush=True)
            print("   ⚠️ Continuing without login - will likely get 0 results", flush=True)
            sys.stdout.flush()
        
        total_new_jobs = 0
        user_notifications = {}  # user_id -> List[Job]
        category_start_time = time.time()
        try:
            for idx, (category, queries) in enumerate(self.SEARCH_QUERIES.items(), 1):
                category_start = time.time()
                print(f"\n📂 Category {idx}/{len(self.SEARCH_QUERIES)}: {category.upper()}", flush=True)
                print("-" * 70, flush=True)
                
                category_jobs = []
                
                # Search with multiple queries
                for q_idx, query in enumerate(queries, 1):
                    try:
                        query_start = time.time()
                        print(f"  🔍 Query {q_idx}/{len(queries)}: '{query}'", flush=True)
                        sys.stdout.flush()
                        # TwitterScraper handles its own internal responsiveness check
                        jobs = self.scraper.search_jobs(query, max_results=10)
                        query_time = time.time() - query_start
                        print(f"  📊 Found {len(jobs)} jobs in {query_time:.1f}s from '{query}'", flush=True)
                        sys.stdout.flush()
                        category_jobs.extend(jobs)
                        time.sleep(3)  # Be polite to Twitter/X
                    except Exception as e:
                        print(f"  ❌ Error searching '{query}': {e}", flush=True)
                        import traceback
                        print(f"  📋 Traceback: {traceback.format_exc()}", flush=True)
                        sys.stdout.flush()
                        # If a query fails, we try to keep going with the next one
                        continue
                
                # Remove duplicates
                unique_jobs = {job['tweet_id']: job for job in category_jobs}
                category_jobs = list(unique_jobs.values())
                
                print(f"✅ Found {len(category_jobs)} unique jobs for {category}", flush=True)
                sys.stdout.flush()
                
                # Process and save jobs
                new_jobs, notifications = self._process_jobs(category_jobs, category)
                total_new_jobs += new_jobs
                
                # Update user_notifications map
                for user_id, job in notifications:
                    if user_id not in user_notifications:
                        user_notifications[user_id] = []
                    user_notifications[user_id].append(job)
                
                category_time = time.time() - category_start
                print(f"⏱️ Category '{category}' completed in {category_time:.1f} seconds ({category_time/60:.1f} min)", flush=True)
                sys.stdout.flush()
                # Send summary emails and telegrams after all categories are done
                if user_notifications:
                    print(f"\n📧 Sending summary notifications to {len(user_notifications)} users...", flush=True)
                    for user_id, jobs in user_notifications.items():
                        user = self.db.query(User).get(user_id)
                        if user:
                            # Send batch email
                            self.notification_service.send_batch_job_notification(user, jobs)
                            
                            # Telegram summary
                            if user.telegram_chat_id and settings.TELEGRAM_BOT_TOKEN:
                                asyncio.run(self.notification_service.send_telegram_summary(user, jobs))

        finally:
            # ALWAYS update status to not scraping
            end_time_dt = datetime.now()
            total_time = time.time() - start_time
            
            # Send admin report
            try:
                admins = self.db.query(User).filter(User.is_admin == True).all()
                if admins:
                    stats = {
                        "new_jobs": total_new_jobs,
                        "categories_count": len(self.SEARCH_QUERIES),
                        "start_time": datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S'),
                        "end_time": end_time_dt.strftime('%Y-%m-%d %H:%M:%S'),
                        "errors_count": 0, # Simplified for now
                        "last_error": ""
                    }
                    print(f"\n📊 Sending scrape report to {len(admins)} admins...", flush=True)
                    for admin in admins:
                        self.notification_service.send_admin_scrape_report(admin, stats)
            except Exception as report_error:
                print(f"⚠️ Failed to send admin report: {report_error}", flush=True)

            try:
                # Re-fetch status to avoid stale session issues
                status = self._get_status_record()
                status.is_scraping = False
                status.last_scrape_at = func.now()
                status.last_jobs_found = total_new_jobs
                self.db.commit()
                print(f"✅ System status reset: is_scraping=False", flush=True)
            except Exception as commit_error:
                print(f"⚠️ Failed to commit status update: {commit_error}", flush=True)
                sys.stdout.flush()
                self.db.rollback()
            
            try:
                self.scraper.close()
            except Exception as close_error:
                print(f"⚠️ Error closing scraper: {close_error}", flush=True)
            sys.stdout.flush()
        
        total_time = time.time() - start_time
        print("\n" + "="*70, flush=True)
        print(f"✅ SCRAPING COMPLETE - {total_new_jobs} NEW JOBS ADDED", flush=True)
        print(f"⏱️ Total time: {total_time:.1f} seconds ({total_time/60:.1f} minutes)", flush=True)
        print(f"⏰ End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", flush=True)
        print("="*70, flush=True)
        
        # Diagnostic summary
        if total_new_jobs == 0:
            print("\n⚠️ DIAGNOSTIC: No jobs were found. Possible reasons:", flush=True)
            print("  1. Twitter/X might be blocking the scraper", flush=True)
            print("  2. Search queries might not be matching current job posts", flush=True)
            print("  3. Login might have failed (check credentials)", flush=True)
            print("  4. Twitter/X page structure might have changed", flush=True)
            print("  5. All found jobs might already exist in database", flush=True)
            print("\n💡 TIPS:", flush=True)
            print("  - Check if Twitter credentials are correct", flush=True)
            print("  - Try running scraper manually to see detailed logs", flush=True)
            print("  - Verify Twitter/X is accessible from your server", flush=True)
            print("  - Check if jobs already exist in database", flush=True)
        
        print("="*70 + "\n", flush=True)
        sys.stdout.flush()
        
        return total_new_jobs
    
    def _process_jobs(self, jobs: List[Dict], category: str) -> (int, List):
        """Process scraped jobs and return matched notifications"""
        new_jobs_count = 0
        all_notifications = []
        
        for job_data in jobs:
            try:
                # Check if job already exists
                existing = self.db.query(Job).filter(
                    Job.tweet_id == job_data['tweet_id']
                ).first()
                
                if existing:
                    continue
                
                # Create new job
                job = Job(
                    tweet_id=job_data['tweet_id'],
                    tweet_url=job_data['tweet_url'],
                    author=job_data['author'],
                    username=job_data['username'],
                    text=job_data['text'],
                    category=category,
                    posted_at=job_data['posted_at'],
                    engagement=job_data['engagement']
                )
                
                self.db.add(job)
                self.db.commit()
                self.db.refresh(job)
                
                new_jobs_count += 1
                print(f"  💾 Saved job: {job.tweet_id}", flush=True)
                sys.stdout.flush()
                
                # Find matching users and notify
                notifications = self._notify_matching_users(job, category)
                all_notifications.extend(notifications)
            except Exception as e:
                print(f"  ⚠️ Error processing job {job_data.get('tweet_id', 'unknown')}: {e}", flush=True)
                sys.stdout.flush()
                self.db.rollback()
                continue  # Continue with next job
        
        return new_jobs_count, all_notifications
    
    def _notify_matching_users(self, job: Job, category: str) -> List:
        """Find users interested in this category and return (user_id, job) pairs"""
        matched_notifications = []
        
        # Find all active users and filter by preferences in Python 
        # to avoid complex JSON operator issues across different DBs (like Postgres json vs jsonb)
        all_active_users = self.db.query(User).filter(
            User.is_active == True
        ).all()
        
        users = [u for u in all_active_users if u.preferences and category in u.preferences]
        
        if not users:
            return []
            
        print(f"  📨 Notifying {len(users)} users who are interested in {category}", flush=True)
        sys.stdout.flush()
        
        for user in users:
            # Check if keywords match (if user has keywords)
            if user.keywords and job.text:
                text_lower = job.text.lower()
                if not any(keyword.lower() in text_lower for keyword in user.keywords):
                    continue
            
            # Check if user already notified about this job
            existing_notification = self.db.query(Notification).filter(
                Notification.user_id == user.id,
                Notification.job_id == job.id
            ).first()
            
            if existing_notification:
                continue
            
            # Send notification (Database only record)
            self.notification_service.send_job_notification(user, job)
            matched_notifications.append((user.id, job))
            
        return matched_notifications