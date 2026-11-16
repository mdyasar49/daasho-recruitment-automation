# -*- coding: utf-8 -*-
"""
LinkedIn Profile Search & Contact Details Scraper
Features:
- Automated Selenium login with multi-account support (Default: Infogenx)
- Searches HR Intern profiles in Tamil Nadu, Kerala & Pondicherry
- Extracts: Name, Headline, Email, Phone, Profile Link, Location/Query
- Syncs to Google Sheet 'Profile_Search' and 'Master_Leads' tabs
- Saves backup locally to Excel & CSV
- Strictly scrapes DATA ONLY (Does NOT send any emails)
"""

import os
import sys
import time
import random
import re
import argparse
import urllib.parse
from datetime import datetime

# Configure Windows terminal stdout encoding for UTF-8 and emojis
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from config import (
    LINKEDIN_USERNAME,
    LINKEDIN_PASSWORD,
    DEFAULT_QUERY,
    MAX_PROFILES,
    MAX_PAGES,
    SHEET_TABS,
    get_worksheet,
    sync_profile_lead,
    save_data_locally,
    get_account_by_id,
    load_accounts
)

# Regex Patterns
EMAIL_REGEX = r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[A-Za-z]{2,}"
PHONE_PATTERNS = [
    r"\+91[-\s]?\d{10}",
    r"\b[6-9]\d{9}\b",
    r"\+\d{1,3}[-\s]?\d{6,12}",
    r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"
]

BLACKLIST_EMAILS = {
    "jobkart.hr@outlook.com",
    "mohammedyasar7868908@gmail.com",
    "mohamedyasar081786@gmail.com",
    "infogenxitprojects@gmail.com",
    "srihariharan213@gmail.com"
}

def rand_sleep(min_sec=1.5, max_sec=3.0):
    time.sleep(random.uniform(min_sec, max_sec))

def start_driver(headless=False):
    opts = Options()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--start-maximized")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)
    wait = WebDriverWait(driver, 15)
    return driver, wait

def safe_find_click(driver, xpaths):
    for xp in xpaths:
        try:
            el = driver.find_element(By.XPATH, xp)
            driver.execute_script("arguments[0].click();", el)
            return True
        except Exception:
            continue
    return False

def extract_from_modal_html(html):
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(" ", strip=True)

    email = ""
    for em in re.findall(EMAIL_REGEX, text):
        em_clean = em.strip().lower()
        if em_clean not in BLACKLIST_EMAILS and not any(x in em_clean for x in ["licdn.com", "sentry.io", "w3.org", "example.com"]):
            email = em.strip()
            break

    phone = ""
    for p in PHONE_PATTERNS:
        m = re.search(p, text)
        if m:
            candidate_phone = m.group(0).strip()
            if not any(x in candidate_phone for x in ["00000", "11111", "12345"]):
                phone = candidate_phone
                break

    return email, phone

def perform_login(driver, username, password):
    print(f"[*] Navigating to LinkedIn login page for: {username}...")
    driver.get("https://www.linkedin.com/login")
    time.sleep(2)

    # Check if already logged in
    if "feed" in driver.current_url.lower():
        print("[[+]] Already logged in to LinkedIn session!")
        return True

    try:
        u_inps = [i for i in driver.find_elements(By.CSS_SELECTOR, "input[type='email'], input[type='text'], input[name='session_key'], #username") if i.is_displayed()]
        p_inps = [i for i in driver.find_elements(By.CSS_SELECTOR, "input[type='password'], input[name='session_password'], #password") if i.is_displayed()]

        if not u_inps or not p_inps:
            print("[!] Could not locate visible login input fields.")
            return False

        u_inps[0].clear()
        u_inps[0].send_keys(username)
        time.sleep(0.5)

        p_inps[0].clear()
        p_inps[0].send_keys(password)
        time.sleep(0.5)

        p_inps[0].send_keys(Keys.ENTER)
        time.sleep(5)

        print(f"[*] Current URL after login attempt: {driver.current_url}")

        if "feed" in driver.current_url.lower() or "search" in driver.current_url.lower():
            print("[[+]] Successfully authenticated into LinkedIn!")
            return True
        elif "checkpoint" in driver.current_url.lower() or "challenge" in driver.current_url.lower():
            print("\n" + "!"*65)
            print("[!] Security verification challenge encountered!")
            print("[!] Please complete verification in browser if visible.")
            print("!"*65 + "\n")
            for _ in range(30):
                if "feed" in driver.current_url.lower():
                    print("[[+]] Verification passed!")
                    return True
                time.sleep(1)
            return False
        return True
    except Exception as e:
        print(f"[!] Login error: {e}")
        return False

def run_scraper(query=None, locations=None, max_profiles=25, max_pages=3, username=None, password=None, headless=False, job_seekers_only=True, require_phone=True, purpose="Immediate Hiring"):
    # Default target role if not provided
    if not query:
        query = "Business Development Executive"

    if locations is None:
        locations = ["Chennai, Tamil Nadu"]

    ws_profile = get_worksheet(SHEET_TABS["PROFILE"])
    existing_urls = set()
    if ws_profile:
        try:
            col_vals = ws_profile.col_values(6)  # Profile Link column (col 6)
            existing_urls = set(col_vals[1:])
            print(f"[[+]] Connected to Google Sheet Tab: '{SHEET_TABS['PROFILE']}' ({len(existing_urls)} existing records)")
        except Exception as e:
            print(f"[!] Note on reading existing Google Sheet: {e}")
    else:
        print(f"[*] Note: Google Sheet tab '{SHEET_TABS['PROFILE']}' pending. Local CSV/Excel will be saved.")

    scraped_records = []

    print("\n" + "="*65)
    print("[START] Starting LinkedIn Profile Scraper (Data Collection Only)")
    print(f"[*] Target Role:       {query}")
    print(f"[*] Target Locations:  {locations}")
    print(f"[*] Campaign Purpose:  {purpose}")
    print(f"[*] Max Profiles:      {max_profiles}")
    print(f"[*] Job Seekers Only:  {job_seekers_only}")
    print(f"[*] Phone Mandatory:   {require_phone}")
    print(f"[*] Output Sheet:      {SHEET_TABS['PROFILE']} & {SHEET_TABS['MASTER']}")
    print("="*65 + "\n")

    driver, wait = start_driver(headless=headless)

    try:
        # Step 1: Login
        logged_in = perform_login(driver, username, password)
        if not logged_in:
            print("[!] Warning: Proceeding with search attempt...")

        # Step 2: Loop across requested locations
        for loc in locations:
            if len(scraped_records) >= max_profiles:
                break

            if job_seekers_only:
                current_query = f'"{query}" ("open to work" OR "actively looking" OR "seeking" OR "immediate joiner") "{loc}"'
            else:
                current_query = f"{query} {loc}"

            print(f"\n[LOC] Searching Location: '{loc}' (Job Seekers Filter: {job_seekers_only})")
            print(f"[*] Query: {current_query}")

            for page_num in range(1, max_pages + 1):
                if len(scraped_records) >= max_profiles:
                    break

                search_url = f"https://www.linkedin.com/search/results/people/?keywords={urllib.parse.quote(current_query)}&page={page_num}"
                print(f"  [PAGE] Scanning Page {page_num}: {search_url}")
                driver.get(search_url)
                rand_sleep(3, 4)

                # Scroll to render all result cards
                for _ in range(3):
                    driver.execute_script("window.scrollBy(0, 800);")
                    rand_sleep(1, 1.5)

                soup = BeautifulSoup(driver.page_source, "html.parser")
                raw_page_urls = []

                for a in soup.find_all("a", href=True):
                    href = a['href'].split("?")[0].strip()
                    if href.startswith("/"):
                        href = "https://www.linkedin.com" + href
                    if "/in/" in href and not "miniProfileUrn" in href and "/opportunities/" not in href:
                        # Clean to base profile link: https://www.linkedin.com/in/username/
                        m = re.match(r"(https://www\.linkedin\.com/in/[^/]+)/?", href)
                        if m:
                            clean_href = m.group(1) + "/"
                            if clean_href not in raw_page_urls:
                                raw_page_urls.append(clean_href)

                if not raw_page_urls:
                    print(f"  [-] No profiles found on page {page_num}.")
                    break

                page_profile_urls = [u for u in raw_page_urls if u not in existing_urls]
                print(f"  [+] Found {len(raw_page_urls)} profiles on page {page_num} ({len(page_profile_urls)} new).")

                if not page_profile_urls:
                    print(f"  [*] All {len(raw_page_urls)} profiles on page {page_num} already collected. Checking next page...")
                    continue

                # Visit each profile to extract detailed info
                for idx, p_url in enumerate(page_profile_urls, start=1):
                    if len(scraped_records) >= max_profiles:
                        print(f"\n[[+]] Target limit of {max_profiles} profiles reached!")
                        break

                    try:
                        print(f"  [{len(scraped_records) + 1}/{max_profiles}] Visiting: {p_url}")
                        driver.get(p_url)
                        rand_sleep(2.5, 3.5)

                        # Extract Name from Title tag, H1, or URL slug
                        name = "N/A"
                        try:
                            page_title = driver.title
                            if "|" in page_title:
                                candidate_part = page_title.split("|")[0].strip()
                                if " - " in candidate_part:
                                    name = candidate_part.split(" - ")[0].strip()
                                else:
                                    name = candidate_part
                        except Exception:
                            pass

                        if not name or name == "LinkedIn Member" or name == "N/A":
                            try:
                                h1_elem = driver.find_element(By.TAG_NAME, "h1")
                                h1_text = h1_elem.text.strip()
                                if h1_text and h1_text != "LinkedIn Member":
                                    name = h1_text
                            except Exception:
                                pass

                        if not name or name == "LinkedIn Member" or name == "N/A":
                            slug = p_url.rstrip("/").split("/in/")[-1].split("?")[0]
                            cleaned = re.sub(r"-[a-zA-Z0-9]+$", "", slug).replace("-", " ").title()
                            name = cleaned if cleaned else slug.title()

                        # Extract Headline
                        p_soup = BeautifulSoup(driver.page_source, "html.parser")
                        headline = ""
                        hl_elem = p_soup.find("div", {"class": re.compile(r"text-body-medium")})
                        if hl_elem:
                            headline = hl_elem.text.strip()
                        if not headline:
                            headline = f"{query} - {loc}"

                        # --- VERIFY ACTIVE JOB SEEKER ---
                        is_job_seeker = False
                        job_seeker_tag = ""

                        # 1. Check for LinkedIn OpenToWork Badge / Photo Frame
                        try:
                            badge_elems = driver.find_elements(
                                By.XPATH,
                                "//img[contains(@alt, 'Open to work') or contains(@class, 'pv-open-to-work')] | "
                                "//div[contains(@class, 'open-to-work') or contains(@class, 'pv-open-to-work-badge')] | "
                                "//main//section[contains(., 'Open to work') or contains(., 'open to work')]"
                            )
                            if badge_elems:
                                is_job_seeker = True
                                job_seeker_tag = "OpenToWork Badge"
                        except Exception:
                            pass

                        # 2. Check Headline & About section for Job Seeker Keywords
                        JOB_SEEKER_KEYWORDS = [
                            "open to work", "#opentowork", "opentowork",
                            "actively looking", "actively seeking", "seeking opportunities",
                            "seeking new", "seeking role", "seeking entry", "seeking hr",
                            "seeking bde", "seeking internship", "immediate joiner",
                            "immediately available", "available to join", "looking for job",
                            "looking for opportunit", "job seeker", "in search of new opportunit",
                            "open for opportunit", "aspiring hr", "fresher looking"
                        ]
                        EXCLUDE_RECRUITERS = [
                            "we are hiring", "i am hiring", "we're hiring", "hiring for",
                            "talent acquisition", "hr recruiter", "recruitment consultant",
                            "senior hr manager", "head of hr", "lead recruiter"
                        ]

                        headline_lower = headline.lower()
                        is_recruiter = any(ex in headline_lower for ex in EXCLUDE_RECRUITERS)

                        if not is_job_seeker:
                            for kw in JOB_SEEKER_KEYWORDS:
                                if kw in headline_lower:
                                    is_job_seeker = True
                                    job_seeker_tag = f"Headline: '{kw}'"
                                    break

                        # Check About section if still not confirmed
                        if not is_job_seeker:
                            try:
                                about_elems = driver.find_elements(By.XPATH, "//section[contains(@id, 'about')] | //div[contains(., 'About') and contains(@class, 'display-flex')]")
                                if about_elems:
                                    about_txt = about_elems[0].text.lower()
                                    for kw in JOB_SEEKER_KEYWORDS:
                                        if kw in about_txt:
                                            is_job_seeker = True
                                            job_seeker_tag = f"About: '{kw}'"
                                            break
                            except Exception:
                                pass

                        if is_recruiter and not any(ok in headline_lower for ok in ["open to work", "seeking", "immediate joiner"]):
                            is_job_seeker = False

                        if job_seekers_only and not is_job_seeker:
                            print(f"    [-] Skipping: {name} (Not an active job seeker / No #OpenToWork or seeking status)")
                            continue
                        else:
                            if is_job_seeker:
                                print(f"    [★] Verified Job Seeker: {name} ({job_seeker_tag})")

                        # Extract Contact Info Modal
                        contact_xpaths = [
                            "//a[contains(@href,'contact-info')]",
                            "//button[contains(@aria-label,'Contact info')]",
                            "//a[contains(@id,'contact-info')]"
                        ]
                        clicked = safe_find_click(driver, contact_xpaths)

                        email, phone = "", ""
                        if clicked:
                            rand_sleep(1.5, 2.0)
                            try:
                                modal = driver.find_element(By.CSS_SELECTOR, "div[role='dialog']")
                                modal_html = modal.get_attribute("outerHTML")
                            except Exception:
                                modal_html = driver.page_source
                            email, phone = extract_from_modal_html(modal_html)

                        # Fallback: check main profile section text (avoiding navbar/header/chat)
                        if not email or not phone:
                            try:
                                main_elem = driver.find_element(By.TAG_NAME, "main")
                                page_em, page_ph = extract_from_modal_html(main_elem.get_attribute("outerHTML"))
                                if not email and page_em:
                                    email = page_em
                                if not phone and page_ph:
                                    phone = page_ph
                            except Exception:
                                pass

                        # Fallback 2: Check candidate's Headline for phone
                        if not phone:
                            for pat in PHONE_PATTERNS:
                                m = re.search(pat, headline)
                                if m and not any(x in m.group(0) for x in ["00000", "11111", "12345"]):
                                    phone = m.group(0).strip()
                                    break

                        # Fallback 3: Check candidate's About section (click 'see more')
                        if not phone:
                            try:
                                about_btn = driver.find_elements(By.XPATH, "//section[contains(@id, 'about')]//button[contains(., 'more') or contains(., 'More')]")
                                if about_btn:
                                    driver.execute_script("arguments[0].click();", about_btn[0])
                                    rand_sleep(0.5, 0.8)
                                about_sec = driver.find_elements(By.XPATH, "//section[contains(@id, 'about')]")
                                if about_sec:
                                    for pat in PHONE_PATTERNS:
                                        m = re.search(pat, about_sec[0].text)
                                        if m and not any(x in m.group(0) for x in ["00000", "11111", "12345"]):
                                            phone = m.group(0).strip()
                                            break
                            except Exception:
                                pass

                        # Determine post link (candidate's recent activity / posts link)
                        post_link = f"{p_url.rstrip('/')}/recent-activity/all/"

                        # Fallback 4: Check candidate's recent activity / posts
                        if not phone:
                            try:
                                driver.get(post_link)
                                rand_sleep(1.8, 2.5)
                                act_text = driver.find_element(By.TAG_NAME, "main").text
                                for pat in PHONE_PATTERNS:
                                    m = re.search(pat, act_text)
                                    if m and not any(x in m.group(0) for x in ["00000", "11111", "12345"]):
                                        phone = m.group(0).strip()
                                        break
                            except Exception:
                                pass

                        # Validate Phone Number
                        is_valid_phone = bool(phone and phone != "Available via LinkedIn DM" and re.search(r"[6-9]\d{9}", phone))
                        if require_phone and not is_valid_phone:
                            print(f"    [-] Skipping: {name} (Missing mandatory Phone number)")
                            continue

                        clean_email = email.strip() if email and email != "N/A" else "Available via LinkedIn DM"
                        clean_phone = phone.strip() if is_valid_phone else "Available via LinkedIn DM"

                        record = {
                            "Name": name,
                            "Headline": headline or f"{query} - {loc}",
                            "Email": clean_email,
                            "Phone": clean_phone,
                            "Location": loc,
                            "Profile Link": p_url,
                            "Profile URL": p_url,
                            "Post Link": post_link,
                            "Campaign Purpose": purpose,
                            "Job Seeker Status": job_seeker_tag or "Active Candidate",
                            "Date Scraped": str(datetime.today().date()),
                            "Status": "Collected"
                        }

                        # Collect the verified job seeker lead
                        scraped_records.append(record)
                        existing_urls.add(p_url)

                        # Sync directly to Google Sheet
                        try:
                            sync_profile_lead(record)
                        except Exception as se:
                            print(f"    [!] Google Sheet sync note: {se}")

                        contact_disp = f"Phone: {clean_phone} | Email: {clean_email}"
                        print(f"    [+] Collected: {name} | Loc: {loc} | {contact_disp}")
                    except Exception as pe:
                        print(f"    [!] Notice on profile {p_url}: {pe}")
                    rand_sleep(1, 2)

        safe_prefix = re.sub(r"[^a-zA-Z0-9_]+", "_", query.lower()).strip("_")
        print("\n" + "="*65)
        print(f"[SUCCESS] Scraping Finished! Total {query} Profiles Collected: {len(scraped_records)}")
        save_data_locally(scraped_records, filename_prefix=f"{safe_prefix}_profiles")
        print("="*65 + "\n")

    finally:
        driver.quit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LinkedIn Profile Contact Info Scraper")
    parser.add_argument("--query", "-q", nargs="*", default=None, help="Search keyword")
    parser.add_argument("--locations", "-l", nargs="*", default=None, help="Locations list")
    parser.add_argument("--max", "-m", type=int, default=25, help="Maximum profiles to scrape")
    parser.add_argument("--pages", "-p", type=int, default=3, help="Maximum search pages")
    parser.add_argument("--account", "-a", type=str, default="account_1", help="Account ID (default: account_1 Mohammed Yasar)")
    parser.add_argument("--username", "-u", type=str, default=None, help="LinkedIn Username/Email")
    parser.add_argument("--password", "-P", type=str, default=None, help="LinkedIn Password")
    parser.add_argument("--purpose", choices=["hiring", "opening_soon", "internship", "custom"], default=None, help="Campaign Purpose")
    parser.add_argument("--headless", action="store_true", help="Run browser in background headless mode")
    parser.add_argument("--job-seekers-only", dest="job_seekers_only", action="store_true", default=True, help="Only collect active job seekers (Open to Work / Seeking)")
    parser.add_argument("--all-profiles", dest="job_seekers_only", action="store_false", help="Scrape all profiles without job seeker filter")
    parser.add_argument("--require-phone", dest="require_phone", action="store_true", default=True, help="Strictly require a valid phone number (default: True)")
    parser.add_argument("--allow-missing-phone", dest="require_phone", action="store_false", help="Allow leads with missing phone numbers")
    args = parser.parse_args()

    # Dynamic interactive input for Campaign Purpose
    if args.purpose:
        if args.purpose == "hiring":
            purpose_str = "Immediate Hiring"
        elif args.purpose == "opening_soon":
            purpose_str = "Opening Soon"
        elif args.purpose == "internship":
            purpose_str = "Internship"
        else:
            purpose_str = "Custom"
    else:
        print("\n🎯 Select Campaign Purpose:")
        print("  [1] Immediate Hiring (Active Job Openings / Immediate Joiners)")
        print("  [2] Opening Soon (Building talent pool for upcoming roles)")
        print("  [3] Internship / Freshers Hiring")
        print("  [4] Custom Purpose")
        try:
            p_ch = input("👉 Enter Choice [1-4] (default: 1): ").strip()
        except Exception:
            p_ch = "1"
        if p_ch == "2":
            purpose_str = "Opening Soon"
        elif p_ch == "3":
            purpose_str = "Internship"
        elif p_ch == "4":
            try:
                purpose_str = input("👉 Enter Custom Purpose (e.g. Freelance, Urgent Hiring): ").strip() or "Hiring"
            except Exception:
                purpose_str = "Hiring"
        else:
            purpose_str = "Immediate Hiring"

    if args.query:
        query_str = " ".join(args.query).strip("'\"")
    else:
        try:
            query_str = input("👉 Enter Target Role / Search Query: ").strip()
        except Exception:
            query_str = ""
        if not query_str:
            query_str = "Business Development Executive"

    def normalize_locations(loc_args):
        if not loc_args:
            try:
                user_loc = input("👉 Enter Target Location(s) (comma-separated, press Enter for default): ").strip()
                if user_loc:
                    return [l.strip().strip("'\"") for l in user_loc.split(",") if l.strip()]
            except Exception:
                pass
            return ["Chennai, Tamil Nadu"]
        joined = " ".join(loc_args)
        if "," in joined:
            return [l.strip().strip("'\"") for l in joined.split(",") if l.strip()]
        return [joined.strip("'\"")]

    locs = normalize_locations(args.locations)

    acc = get_account_by_id(args.account)
    def_u = acc.get("username", "") if acc else ""
    def_p = acc.get("password", "") if acc else ""

    u = args.username
    p = args.password
    if not u:
        try:
            user_in = input(f"👉 Enter LinkedIn Email/Username (Press Enter for '{def_u}'): ").strip()
            u = user_in if user_in else def_u
        except Exception:
            u = def_u
    if not p:
        try:
            pass_in = input("👉 Enter LinkedIn Password (Press Enter for saved default): ").strip()
            p = pass_in if pass_in else def_p
        except Exception:
            p = def_p

    print(f"[*] Active LinkedIn Account: {u}")

    # Auto-adjust pages if max requested profiles is high
    target_pages = args.pages
    if args.pages == 3 and args.max > 25:
        target_pages = min(50, (args.max // 10) + 2)

    run_scraper(
        query=query_str,
        locations=locs,
        max_profiles=args.max,
        max_pages=target_pages,
        username=u,
        password=p,
        headless=args.headless,
        job_seekers_only=args.job_seekers_only,
        require_phone=args.require_phone,
        purpose=purpose_str
    )
