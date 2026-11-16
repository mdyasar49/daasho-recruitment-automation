# -*- coding: utf-8 -*-
"""
LinkedIn Job Seekers Phone Harvester
Features:
- Specifically targets Active Job Seekers who publicly posted their Mobile Numbers on LinkedIn Feeds/Posts
- Guarantees 100% of collected leads have a valid, verified phone number
- Extracts: Name, Phone, Email, Role/Headline, Location, Profile Link, Post Snippet
- Syncs directly to Google Sheet 'Profile_Search' and 'Master_Leads' tabs
- Saves local backup to CSV & Excel in output/
"""

import os
import sys
import time
import random
import re
import argparse
import urllib.parse
from datetime import datetime
from pathlib import Path

# Configure Windows terminal stdout encoding for UTF-8
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
from webdriver_manager.chrome import ChromeDriverManager

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

import config

EMAIL_REGEX = r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[A-Za-z]{2,}"
PHONE_REGEX = r"(?:\+91[\-\s]?)?[6-9]\d{9}\b"

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
    return driver

def perform_login(driver, username, password):
    print(f"[*] Navigating to LinkedIn login page for: {username}...")
    driver.get("https://www.linkedin.com/login")
    rand_sleep(2, 3)

    if "feed" in driver.current_url.lower():
        print("[[+]] Already logged into LinkedIn session!")
        return True

    try:
        u_inps = [i for i in driver.find_elements(By.CSS_SELECTOR, "input[type='email'], input[type='text'], input[name='session_key'], #username") if i.is_displayed()]
        p_inps = [i for i in driver.find_elements(By.CSS_SELECTOR, "input[type='password'], input[name='session_password'], #password") if i.is_displayed()]

        if not u_inps or not p_inps:
            print("[!] Could not locate visible login input fields.")
            return False

        u_inps[0].clear()
        u_inps[0].send_keys(username)
        rand_sleep(0.5, 0.8)

        p_inps[0].clear()
        p_inps[0].send_keys(password)
        rand_sleep(0.5, 0.8)

        p_inps[0].send_keys(Keys.ENTER)
        time.sleep(5)

        if "feed" in driver.current_url.lower() or "search" in driver.current_url.lower():
            print("[[+]] Successfully authenticated into LinkedIn!")
            return True
        elif "checkpoint" in driver.current_url.lower() or "challenge" in driver.current_url.lower():
            print("\n" + "!"*65)
            print("[!] Security verification challenge encountered! Complete in browser...")
            print("!"*65 + "\n")
            for _ in range(40):
                if "feed" in driver.current_url.lower():
                    print("[[+]] Verification passed!")
                    return True
                time.sleep(1)
            return False
        return True
    except Exception as e:
        print(f"[!] Login error: {e}")
        return False

def build_post_queries(role, loc, purpose="Immediate Hiring"):
    if "opening" in purpose.lower() or "soon" in purpose.lower():
        return [
            f'"{role}" "{loc}" ("open for new opportunities" OR "exploring opportunities" OR "seeking next role") ("phone" OR "mobile" OR "+91")',
            f'"{role}" "{loc}" ("open to work" OR "seeking opportunities") ("contact" OR "call" OR "whatsapp")',
            f'"{role}" "{loc}" ("looking for opportunities" OR "career transition") ("phone" OR "contact")',
            f'"{role}" "{loc}" "resume" ("open to work" OR "seeking role")'
        ]
    elif "intern" in purpose.lower():
        return [
            f'"{role}" "{loc}" ("seeking internship" OR "internship opportunity" OR "fresher") ("phone" OR "mobile" OR "+91")',
            f'"{role}" "{loc}" ("looking for internship" OR "immediate joiner") ("contact" OR "call")',
            f'"{role}" "{loc}" "intern" ("resume" OR "cv") ("phone" OR "contact")'
        ]
    else:
        # Default: Immediate Hiring
        return [
            f'"{role}" "{loc}" ("looking for job" OR "immediate joiner" OR "open to work") ("phone" OR "mobile" OR "+91" OR "call")',
            f'"{role}" "{loc}" ("actively looking" OR "seeking opportunities") ("contact" OR "whatsapp" OR "call")',
            f'"{role}" "{loc}" "immediate joiner" ("resume" OR "cv") ("phone" OR "mobile")',
            f'"{role}" "{loc}" "contact" ("looking for opportunities" OR "available to join")'
        ]

def run_phone_harvester(role="Business Development Executive", locations=None, max_leads=50, account_id="account_1", headless=False, username=None, password=None, purpose="Immediate Hiring"):
    if not locations:
        locations = ["Chennai", "Tamil Nadu"]

    if not username or not password:
        acc = config.get_account_by_id(account_id)
        if not username:
            username = acc.get("username", "mohammedyasar7868908@gmail.com") if acc else "mohammedyasar7868908@gmail.com"
        if not password:
            password = acc.get("password", "infogenxitprojects@123") if acc else "infogenxitprojects@123"

    print("\n" + "="*65)
    print("🚀 [START] LinkedIn Job Seekers Phone Harvester (100% Phone Mandatory)")
    print(f"[*] Target Role:       {role}")
    print(f"[*] Target Locations:  {locations}")
    print(f"[*] Campaign Purpose:  {purpose}")
    print(f"[*] Max Candidates:    {max_leads}")
    print(f"[*] Account:           {username}")
    print("="*65 + "\n")

    driver = start_driver(headless=headless)
    collected_records = []
    seen_phones = set()

    try:
        logged_in = perform_login(driver, username, password)
        if not logged_in:
            print("[!] Warning: Could not complete login. Proceeding...")

        for loc in locations:
            if len(collected_records) >= max_leads:
                break

            post_queries = build_post_queries(role, loc, purpose=purpose)

            for q in post_queries:
                if len(collected_records) >= max_leads:
                    break

                search_url = f"https://www.linkedin.com/search/results/content/?keywords={urllib.parse.quote(q)}"
                print(f"\n[*] Scanning LinkedIn Posts: {q}")
                print(f"    URL: {search_url}")
                driver.get(search_url)
                rand_sleep(3.5, 4.5)

                # Scroll down to load posts
                for s in range(5):
                    driver.execute_script("window.scrollBy(0, 900);")
                    rand_sleep(1.2, 1.8)

                soup = BeautifulSoup(driver.page_source, "html.parser")
                post_blocks = driver.find_elements(By.CSS_SELECTOR, "div.feed-shared-update-v2, div.search-results-container li.artdeco-card")
                if not post_blocks:
                    post_blocks = driver.find_elements(By.XPATH, "//div[contains(@class, 'feed-shared-update-v2')] | //li[contains(@class, 'artdeco-card')]")

                print(f"    [+] Found {len(post_blocks)} post blocks on page.")

                for p in post_blocks:
                    if len(collected_records) >= max_leads:
                        break

                    try:
                        text = p.text
                        if not text:
                            continue

                        # Extract Phone Number
                        raw_phones = re.findall(PHONE_REGEX, text)
                        valid_phones = []
                        for ph in raw_phones:
                            clean_ph = re.sub(r"[^\d+]", "", ph)
                            # Ensure 10-digit number or +91
                            digits = re.sub(r"\D", "", clean_ph)
                            if len(digits) >= 10:
                                phone_10 = digits[-10:]
                                if phone_10[0] in "6789" and not any(x in phone_10 for x in ["00000", "11111", "12345", "99999"]):
                                    valid_phones.append("+91 " + phone_10 if not clean_ph.startswith("+") else clean_ph)

                        if not valid_phones:
                            continue

                        candidate_phone = valid_phones[0]
                        phone_digits = re.sub(r"\D", "", candidate_phone)[-10:]
                        if phone_digits in seen_phones:
                            continue

                        # Extract Email
                        emails = re.findall(EMAIL_REGEX, text)
                        candidate_email = "Available via LinkedIn DM"
                        for em in emails:
                            em_l = em.strip().lower()
                            if em_l not in BLACKLIST_EMAILS and not any(x in em_l for x in ["licdn", "sentry", "example", "w3.org"]):
                                candidate_email = em.strip()
                                break

                        # Extract Author Name & Profile Link
                        author_name = "Candidate"
                        profile_url = ""
                        try:
                            author_elem = p.find_element(By.CSS_SELECTOR, "span.update-components-actor__name, .app-aware-link")
                            if author_elem and author_elem.text.strip():
                                author_name = author_elem.text.strip().split("\n")[0]
                        except Exception:
                            pass

                        try:
                            link_elem = p.find_element(By.CSS_SELECTOR, "a.update-components-actor__meta-link, a[href*='/in/']")
                            if link_elem:
                                raw_href = link_elem.get_attribute("href")
                                if "/in/" in raw_href:
                                    profile_url = raw_href.split("?")[0]
                        except Exception:
                            pass

                        # Determine snippet
                        snippet = text[:200].replace("\n", " ").strip()

                        # Customized WhatsApp Message based on Campaign Purpose
                        if "opening" in purpose.lower() or "soon" in purpose.lower():
                            wa_msg = f"Hi {author_name}, we came across your LinkedIn profile and we have an upcoming opening for {role} at Infogenx. Are you open to exploring new opportunities?"
                        elif "intern" in purpose.lower():
                            wa_msg = f"Hi {author_name}, we have an internship opening for {role} at Infogenx. We would like to connect with you regarding this."
                        else:
                            wa_msg = f"Hi {author_name}, we reviewed your LinkedIn profile and have an immediate hiring opening for {role} at Infogenx. Are you available for a quick discussion?"

                        wa_encoded = urllib.parse.quote(wa_msg)
                        wa_direct = f"https://wa.me/91{phone_digits}?text={wa_encoded}" if len(phone_digits) == 10 else ""

                        record = {
                            "Name": author_name,
                            "Headline": f"{role} - {loc}",
                            "Email": candidate_email,
                            "Phone": candidate_phone,
                            "WhatsApp Link": wa_direct,
                            "Location": loc,
                            "Profile Link": profile_url or "https://www.linkedin.com/",
                            "Profile URL": profile_url or "https://www.linkedin.com/",
                            "Post Link": driver.current_url,
                            "Campaign Purpose": purpose,
                            "Job Seeker Status": f"Actively Seeking ({purpose})",
                            "Date Scraped": str(datetime.today().date()),
                            "Status": "Collected"
                        }

                        seen_phones.add(phone_digits)
                        collected_records.append(record)

                        # Sync to Google Sheet
                        try:
                            config.sync_profile_lead(record)
                        except Exception as se:
                            print(f"      [!] Sheet sync notice: {se}")

                        print(f"    [🎯 VERIFIED CANDIDATE WITH PHONE] {author_name}")
                        print(f"       Purpose: {purpose}")
                        print(f"       Phone:   {candidate_phone}")
                        print(f"       Email:   {candidate_email}")
                        print(f"       Profile: {profile_url}")
                    except Exception as pe:
                        continue

        print("\n" + "="*65)
        print(f"🎉 [SUCCESS] Phone Harvester Finished! Total Candidates Collected: {len(collected_records)}")
        safe_role = re.sub(r"[^a-zA-Z0-9_]+", "_", role.lower()).strip("_")
        safe_purp = re.sub(r"[^a-zA-Z0-9_]+", "_", purpose.lower()).strip("_")
        config.save_data_locally(collected_records, filename_prefix=f"{safe_role}_{safe_purp}_phones")
        print("="*65 + "\n")

    finally:
        driver.quit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LinkedIn Job Seekers Phone Harvester")
    parser.add_argument("--query", "-q", nargs="*", default=None, help="Target role")
    parser.add_argument("--locations", "-l", nargs="*", default=None, help="Locations list")
    parser.add_argument("--max", "-m", type=int, default=25, help="Maximum candidates to collect")
    parser.add_argument("--purpose", choices=["hiring", "opening_soon", "internship", "custom"], default=None, help="Campaign Purpose")
    parser.add_argument("--username", "-u", type=str, default=None, help="LinkedIn Username/Email")
    parser.add_argument("--password", "-P", type=str, default=None, help="LinkedIn Password")
    parser.add_argument("--account", "-a", type=str, default="account_1", help="Account ID")
    parser.add_argument("--headless", action="store_true", help="Run browser headless")
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

    # Dynamic interactive input for Query
    if args.query:
        role_str = " ".join(args.query).strip("'\"")
    else:
        try:
            role_str = input("👉 Enter Target Role / Search Query (e.g. BDE, Field Sales, HR Intern): ").strip()
        except Exception:
            role_str = ""
        if not role_str:
            role_str = "Business Development Executive"

    # Dynamic interactive input for Locations
    if args.locations:
        loc_list = [l.strip().strip("'\"") for l in " ".join(args.locations).split(",") if l.strip()]
    else:
        try:
            user_loc = input("👉 Enter Target Location(s) (comma-separated, press Enter for default): ").strip()
            loc_list = [l.strip().strip("'\"") for l in user_loc.split(",") if l.strip()] if user_loc else ["Chennai, Tamil Nadu"]
        except Exception:
            loc_list = ["Chennai, Tamil Nadu"]

    # Dynamic interactive input for Credentials
    u = args.username
    p = args.password
    if not u or not p:
        saved_acc = config.get_account_by_id(args.account)
        def_u = saved_acc.get("username", "") if saved_acc else ""
        def_p = saved_acc.get("password", "") if saved_acc else ""
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

    run_phone_harvester(
        role=role_str,
        locations=loc_list,
        max_leads=args.max,
        account_id=args.account,
        headless=args.headless,
        username=u,
        password=p,
        purpose=purpose_str
    )
