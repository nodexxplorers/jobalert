# FILE: backend/app/services/twitter_scraper.py
# Updated to use database-driven cookie injection and improved login flow.

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from typing import List, Dict, Optional
from datetime import datetime
import time
import re
import json
import os
from pathlib import Path
from app.models.job import Job
from app.models.user import User
from sqlalchemy.orm import Session

class TwitterScraper:
    """
    Selenium-based Twitter scraper for job postings
    Uses headless Chrome to scrape Twitter search results
    """
    
    
    def __init__(self, headless: bool = True):
        self.driver = None
        self.headless = headless
        self.setup_driver()
    
    def setup_driver(self):
        """Initialize Chrome driver with optimal settings"""
        options = Options()
        
        if self.headless:
            options.add_argument("--headless=new")
        
        # Use EAGER page load strategy to avoid waiting for heavy scripts/images
        options.page_load_strategy = 'eager'
        
        # Essential options for stability and avoiding renderer timeouts
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-renderer-backgrounding")
        options.add_argument("--disable-background-timer-throttling")
        options.add_argument("--disable-backgrounding-occluded-windows")
        options.add_argument("--disable-breakpad")
        options.add_argument("--disable-client-side-phishing-detection")
        options.add_argument("--disable-ipc-flooding-protection")
        options.add_argument("--password-store=basic")
        options.add_argument("--use-mock-keychain")
        
        # Avoid detection
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # User agent
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        try:
            try:
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=options)
            except Exception as e:
                print(f"⚠️ Failed to install autodetected Chrome driver: {e}")
                print("   Attempting to initialize using system default/PATH...")
                # Fallback: Try to launch without specifying path (hopes it is in PATH)
                self.driver = webdriver.Chrome(options=options)

            
            # Set page load timeout
            self.driver.set_page_load_timeout(30)
            
            # Execute CDP to avoid detection and BLOCK IMAGES to save memory/prevent timeouts
            self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            
            # Block images and media to keep the renderer light
            self.driver.execute_cdp_cmd('Network.setBlockedURLs', {
                "urls": ["*.jpg", "*.jpeg", "*.png", "*.gif", "*.svg", "*.mp4", "*.webm", "abs.twimg.com/emoji/*"]
            })
            self.driver.execute_cdp_cmd('Network.enable', {})
            
            print("✅ Chrome driver initialized (Strategy: Eager, Images Blocked)")
        except Exception as e:
            print(f"❌ Failed to initialize Chrome driver: {e}")
            raise
    
    def inject_cookies(self, cookies_json: str):
        """Inject JSON formatted cookies into the browser session with timeout protection"""
        try:
            import json
            cookies = json.loads(cookies_json)
            
            # First visit x.com just to set domain context - DO NOT wait for it to load
            print("   ⏳ Setting domain context for injection...")
            try:
                # Use a very short timeout - we just need the domain to match
                self.driver.set_page_load_timeout(5)
                self.driver.get("https://x.com/favicon.ico") # Load an tiny image instead of the whole site
            except Exception:
                pass
            
            # Reset timeout
            self.driver.set_page_load_timeout(30)
            
            for cookie in cookies:
                try:
                    # Fix common cookie issues for Selenium
                    if 'expiry' in cookie:
                        del cookie['expiry']
                    if 'sameSite' in cookie and cookie['sameSite'] not in ["Strict", "Lax", "None"]:
                        del cookie['sameSite']
                        
                    self.driver.add_cookie(cookie)
                except Exception:
                    pass
            
            print("   ✅ Cookies injected successfully")
            return True
        except Exception as e:
            print(f"   ❌ Failed to inject cookies: {e}")
            return False
    
    def _is_logged_in(self) -> bool:
        """Check if we're currently logged in by looking for account-related text or elements"""
        try:
            # We check the page source for indicators that we're NOT on a login prompt
            page_text = self.driver.page_source.lower()
            current_url = self.driver.current_url.lower()
            
            # If we see these, we are definitely NOT logged in
            login_indicators = ["/i/flow/login", "sign in", "login to x", "new to x?"]
            if any(indicator in current_url or (indicator in page_text and len(page_text) < 10000) for indicator in login_indicators):
                return False
                
            # If we see these, we ARE logged in
            auth_indicators = ["home", "explore", "notifications", "messages", "profile", "logout", "post", "tweet"]
            if any(indicator in page_text for indicator in auth_indicators):
                return True
                
            return True # Default to True and let the search try if we're not sure
        except:
            return False
    
    def login(self, username, password, email=None, cookies_json=None):
        """Log in to Twitter/X - CRITICAL for accessing search results"""
        if not self.driver:
            self.setup_driver()
        
        # Try injected cookies first if provided
        if cookies_json:
            print("🔑 Attempting to restore session from injected cookies...")
            if self.inject_cookies(cookies_json):
                # We skip navigating to /home and go straight to a check or search
                print("   ⏳ Verifying session status (Lightweight check)...")
                try:
                    self.driver.set_page_load_timeout(15)
                    self.driver.get("https://x.com/settings/account") # Lighter page than Home
                    time.sleep(3)
                    if self._is_logged_in():
                        print("✅ Session restored via injected cookies!")
                        return True
                except Exception:
                    # Even if it times out, we'll try to proceed to search
                    print("   ⚠️ Verification check timed out, will attempt to search anyway")
                    return True 
                
                print("⚠️ Injected cookies might be invalid, falling back to manual login...")
        
        # Database-driven cookie injection is now the primary method.
        # Manual login will trigger below if cookies are missing or expired.
        
        print(f"🔐 Logging in as {username}...")
        try:
            login_url = "https://x.com/i/flow/login"
            
            print(f"   Trying: {login_url}")
            self.driver.get(login_url)
            time.sleep(3)
            
            # Enter Username
            try:
                user_input = WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.NAME, "text"))
                )
                user_input.clear()
                user_input.send_keys(username)
                print("   ✅ Username entered")
            except Exception as e:
                print(f"   ❌ Could not find username field: {e}")
                return False
            
            # Click Next
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//span[text()='Next']"))
                )
                next_button = self.driver.find_element(By.XPATH, "//span[text()='Next']")
                self.driver.execute_script("arguments[0].click();", next_button)
                print("   ✅ Clicked Next")
                time.sleep(3)
            except Exception as e:
                print(f"   ❌ Could not click Next: {e}")
                return False
            
            # Handle verification challenge (email/phone)
            try:
                time.sleep(2)
                current_url = self.driver.current_url.lower()
                page_text = self.driver.page_source.lower()
                
                # Check if we're on a verification page
                if 'challenge' in current_url or 'unusual' in page_text or 'verify' in page_text:
                    print(f"   ⚠️ Verification challenge detected")
                    
                    if email:
                        try:
                            # Wait for and fill email/phone input
                            verify_input = WebDriverWait(self.driver, 10).until(
                                EC.presence_of_element_located((By.NAME, "text"))
                            )
                            verify_input.clear()
                            verify_input.send_keys(email)
                            print(f"   ✅ Entered email for verification: {email}")
                            
                            time.sleep(1)
                            
                            # Click Next on verification
                            verify_next = WebDriverWait(self.driver, 10).until(
                                EC.presence_of_element_located((By.XPATH, "//span[text()='Next']"))
                            )
                            self.driver.execute_script("arguments[0].click();", verify_next)
                            print(f"   ✅ Verification Next clicked")
                            time.sleep(5)
                        except Exception as e:
                            print(f"   ❌ Verification failed: {e}")
                            return False
            except:
                pass
            
            # Enter Password
            try:
                password_input = WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.NAME, "password"))
                )
                password_input.clear()
                password_input.send_keys(password)
                print("   ✅ Password entered")
            except Exception as e:
                print(f"   ❌ Could not find password field: {e}")
                return False
            
            # Click Login
            try:
                login_button = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//span[text()='Log in']"))
                )
                self.driver.execute_script("arguments[0].click();", login_button)
                print("   ✅ Clicked Login button")
            except:
                # Try pressing Enter instead
                try:
                    self.driver.find_element(By.NAME, "password").send_keys(Keys.RETURN)
                    print("   ✅ Pressed Enter on password field")
                except:
                    print("   ❌ Could not submit login")
                    return False
            
            # Wait for login to complete
            print("   ⏳ Waiting for login to complete...")
            for attempt in range(15):
                time.sleep(1)
                current_url = self.driver.current_url.lower()
                
                if '/home' in current_url or '/search' in current_url:
                    print("   ✅ Login successful!")
                    time.sleep(2)
                    
                    return True
                
                if '/i/flow/login' in current_url and attempt > 5:
                    print(f"   ❌ Still on login page after {attempt} seconds")
                    return False
            
            print("   ❌ Login timeout")
            return False
            
        except Exception as e:
            print(f"❌ Login failed with error: {e}")
            import traceback
            print(f"   📋 Traceback:\n{traceback.format_exc()}")
            return False

    def search_jobs(self, query: str, max_results: int = 20) -> List[Dict]:
        """
        Search Twitter for job posts
        
        Args:
            query: Search query (e.g., "video editor needed")
            max_results: Maximum number of results to return
        
        Returns:
            List of job dictionaries
        """
        jobs = []
        
        try:
            # Check if logged in
            if not self._is_logged_in():
                print(f"⚠️ Not logged in. Please ensure login() is called with credentials or cookies first.")
                # We don't return here because sometimes _is_logged_in gives false negatives 
                # or we might want to try searching anyway (though it usually fails on X)
            
            from urllib.parse import quote
            encoded_query = quote(query)
            search_url = f"https://x.com/search?q={encoded_query}&f=live"
            
            import sys
            print(f"🔍 Searching X/Twitter: '{query}'", flush=True)
            print(f"   URL: {search_url}", flush=True)
            sys.stdout.flush()
            
            from selenium.common.exceptions import TimeoutException
            
            try:
                # Use a slightly more aggressive timeout for the initial load
                self.driver.set_page_load_timeout(25)
                self.driver.get(search_url)
            except TimeoutException:
                print("   ⚠️ Search page load timed out - continuing anyway...")
            except Exception as e:
                if "renderer" in str(e).lower():
                    print("   ⚠️ Renderer timeout detected - browser is struggling but attempting to continue...")
                else:
                    raise e
            
            # Re-verify we aren't completely stuck
            time.sleep(3)
            current_url = self.driver.current_url
            
            # Check if redirected to login
            if '/i/flow/login' in current_url or 'login' in current_url:
                print("   ❌ CRITICAL: Redirected to login page")
                print("   💡 Session expired or cookies invalid")
                return jobs
            
            # Wait for tweets to load
            print("   ⏳ Waiting for page to load (5 seconds)...", flush=True)
            sys.stdout.flush()
            
            # Wait for either tweets to load OR login redirect
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'article[data-testid="tweet"]'))
                )
            except:
                # If tweets didn't load, tweets might use different selector
                time.sleep(5)
            
            current_url = self.driver.current_url
            print(f"   📍 Current URL: {current_url}")
            
            # Check if redirected to login
            if '/i/flow/login' in current_url or 'login' in current_url:
                print("   ❌ CRITICAL: Redirected to login page")
                print("   💡 Session expired - need to login again")
                return jobs
            
            # Try to find tweets
            tweets = self._find_tweets()
            
            if len(tweets) == 0:
                print(f"   ⚠️ No tweets found on first try, scrolling...")
                for i in range(3):
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)
                    tweets = self._find_tweets()
                    if len(tweets) > 0:
                        break
            
            print(f"📦 Found {len(tweets)} tweets")
            
            for tweet in tweets:
                if len(jobs) >= max_results:
                    break
                
                try:
                    job_data = self._parse_tweet(tweet)
                    if job_data and self._is_valid_job(job_data):
                        if not any(j['tweet_id'] == job_data['tweet_id'] for j in jobs):
                            jobs.append(job_data)
                except Exception as e:
                    continue
            
            print(f"✅ Collected {len(jobs)} valid jobs")
            
        except Exception as e:
            print(f"❌ Scraping error: {e}")
        
        return jobs
    
    def _find_tweets(self) -> List:
        """Find tweet elements using multiple selectors"""
        selectors = [
            'article[data-testid="tweet"]',
            'div[data-testid="tweet"]',
            'article[role="article"]',
        ]
        
        for selector in selectors:
            try:
                tweets = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if len(tweets) > 0:
                    return tweets
            except:
                continue
        
        return []
    
    def _parse_tweet(self, tweet_element) -> Optional[Dict]:
        """Parse a single tweet element"""
        try:
            # Get tweet link (contains tweet ID)
            time_elem = tweet_element.find_element(By.CSS_SELECTOR, 'time')
            link_elem = time_elem.find_element(By.XPATH, './ancestor::a')
            tweet_url = link_elem.get_attribute('href')
            
            if not tweet_url:
                return None
            
            tweet_id = tweet_url.split('/')[-1].split('?')[0]
            
            # Get username
            username_elem = tweet_element.find_element(
                By.CSS_SELECTOR,
                'div[data-testid="User-Name"] a'
            )
            username = username_elem.get_attribute('href').split('/')[-1]
            
            # Get author display name
            try:
                author_elem = tweet_element.find_element(
                    By.CSS_SELECTOR,
                    'div[data-testid="User-Name"] span'
                )
                author = author_elem.text
            except:
                author = username
            
            # Get tweet text
            try:
                text_elem = tweet_element.find_element(
                    By.CSS_SELECTOR,
                    'div[data-testid="tweetText"]'
                )
                text = text_elem.text
            except:
                text = ""
            
            # Get timestamp
            try:
                timestamp = time_elem.get_attribute('datetime')
            except:
                timestamp = datetime.now().isoformat()
            
            # Get engagement metrics
            engagement = {'likes': 0, 'retweets': 0, 'replies': 0}
            
            try:
                metrics = tweet_element.find_elements(By.CSS_SELECTOR, 'div[role="group"] button')
                for i, metric in enumerate(metrics[:3]):
                    try:
                        count_text = metric.get_attribute('aria-label')
                        if count_text:
                            numbers = re.findall(r'\d+', count_text)
                            if numbers:
                                count = int(numbers[0])
                                if i == 0:
                                    engagement['replies'] = count
                                elif i == 1:
                                    engagement['retweets'] = count
                                elif i == 2:
                                    engagement['likes'] = count
                    except:
                        continue
            except:
                pass
            
            return {
                'tweet_id': tweet_id,
                'tweet_url': tweet_url,
                'username': username,
                'author': author,
                'text': text,
                'posted_at': timestamp,
                'engagement': engagement
            }
            
        except Exception as e:
            return None
    
    def _is_valid_job(self, job_data: Dict) -> bool:
        """Validate if tweet is a genuine job posting"""
        text = job_data.get('text', '').lower()
        
        if not text or len(text) < 20:
            return False
        
        job_keywords = [
            'hiring', 'looking for', 'need', 'needed', 'seeking', 'wanted',
            'opportunity', 'position', 'job', 'freelance', 'remote', 'work',
            'editor', 'developer', 'writer', 'designer', 'animator',
            'apply', 'application', 'role', 'opening', 'vacancy'
        ]
        
        has_job_keyword = any(keyword in text for keyword in job_keywords)
        
        spam_keywords = [
            'click link in bio', 'dm for details only', 'dm me',
            'follow me', 'check my profile', 'link in bio',
            'buy now', 'limited offer', 'act now', 'get rich quick',
            'make money fast', 'crypto', 'bitcoin', 'nft'
        ]
        
        has_spam = any(spam in text for spam in spam_keywords)
        
        return has_job_keyword and not has_spam
    
    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
            print("✅ Browser closed")
