import time
import random
from playwright.sync_api import sync_playwright

class AttendanceBot:
    def __init__(self, prn="24UCS056", dob="10-08-2006", semester="odd"):
        self.prn = prn
        
        # URL Logic
        if semester == "even":
            self.url = "https://online.dkte.ac.in/newparents/index.php"
        else:
            self.url = "https://online.dkte.ac.in/newparentsodd/index.php"

        self.semester = semester
        self.browser = None
        self.page = None
        self.results = []
        self.login_error = None
        
        # Parse DOB
        try:
            parts = dob.split('-')
            self.dob_day = parts[0]
            self.dob_month = parts[1]
            self.dob_year = parts[2]
        except:
            self.dob_day = "10"
            self.dob_month = "08"
            self.dob_year = "2006"

    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    ]

    def login(self):
        """Performs login using Playwright."""
        try:
            print(f"STEP 1: Navigating to {self.url}...", flush=True)
            
            # Human-like delay before navigation
            time.sleep(random.uniform(1, 2))
            
            try:
                self.page.goto(self.url, timeout=30000, wait_until="domcontentloaded")
            except Exception as e:
                print(f"  ! Navigation error: {e}", flush=True)
            
            # Verify Access
            title = self.page.title()
            content = self.page.content()
            print(f"  > Page Loaded. Title: {title}", flush=True)
            
            if "Forbidden" in title or "403" in title or "403" in content[:500]:
                print("!!! ACCESS BLOCKED (403).", flush=True)
                print("  DEBUG: Page content preview:", flush=True)
                print(content[:1000], flush=True)
                self.login_error = "403 Forbidden - IP Blocked by DKTE"
                return False

            # STEP 2: Handle Overlays
            try:
                self.page.evaluate("""() => {
                    document.querySelectorAll('.uk-modal, .uk-modal-page, .cn-overlay, #preloader').forEach(e => e.remove());
                }""")
            except: pass

            # Human-like delay
            time.sleep(random.uniform(0.5, 1.5))

            # STEP 3: Enter PRN
            print("STEP 3: Entering PRN...", flush=True)
            try:
                self.page.wait_for_selector("#username", state="visible", timeout=15000)
                self.page.click("#username")
                time.sleep(random.uniform(0.2, 0.5))
                self.page.fill("#username", self.prn)
            except Exception as e:
                print(f"  ! PRN Field issue: {e}", flush=True)
                try:
                    self.page.evaluate(f"document.getElementById('username').value = '{self.prn}';")
                except:
                    self.login_error = "Could not find PRN field"
                    return False
            
            # STEP 4: Select DOB
            print("STEP 4: Selecting DOB...", flush=True)
            try:
                time.sleep(random.uniform(0.3, 0.7))
                self.page.select_option("#dd", self.dob_day)
                time.sleep(random.uniform(0.1, 0.3))
                self.page.select_option("#mm", self.dob_month)
                time.sleep(random.uniform(0.1, 0.3))
                self.page.select_option("#yyyy", self.dob_year)
            except Exception as e:
                print(f"  ! DOB selection issue: {e}", flush=True)

            # STEP 5: Click Login
            print("STEP 5: Clicking Login...", flush=True)
            time.sleep(random.uniform(0.5, 1))
            try:
                self.page.click(".cn-login-btn", timeout=5000)
            except:
                try:
                    self.page.evaluate("document.querySelector('.cn-login-btn').click();")
                except:
                    self.login_error = "Login button not found"
                    return False

            # STEP 6: Verify Login
            print("STEP 6: Waiting for Dashboard...", flush=True)
            try:
                self.page.wait_for_url("**/studentdashboard**", timeout=20000)
                print("  > Login Successful!", flush=True)
                return True
            except:
                # Check for error message
                content = self.page.content().lower()
                if "invalid" in content:
                    self.login_error = "Invalid Credentials"
                elif "403" in content or "forbidden" in content:
                    self.login_error = "403 Forbidden after login attempt"
                else:
                    self.login_error = "Dashboard did not load (timeout)"
                print(f"  ! Login Error: {self.login_error}", flush=True)
                return False

        except Exception as e:
            print(f"Login Error: {e}")
            self.login_error = str(e)
            return False

    def scrape_courses(self):
        print("STEP 7: Scraping Courses...")
        try:
            # Click Course Registration
            time.sleep(random.uniform(1, 2))
            try:
                self.page.click("text=Course registration", timeout=10000)
            except:
                # Try alternate navigation
                if self.semester == "even":
                    self.page.goto("https://online.dkte.ac.in/newparents/index.php?option=com_studentdashboard&controller=studentdashboard&task=dashboard&Itemid=101")
                else:
                    self.page.goto("https://online.dkte.ac.in/newparentsodd/index.php?option=com_studentdashboard&controller=studentdashboard&task=dashboard&Itemid=101")
            
            # Wait for table
            self.page.wait_for_selector(".uk-table", timeout=15000)
            time.sleep(1)
            
            # Scrape rows
            rows = self.page.query_selector_all("table.uk-table tbody tr")
            if not rows:
                rows = self.page.query_selector_all("table.uk-table tr")

            courses = []
            for row in rows:
                cols = row.query_selector_all("td")
                if len(cols) >= 3:
                    code = cols[0].inner_text().strip()
                    name = cols[1].inner_text().strip()
                    
                    if not code:
                        continue
                    
                    # Check for attendance link
                    link_el = row.query_selector("a[href*='attendencelist']")
                    if link_el:
                        url = link_el.get_attribute("href")
                        courses.append({"code": code, "name": name, "url": url})
            
            print(f"  > Found {len(courses)} courses.")
            return courses

        except Exception as e:
            print(f"Scrape Error: {e}")
            return []

    def get_attendance(self, target_date):
        self.results = []
        
        MAX_RETRIES = 2
        
        for attempt in range(MAX_RETRIES):
            print(f"\n=== ATTEMPT {attempt + 1}/{MAX_RETRIES} ===", flush=True)
            
            try:
                with sync_playwright() as p:
                    # Select random User Agent
                    selected_ua = random.choice(self.USER_AGENTS)
                    print(f"  > Using UA: {selected_ua[:50]}...", flush=True)
                    
                    # Launch browser with stealth settings
                    print("STEP 0: Launching Browser...", flush=True)
                    browser = p.chromium.launch(
                        headless=True,
                        args=[
                            "--disable-blink-features=AutomationControlled",
                            "--no-sandbox",
                            "--disable-setuid-sandbox",
                            "--disable-dev-shm-usage",
                            "--disable-accelerated-2d-canvas",
                            "--no-first-run",
                            "--no-zygote",
                            "--disable-gpu",
                        ],
                        timeout=60000
                    )
                    
                    # Create context with stealth options
                    context = browser.new_context(
                        user_agent=selected_ua,
                        viewport={'width': 1920, 'height': 1080},
                        locale="en-IN",
                        timezone_id="Asia/Kolkata",
                        extra_http_headers={
                            "Accept-Language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
                            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                            "Upgrade-Insecure-Requests": "1",
                        },
                    )
                    
                    # Anti-detection scripts
                    context.add_init_script("""
                        Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                        Object.defineProperty(navigator, 'languages', {get: () => ['en-IN', 'en-GB', 'en']});
                        Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
                        window.chrome = { runtime: {} };
                        Object.defineProperty(navigator, 'maxTouchPoints', {get: () => 0});
                    """)
                    
                    self.page = context.new_page()
                    self.page.set_default_timeout(30000)
                    
                    if self.login():
                        print("  > Login Success! Scraping courses...", flush=True)
                        courses = self.scrape_courses()
                        
                        if not courses:
                            self.results = [{"code": "INFO", "name": "No Courses Found", "status": "N/A"}]
                        else:
                            print(f"STEP 8: Checking Attendance for {target_date}...", flush=True)
                            
                            for i, course in enumerate(courses):
                                print(f"  [{i+1}/{len(courses)}] Checking {course['code']}...", flush=True)
                                status = "Not Found"
                                
                                try:
                                    # Navigate to course attendance page
                                    time.sleep(random.uniform(0.5, 1.5))
                                    
                                    # Try clicking on course tab first
                                    clicked = False
                                    try:
                                        self.page.click(f"text={course['code']}", timeout=5000)
                                        clicked = True
                                        time.sleep(0.5)
                                    except:
                                        pass
                                    
                                    # Click attendance link
                                    try:
                                        self.page.click("a[href*='attendencelist']", timeout=8000)
                                        self.page.wait_for_selector("table", timeout=10000)
                                        time.sleep(0.5)
                                        
                                        # Find matching date rows
                                        rows = self.page.query_selector_all("table tr")
                                        found_statuses = []
                                        
                                        for row in rows:
                                            row_text = row.inner_text()
                                            if target_date in row_text:
                                                text_lower = row_text.lower()
                                                inner_html = row.inner_html().lower()
                                                
                                                if "absent" in text_lower or "uk-label-danger" in inner_html:
                                                    found_statuses.append("Absent")
                                                elif "present" in text_lower or "uk-label-success" in inner_html:
                                                    found_statuses.append("Present")
                                        
                                        if found_statuses:
                                            status = ", ".join(found_statuses)
                                    except Exception as e:
                                        print(f"    ! Error checking attendance: {e}", flush=True)
                                        status = "Error"
                                        
                                except Exception as e:
                                    print(f"    ! Navigation error: {e}", flush=True)
                                    status = "Nav Error"
                                
                                self.results.append({
                                    "code": course['code'],
                                    "name": course['name'],
                                    "status": status,
                                    "date": target_date
                                })
                                print(f"    > Status: {status}", flush=True)
                        
                        browser.close()
                        break  # Success, exit retry loop
                    
                    else:
                        print(f"  ! Login Failed: {self.login_error}", flush=True)
                        browser.close()
                        
                        # If 403, no point retrying
                        if "403" in str(self.login_error):
                            self.results = [{
                                "code": "ERROR",
                                "name": "403 Forbidden",
                                "status": "DKTE website blocked this server's IP. Try again later or use a different deployment region.",
                                "date": target_date
                            }]
                            break
                        
            except Exception as e:
                print(f"  ! Critical Error: {e}", flush=True)
        
        if not self.results:
            self.results = [{
                "code": "ERROR",
                "name": "All Attempts Failed",
                "status": self.login_error or "Unknown error",
                "date": target_date
            }]
        
        return self.results
