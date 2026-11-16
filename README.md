# 🚀 Daasho Recruitment & Lead Automation Suite

An enterprise-grade talent acquisition and candidate sourcing engine built specifically for **Daasho Technologies Private Limited** (Chennai, Tamil Nadu).

---

## 🌟 Highlights & Capabilities
- **LinkedIn High-Reach Post Copies:** Formatted for maximum algorithm reach for **BDE (Field Sales)** & **HR Executive** roles.
- **Brand Creatives Included:** High-resolution hiring graphics in Daasho brand colors (**Royal Blue `#0B3C95` & Energetic Yellow `#FFC107`**) with official logo & QR CTA.
- **Automated Google Form:** 9-question candidate application form linking directly to the live Google Sheet.
- **Job Seeker Harvester:** Scrapes active candidates with 100% verified mobile numbers and generates 1-Click WhatsApp links.
- **Secure Credentials Management:** Configured with `Daasho App Manager` credentials.

---

## 📂 Repository Structure

```tree
daasho-recruitment-automation/
├── creatives/
│   ├── Daasho_BDE_Hiring_Poster.jpg           # BDE Field Sales Poster
│   └── Daasho_HR_Executive_Hiring_Poster.jpg  # HR Recruiter Poster
├── google_apps_scripts/
│   └── create_daasho_google_form.gs           # Auto Form Generator & Sheet Linker
├── scripts/
│   ├── harvest_daasho_candidates.py           # 100% Phone Number Lead Harvester
│   ├── 1_daasho_profile_scraper.py            # Deep Profile Contact Scraper
│   └── config.py                              # Central Config & Sync Engine
├── credentials/
│   └── daasho_credentials.json                # Daasho App Manager Credentials
├── DAASHO_LINKEDIN_HIRING_CAMPAIGN.md         # Official LinkedIn Post Copies
├── .env.example
├── .gitignore
└── README.md
```

---

## 🚀 Quick Start

### 1. Run Candidate Phone Harvester:
```bash
python scripts/harvest_daasho_candidates.py --purpose hiring --query "Business Development Executive" --locations "Chennai, Tamil Nadu" --max 25
```

### 2. Connect Google Form to Sheet:
1. Open [Google Apps Script Editor](https://script.google.com/).
2. Run `google_apps_scripts/create_daasho_google_form.gs`.
3. The generated public URL automatically writes all applications to:
   `https://docs.google.com/spreadsheets/d/1kxEeoG4dVSXgl5qfDTHGf3LlyEPgMQjrlAjvWFzzZ28/edit`

---

## 🏢 Organization
**Daasho Technologies Private Limited**  
Chennai, Tamil Nadu, India  
Fast-Track Contact: `+91 9787806366`
