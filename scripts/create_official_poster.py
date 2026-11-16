import os
from PIL import Image, ImageDraw, ImageFont

OUT_DIR = "d:/infonix/daasho-recruitment-automation/creatives"
LOGO_PATH = os.path.join(OUT_DIR, "lockup-transparent.png")
EMBLEM_PATH = os.path.join(OUT_DIR, "emblem-yellow.png")
FONT_BOLD = "C:/Windows/Fonts/segoeuib.ttf"
FONT_REG = "C:/Windows/Fonts/segoeui.ttf"
FONT_TITLE = "C:/Windows/Fonts/arialbd.ttf"

def create_poster_1_royal_blue():
    """Variation 1: Premium Royal Blue & Yellow - High Reach Corporate Format"""
    w, h = 1080, 1350
    img = Image.new("RGBA", (w, h), (11, 44, 115, 255))
    draw = ImageDraw.Draw(img)

    # Gradient background
    top_c = (8, 30, 80)
    bot_c = (14, 62, 160)
    for y in range(h):
        r = int(top_c[0] + (bot_c[0] - top_c[0]) * (y / h))
        g = int(top_c[1] + (bot_c[1] - top_c[1]) * (y / h))
        b = int(top_c[2] + (bot_c[2] - top_c[2]) * (y / h))
        draw.line([(0, y), (w, y)], fill=(r, g, b, 255))

    # Corner Accents
    draw.polygon([(0, 0), (260, 0), (0, 170)], fill=(255, 193, 7, 35))
    draw.polygon([(w, h), (w - 280, h), (w, h - 200)], fill=(255, 193, 7, 30))

    # Fonts
    f_huge = ImageFont.truetype(FONT_TITLE, 44)
    f_title = ImageFont.truetype(FONT_BOLD, 32)
    f_sub = ImageFont.truetype(FONT_BOLD, 23)
    f_body = ImageFont.truetype(FONT_REG, 21)
    f_body_b = ImageFont.truetype(FONT_BOLD, 21)
    f_small = ImageFont.truetype(FONT_REG, 18)
    f_badge = ImageFont.truetype(FONT_BOLD, 19)

    # 1. Official Logo
    if os.path.exists(LOGO_PATH):
        logo = Image.open(LOGO_PATH).convert("RGBA")
        target_w = 400
        target_h = int(logo.height * (target_w / logo.width))
        logo = logo.resize((target_w, target_h), Image.Resampling.LANCZOS)
        img.paste(logo, ((w - target_w) // 2, 40), logo)

    tagline = "Everyday Delivery, Made Affordable — Food, Groceries & Essentials"
    tw = draw.textlength(tagline, font=f_small)
    draw.text(((w - tw) // 2, 195), tagline, fill=(215, 232, 255), font=f_small)

    # 2. Hiring Badge
    badge = "✦ WE ARE HIRING — CHENNAI FOUNDING TEAM ✦"
    bw = draw.textlength(badge, font=f_badge) + 36
    bx = (w - bw) // 2
    draw.rounded_rectangle([bx, 235, bx + bw, 278], radius=21, fill=(255, 193, 7))
    draw.text(((w - draw.textlength(badge, font=f_badge)) // 2, 244), badge, fill=(10, 30, 75), font=f_badge)

    # 3. Main Title
    t1 = "BUSINESS DEVELOPMENT EXECUTIVE"
    draw.text(((w - draw.textlength(t1, font=f_huge)) // 2, 298), t1, fill=(255, 255, 255), font=f_huge)

    st = "Field Sales & Merchant Partnerships • Onboarding Ground Team"
    draw.text(((w - draw.textlength(st, font=f_sub)) // 2, 360), st, fill=(255, 215, 64), font=f_sub)

    # 4. Requirements Card (Crisp White Container)
    c_top, c_bot = 410, 850
    draw.rounded_rectangle([60, c_top, w - 60, c_bot], radius=24, fill=(255, 255, 255, 252))
    draw.rounded_rectangle([60, c_top, w - 60, c_top + 52], radius=24, fill=(240, 245, 255))
    draw.text((95, c_top + 13), "CANDIDATE ELIGIBILITY CRITERIA", fill=(11, 44, 115), font=f_body_b)

    reqs = [
        ("📍 Location:", "Chennai, Tamil Nadu (Candidates across TN ready to relocate welcome)"),
        ("⏳ Experience:", "0 to 3 Years (Freshers & Experienced Sales Executives Welcome)"),
        ("🗣️ Language:", "TAMIL (Mandatory) + Basic English / Other Languages"),
        ("🎯 Domain Interest:", "Strong passion for Field Sales, merchant meetings & shop onboarding"),
        ("🛵 Mobility:", "Two-Wheeler (Bike/Scooter) + Valid Driving License Mandatory"),
        ("⚡ Joining:", "Immediate Joiners / Within 7 to 15 Days Preferred")
    ]

    curr_y = c_top + 70
    for lbl, val in reqs:
        draw.text((95, curr_y), "✔", fill=(0, 165, 65), font=f_body_b)
        draw.text((125, curr_y), lbl, fill=(12, 28, 60), font=f_body_b)
        lw = draw.textlength(lbl, font=f_body_b)
        draw.text((135 + lw, curr_y), val, fill=(45, 55, 75), font=f_body)
        draw.line([(95, curr_y + 45), (w - 95, curr_y + 45)], fill=(235, 240, 248), width=1)
        curr_y += 58

    # 5. Compensation & Perks (Daasho Yellow Container)
    p_top, p_bot = 870, 1115
    draw.rounded_rectangle([60, p_top, w - 60, p_bot], radius=24, fill=(255, 193, 7, 245))
    draw.text((95, p_top + 18), "SALARY & EXCLUSIVE PERKS", fill=(10, 30, 75), font=f_title)

    perks = [
        "💰 ₹25,000+ per month CTC + High Monthly Performance Incentives",
        "⛽ Daily Fuel & Travel Allowance for Field Operations",
        "🏥 Medical Insurance Coverage + PF (Provident Fund)",
        "🚀 High-Growth Career Path: Promotion to Team Lead / ASM in 6-12 Months"
    ]
    py = p_top + 72
    for p in perks:
        draw.text((95, py), p, fill=(15, 30, 60), font=f_body_b)
        py += 46

    # 6. Footer CTA
    cta_top = 1135
    draw.rounded_rectangle([60, cta_top, w - 60, h - 50], radius=20, fill=(6, 24, 65))
    draw.text((95, cta_top + 18), "HOW TO APPLY:", fill=(255, 193, 7), font=f_body_b)
    draw.text((95, cta_top + 52), "👉 Fill out the Google Form link in the post description", fill=(255, 255, 255), font=f_body)
    draw.text((95, cta_top + 90), "📲 Fast-track WhatsApp: +91 9787806366 | careers@daasho.com | daasho.com", fill=(200, 225, 255), font=f_body_b)

    out_jpg = os.path.join(OUT_DIR, "Daasho_BDE_Poster_1_RoyalBlue.jpg")
    img.convert("RGB").save(out_jpg, "JPEG", quality=95)
    print(f"[+] Generated: {out_jpg}")


def create_poster_2_high_energy_yellow():
    """Variation 2: High Energy Launch Edition - Yellow Hero Header"""
    w, h = 1080, 1350
    img = Image.new("RGBA", (w, h), (245, 248, 255, 255))
    draw = ImageDraw.Draw(img)

    # Fonts
    f_huge = ImageFont.truetype(FONT_TITLE, 44)
    f_title = ImageFont.truetype(FONT_BOLD, 30)
    f_sub = ImageFont.truetype(FONT_BOLD, 23)
    f_body = ImageFont.truetype(FONT_REG, 21)
    f_body_b = ImageFont.truetype(FONT_BOLD, 21)
    f_small = ImageFont.truetype(FONT_REG, 18)
    f_badge = ImageFont.truetype(FONT_BOLD, 19)

    # 1. Top Header: Deep Navy
    header_h = 360
    draw.rectangle([0, 0, w, header_h], fill=(11, 44, 115))

    if os.path.exists(LOGO_PATH):
        logo = Image.open(LOGO_PATH).convert("RGBA")
        target_w = 380
        target_h = int(logo.height * (target_w / logo.width))
        logo = logo.resize((target_w, target_h), Image.Resampling.LANCZOS)
        img.paste(logo, ((w - target_w) // 2, 35), logo)

    # Badge
    b_txt = "🚀 BUILD WHAT CHENNAI WILL USE EVERY DAY"
    bw = draw.textlength(b_txt, font=f_badge) + 36
    draw.rounded_rectangle([((w - bw) // 2), 175, ((w - bw) // 2) + bw, 215], radius=20, fill=(255, 193, 7))
    draw.text(((w - draw.textlength(b_txt, font=f_badge)) // 2, 184), b_txt, fill=(11, 44, 115), font=f_badge)

    t1 = "BUSINESS DEVELOPMENT EXECUTIVE"
    draw.text(((w - draw.textlength(t1, font=f_huge)) // 2, 235), t1, fill=(255, 255, 255), font=f_huge)
    st = "Field Sales & Merchant Onboarding | 0 - 3 Years Experience"
    draw.text(((w - draw.textlength(st, font=f_sub)) // 2, 298), st, fill=(255, 215, 64), font=f_sub)

    # 2. Key Highlights Bar
    bar_y = 380
    draw.rounded_rectangle([50, bar_y, w - 50, bar_y + 80], radius=16, fill=(255, 193, 7))
    draw.text((75, bar_y + 12), "🔥 FIXED SALARY: ₹25,000+ / Month + HIGH INCENTIVES", fill=(11, 44, 115), font=f_title)
    draw.text((75, bar_y + 46), "⛽ Petrol / Travel Allowance + Medical Insurance + PF Included", fill=(20, 40, 80), font=f_body_b)

    # 3. Requirement Grid (2 Columns or Clean Stack)
    card_top = 485
    draw.rounded_rectangle([50, card_top, w - 50, 970], radius=20, fill=(255, 255, 255), outline=(210, 220, 240), width=2)
    draw.text((80, card_top + 20), "📌 MANDATORY REQUIREMENTS & ELIGIBILITY", fill=(11, 44, 115), font=f_title)

    items = [
        ("📍 Working Location:", "Chennai, Tamil Nadu"),
        ("✈️ Relocation:", "Candidates across Tamil Nadu ready to relocate to Chennai are welcome!"),
        ("⏳ Experience Level:", "0 to 3 Years (Freshers & Experienced Sales Pros)"),
        ("🗣️ Language:", "TAMIL (Mandatory) — Must speak fluently with merchants"),
        ("💼 Job Profile:", "Onboarding restaurants, grocery stores & retail partners on-ground"),
        ("🛵 Essential:", "Two-Wheeler (Bike/Scooter) + Valid Driving License"),
        ("⚡ Join Date:", "Immediate Joiners / Within 7 to 15 Days")
    ]

    cy = card_top + 75
    for lbl, val in items:
        draw.text((80, cy), "★", fill=(255, 160, 0), font=f_body_b)
        draw.text((110, cy), lbl, fill=(15, 30, 60), font=f_body_b)
        lw = draw.textlength(lbl, font=f_body_b)
        draw.text((120 + lw, cy), val, fill=(50, 60, 80), font=f_body)
        draw.line([(80, cy + 45), (w - 80, cy + 45)], fill=(240, 244, 250), width=1)
        cy += 58

    # 4. Bottom Box: Apply Info
    cta_y = 995
    draw.rounded_rectangle([50, cta_y, w - 50, h - 45], radius=20, fill=(11, 44, 115))
    draw.text((85, cta_y + 25), "EASY 1-MINUTE APPLICATION PROCESS:", fill=(255, 193, 7), font=f_title)
    draw.text((85, cta_y + 75), "1. Click the Google Form link in the post description & submit your details.", fill=(255, 255, 255), font=f_body)
    draw.text((85, cta_y + 115), "2. Or WhatsApp your Resume directly to HR: +91 9787806366", fill=(255, 255, 255), font=f_body)
    draw.text((85, cta_y + 155), "3. Shortlisted candidates will get an interview schedule within 24 hours.", fill=(200, 230, 255), font=f_body_b)
    draw.text((85, cta_y + 200), "🌐 Daasho Technologies Private Limited | Chennai | daasho.com", fill=(255, 215, 64), font=f_small)

    out_jpg = os.path.join(OUT_DIR, "Daasho_BDE_Poster_2_LaunchEdition.jpg")
    img.convert("RGB").save(out_jpg, "JPEG", quality=95)
    print(f"[+] Generated: {out_jpg}")


if __name__ == "__main__":
    create_poster_1_royal_blue()
    create_poster_2_high_energy_yellow()
