# -*- coding: utf-8 -*-
"""
Central configuration, multi-account manager, and Google Sheet sync helpers for LinkedIn Lead Automation Suite.
Google Sheet: https://docs.google.com/spreadsheets/d/1Xb8Z2M6rBANcqNgvE37XIapEINqLD3Gaf0wOqdfdmTs/edit
Google Apps Script: https://script.google.com/d/1G2_d05xDJFTIkOhZoIdAkxSkcf7mpBXNi53CXLBX1n_8HVMGM6DVXblT/edit
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Base directory
BASE_DIR = Path(__file__).resolve().parent

# Load .env file
load_dotenv(BASE_DIR / ".env")

# --- MULTI-ACCOUNT MANAGEMENT ---
ACCOUNTS_FILE = BASE_DIR / "accounts.json"

def load_accounts():
    """
    Loads all configured LinkedIn accounts.
    Includes Srihariharan and Infogenx (from master_credentials) by default.
    """
    accounts = []
    if ACCOUNTS_FILE.exists():
        try:
            with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
                accounts = json.load(f)
        except Exception:
            pass

    if not accounts:
        # Default accounts: Account 1 (Srihariharan) + Account 2 (Infogenx)
        accounts = [
            {
                "id": "account_1",
                "name": "Srihariharan",
                "username": os.getenv("LINKEDIN_USERNAME", "srihariharan213@gmail.com"),
                "password": os.getenv("LINKEDIN_PASSWORD", "Hariharan@213"),
                "cookie": os.getenv("LINKEDIN_COOKIE", ""),
                "active": True
            },
            {
                "id": "account_2",
                "name": "Infogenx IT Projects",
                "username": "infogenxitprojects@gmail.com",
                "password": "infogenxitprojects@123",
                "cookie": "",
                "active": True
            }
        ]
        # Also check master_credentials.json if available
        master_cred_path = BASE_DIR.parent / "credentials" / "master_credentials.json"
        if master_cred_path.exists():
            try:
                m_data = json.load(open(master_cred_path, encoding="utf-8"))
                lk_info = m_data.get("linkedin_infogenx")
                if lk_info and lk_info.get("username"):
                    accounts[1]["username"] = lk_info.get("username")
                    accounts[1]["password"] = lk_info.get("password")
            except Exception:
                pass

        try:
            with open(ACCOUNTS_FILE, "w", encoding="utf-8") as f:
                json.dump(accounts, f, indent=2)
        except Exception:
            pass

    return accounts

def get_account_by_id(account_id):
    accounts = load_accounts()
    for acc in accounts:
        if acc.get("id") == account_id:
            return acc
    return accounts[0] if accounts else None

def save_new_account(name, username, password, cookie=""):
    accounts = load_accounts()
    new_id = f"account_{len(accounts) + 1}"
    acc = {
        "id": new_id,
        "name": name,
        "username": username,
        "password": password,
        "cookie": cookie,
        "active": True
    }
    accounts.append(acc)
    with open(ACCOUNTS_FILE, "w", encoding="utf-8") as f:
        json.dump(accounts, f, indent=2)
    return acc

# Defaults from first account
_initial_accounts = load_accounts()
PRIMARY_ACCOUNT = _initial_accounts[0] if _initial_accounts else {}

LINKEDIN_USERNAME = PRIMARY_ACCOUNT.get("username", "srihariharan213@gmail.com")
LINKEDIN_PASSWORD = PRIMARY_ACCOUNT.get("password", "Hariharan@213")

DEFAULT_QUERY = os.getenv("DEFAULT_QUERY", '("HR Intern" OR "Human Resources Intern" OR "Looking for HR Internship")')
MAX_PROFILES = int(os.getenv("MAX_PROFILES", "25"))
MAX_PAGES = int(os.getenv("MAX_PAGES", "10"))

# Target Roles Supported by Infogenx Recruitment
ROLE_PRESETS = {
    "1": {
        "title": "HR Intern",
        "query": '("HR Intern" OR "Human Resources Intern" OR "Looking for HR Internship")',
        "headline_default": "HR Intern",
        "is_graphic_designer": False
    },
    "2": {
        "title": "HR / HR Executive",
        "query": '("HR Executive" OR "Human Resources Generalist" OR "HR Officer" OR "Talent Acquisition")',
        "headline_default": "HR Executive",
        "is_graphic_designer": False
    },
    "3": {
        "title": "Graphic Designer & Digital Marketing Intern",
        "query": '("Graphic Design Intern" OR "Digital Marketing Intern" OR "Graphic Designer Intern")',
        "headline_default": "Graphic Designer & Digital Marketing Intern",
        "is_graphic_designer": True
    },
    "4": {
        "title": "Graphic Designer & Digital Marketing",
        "query": '("Graphic Designer" OR "Digital Marketing Specialist" OR "Graphic & Digital Designer")',
        "headline_default": "Graphic Designer & Digital Marketing Specialist",
        "is_graphic_designer": True
    },
    "5": {
        "title": "Digital Marketing (5+ Years of Experience)",
        "query": '("Senior Digital Marketing" OR "Digital Marketing Manager" OR "Digital Marketing Lead" OR "SEO Manager")',
        "headline_default": "Digital Marketing Specialist (5+ Years)",
        "is_graphic_designer": False
    }
}

# Target Google Sheet & Apps Script
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID", "1Xb8Z2M6rBANcqNgvE37XIapEINqLD3Gaf0wOqdfdmTs")
APPS_SCRIPT_ID = "1G2_d05xDJFTIkOhZoIdAkxSkcf7mpBXNi53CXLBX1n_8HVMGM6DVXblT"
SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE", "")

if not SERVICE_ACCOUNT_FILE or not os.path.exists(SERVICE_ACCOUNT_FILE):
    candidate_paths = [
        BASE_DIR / "credentials" / "service_account.json",
        BASE_DIR.parent / "credentials" / "splendid-planet-504710-d0-d1bee6e83a75.json",
        BASE_DIR.parent / "credentials" / "sheet-sync-504707-85df40232946.json",
    ]
    for p in candidate_paths:
        if p.exists():
            SERVICE_ACCOUNT_FILE = str(p)
            break

LINKEDIN_COOKIE = os.getenv("LINKEDIN_COOKIE", "")

SHEET_TABS = {
    "PROFILE": "Profile_Search",
    "JOB_POSTS": "Job_Post_Applicants",
    "ROLE_SEARCH": "Role_Search",
    "MASTER": "Master_Leads",
    "BDE": "BDE_Field_Sales_TamilNadu"
}

# --- GOOGLE SHEETS CLIENT CACHE ---
_gspread_client = None
_gspread_sheet = None

def get_client():
    global _gspread_client, _gspread_sheet
    if _gspread_sheet is not None:
        return _gspread_sheet

    if not SERVICE_ACCOUNT_FILE or not os.path.exists(SERVICE_ACCOUNT_FILE):
        return None

    try:
        import gspread
        from google.oauth2.service_account import Credentials
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=scopes)
        _gspread_client = gspread.authorize(creds)
        _gspread_sheet = _gspread_client.open_by_key(GOOGLE_SHEET_ID)
        return _gspread_sheet
    except Exception as e:
        print(f"[!] Google Sheets Notice: {e}")
        return None

def get_worksheet(tab_name):
    sh = get_client()
    if not sh:
        return None
    try:
        return sh.worksheet(tab_name)
    except Exception:
        try:
            ws = sh.add_worksheet(title=tab_name, rows="1000", cols="12")
            return ws
        except Exception:
            return None

def append_to_sheet(tab_name, row_data):
    ws = get_worksheet(tab_name)
    if ws:
        try:
            ws.append_row(row_data)
            return True
        except Exception as e:
            print(f"[!] Append error in '{tab_name}': {e}")
    return False

# --- DEDICATED SYNC HELPERS ---
def sync_profile_lead(record):
    name = str(record.get("Name", "")).strip()
    headline = str(record.get("Headline", "")).strip()
    email = str(record.get("Email", "")).strip()
    phone = str(record.get("Phone", "")).strip()
    location = str(record.get("Location") or record.get("Search Query") or "Tamil Nadu").strip()
    profile_link = str(record.get("Profile Link") or record.get("Profile URL") or "").strip()
    post_link = str(record.get("Post Link") or f"{profile_link.rstrip('/')}/recent-activity/all/").strip()
    date_scraped = str(record.get("Date Scraped", str(datetime.today().date())))
    status = str(record.get("Status", "Collected"))

    # Strictly enforce mandatory fields: Name, Email, Phone, Profile Link, Post Link
    if not email or email.upper() == "N/A" or not phone or phone.upper() == "N/A":
        print(f"    [-] Skipping record for '{name}': Missing mandatory Email or Phone.")
        return False

    # Generate 1-Click WhatsApp Direct Link
    phone_digits = re.sub(r"\D", "", phone)[-10:] if phone else ""
    wa_link = f"https://wa.me/91{phone_digits}" if len(phone_digits) == 10 else ""

    row = [
        name,
        headline or f"Candidate - {location}",
        email,
        phone,
        location,
        profile_link,
        post_link,
        date_scraped,
        status,
        wa_link
    ]
    append_to_sheet(SHEET_TABS["PROFILE"], row)

    master_row = [
        "Profile Search",
        name,
        headline or f"Candidate - {location}",
        email,
        phone,
        profile_link,
        f"Post: {post_link} | Loc: {location}",
        date_scraped,
        status,
        wa_link
    ]
    append_to_sheet(SHEET_TABS["MASTER"], master_row)

def sync_job_applicant(record):
    row = [
        record.get("Name", "N/A"),
        record.get("Headline", "N/A"),
        record.get("Email", "N/A"),
        record.get("Phone", "N/A"),
        record.get("Location", "N/A"),
        record.get("Profile URL", "N/A"),
        record.get("Job ID", "N/A"),
        record.get("Job Link", "N/A"),
        record.get("Date Extracted", str(datetime.today().date())),
        record.get("Status", "Pending")
    ]
    append_to_sheet(SHEET_TABS["JOB_POSTS"], row)

    master_row = [
        "Job Applicant",
        record.get("Name", "N/A"),
        record.get("Headline", "N/A"),
        record.get("Email", "N/A"),
        record.get("Phone", "N/A"),
        record.get("Profile URL", "N/A"),
        f"Job: {record.get('Job Link', '')}",
        record.get("Date Extracted", str(datetime.today().date())),
        record.get("Status", "Pending")
    ]
    append_to_sheet(SHEET_TABS["MASTER"], master_row)

def sync_role_lead(record):
    row = [
        record.get("Target Role", "N/A"),
        record.get("Candidate Name", "N/A"),
        record.get("Headline/Title", "N/A"),
        record.get("Email", "N/A"),
        record.get("Phone", "N/A"),
        record.get("Location", "N/A"),
        record.get("Profile URL", "N/A"),
        record.get("Invite Note", "N/A"),
        record.get("Date Sent", str(datetime.today().date())),
        record.get("Status", "Sent")
    ]
    append_to_sheet(SHEET_TABS["ROLE_SEARCH"], row)

    master_row = [
        f"Role: {record.get('Target Role', '')}",
        record.get("Candidate Name", "N/A"),
        record.get("Headline/Title", "N/A"),
        record.get("Email", "N/A"),
        record.get("Phone", "N/A"),
        record.get("Profile URL", "N/A"),
        f"Role Search: {record.get('Target Role', '')}",
        record.get("Date Sent", str(datetime.today().date())),
        record.get("Status", record.get("Status", "Sent"))
    ]
    append_to_sheet(SHEET_TABS["MASTER"], master_row)

def sync_bde_lead(record):
    name = str(record.get("Name", record.get("Candidate Name", ""))).strip()
    headline = str(record.get("Headline", record.get("Headline/Title", ""))).strip()
    email = str(record.get("Email", "")).strip()
    phone = str(record.get("Phone", "")).strip()
    location = str(record.get("Location") or record.get("Search Query") or "Chennai / Tamil Nadu").strip()
    profile_link = str(record.get("Profile Link") or record.get("Profile URL") or "").strip()
    date_scraped = str(record.get("Date Scraped", record.get("Date Added", str(datetime.today().date()))))
    status = str(record.get("Status", "Collected"))

    row = [
        name,
        headline or f"BDE Candidate - {location}",
        record.get("Experience", "0-3 Years"),
        location,
        "Tamil (Mandatory)",
        "Yes (Field Sales)",
        "Open to Relocate",
        email,
        phone,
        profile_link,
        date_scraped,
        status
    ]
    append_to_sheet(SHEET_TABS.get("BDE", "BDE_Field_Sales_TamilNadu"), row)
    return True

# --- LOCAL FILE BACKUP HELPER ---
def save_data_locally(data, filename_prefix="linkedin_results"):
    if not data:
        print("[-] No data to save.")
        return None

    import pandas as pd
    data_dir = BASE_DIR / "output"
    data_dir.mkdir(exist_ok=True)

    df = pd.DataFrame(data)
    csv_path = data_dir / f"{filename_prefix}.csv"
    xlsx_path = data_dir / f"{filename_prefix}.xlsx"

    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    try:
        df.to_excel(xlsx_path, index=False)
    except Exception:
        pass

    print(f"[+] Data successfully saved locally:")
    print(f"    - CSV:   {csv_path}")
    print(f"    - Excel: {xlsx_path}")
    return csv_path
