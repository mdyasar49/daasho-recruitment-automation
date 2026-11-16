import os
from PIL import Image, ImageDraw, ImageFont

def generate_poster():
    width = 1080
    height = 1350

    # 1. Background with brand gradient
    poster = Image.new("RGBA", (width, height), (11, 44, 115, 255)) # #0B2C73
    draw = ImageDraw.Draw(poster)

    # Vertical gradient top to bottom
    top_color = (8, 30, 80)
    bot_color = (13, 58, 150)
    for y in range(height):
        r = int(top_color[0] + (bot_color[0] - top_color[0]) * (y / height))
        g = int(top_color[1] + (bot_color[1] - top_color[1]) * (y / height))
        b = int(top_color[2] + (bot_color[2] - top_color[2]) * (y / height))
        draw.line([(0, y), (width, y)], fill=(r, g, b, 255))

    # Decorative geometric accents in Daasho yellow (#FFC107)
    draw.polygon([(0, 0), (280, 0), (0, 180)], fill=(255, 193, 7, 35))
    draw.polygon([(width, height), (width - 320, height), (width, height - 220)], fill=(255, 193, 7, 30))

    # Fonts
    font_bold = "C:/Windows/Fonts/segoeuib.ttf"
    font_reg = "C:/Windows/Fonts/segoeui.ttf"
    font_title = "C:/Windows/Fonts/arialbd.ttf"

    f_huge = ImageFont.truetype(font_title, 46)
    f_title = ImageFont.truetype(font_bold, 36)
    f_sub = ImageFont.truetype(font_bold, 24)
    f_body = ImageFont.truetype(font_reg, 22)
    f_body_bold = ImageFont.truetype(font_bold, 22)
    f_small = ImageFont.truetype(font_reg, 18)
    f_badge = ImageFont.truetype(font_bold, 20)

    # 2. Insert Official Daasho Logo
    logo_path = "d:/infonix/daasho-recruitment-automation/creatives/lockup-transparent.png"
    if os.path.exists(logo_path):
        logo = Image.open(logo_path).convert("RGBA")
        # Resize maintaining aspect ratio
        target_w = 420
        ratio = target_w / logo.width
        target_h = int(logo.height * ratio)
        logo = logo.resize((target_w, target_h), Image.Resampling.LANCZOS)
        logo_x = (width - target_w) // 2
        poster.paste(logo, (logo_x, 45), logo)

    # Top Tagline
    tagline = "Everyday Delivery, Made Affordable — Food, Groceries & Essentials"
    tw = draw.textlength(tagline, font=f_small)
    draw.text(((width - tw) // 2, 205), tagline, fill=(210, 228, 255), font=f_small)

    # 3. WE ARE HIRING BADGE
    badge_text = "✦ WE ARE HIRING ✦"
    bw = draw.textlength(badge_text, font=f_badge) + 40
    bx = (width - bw) // 2
    draw.rounded_rectangle([bx, 245, bx + bw, 290], radius=22, fill=(255, 193, 7)) # Yellow badge
    draw.text(((width - draw.textlength(badge_text, font=f_badge)) // 2, 254), badge_text, fill=(10, 30, 75), font=f_badge)

    # 4. Job Title
    title1 = "BUSINESS DEVELOPMENT EXECUTIVE"
    t1_w = draw.textlength(title1, font=f_huge)
    draw.text(((width - t1_w) // 2, 310), title1, fill=(255, 255, 255), font=f_huge)

    subtitle = "Field Sales & Merchant Onboarding • Chennai Launch"
    st_w = draw.textlength(subtitle, font=f_sub)
    draw.text(((width - st_w) // 2, 375), subtitle, fill=(255, 215, 64), font=f_sub)

    # 5. Main Card: Role Requirements (Clean White Card)
    card_top = 425
    card_bot = 855
    draw.rounded_rectangle([60, card_top, width - 60, card_bot], radius=24, fill=(255, 255, 255, 250))
    
    # Card Header
    draw.rounded_rectangle([60, card_top, width - 60, card_top + 55], radius=24, fill=(240, 244, 255))
    draw.text((95, card_top + 14), "KEY CANDIDATE REQUIREMENTS", fill=(11, 44, 115), font=f_body_bold)

    items = [
        ("📍 Location:", "Chennai, Tamil Nadu (Open to TN candidates ready to relocate)"),
        ("⏳ Experience:", "0 to 3 Years (Freshers & Experienced Candidates Welcome)"),
        ("🗣️ Language:", "Tamil (Mandatory) + Basic English"),
        ("🎯 Domain:", "Passionate about Field Sales & Merchant Relationship Building"),
        ("🛵 Mobility:", "Two-Wheeler (Bike/Scooter) + Valid Driving License Required"),
        ("⚡ Availability:", "Immediate Joiners / Within 7 to 15 Days Preferred")
    ]

    curr_y = card_top + 75
    for label, val in items:
        draw.text((95, curr_y), "✔", fill=(0, 160, 60), font=f_body_bold)
        draw.text((125, curr_y), label, fill=(15, 25, 45), font=f_body_bold)
        lbl_w = draw.textlength(label, font=f_body_bold)
        draw.text((135 + lbl_w, curr_y), val, fill=(50, 60, 80), font=f_body)
        draw.line([(95, curr_y + 44), (width - 95, curr_y + 44)], fill=(235, 238, 245), width=1)
        curr_y += 58

    # 6. Secondary Card: Package & Perks (Daasho Yellow Glow Box)
    perks_top = 875
    perks_bot = 1110
    draw.rounded_rectangle([60, perks_top, width - 60, perks_bot], radius=24, fill=(255, 193, 7, 240))
    
    draw.text((95, perks_top + 20), "WHAT DAASHO OFFERS YOU", fill=(10, 30, 75), font=f_title)

    perks = [
        "💰 ₹25,000+ per month CTC + High Monthly Performance Incentives",
        "⛽ Daily Fuel & Travel Allowance for Field Movement",
        "🏥 Comprehensive Medical Insurance & PF (Provident Fund)",
        "🚀 Fast-Track Promotion to Team Lead / Area Sales Manager"
    ]

    py = perks_top + 75
    for p in perks:
        draw.text((95, py), p, fill=(15, 30, 60), font=f_body_bold)
        py += 46

    # 7. Footer: Call to Action
    cta_box_top = 1130
    draw.rounded_rectangle([60, cta_box_top, width - 60, height - 55], radius=20, fill=(6, 25, 68))
    
    cta_title = "HOW TO APPLY:"
    draw.text((95, cta_box_top + 20), cta_title, fill=(255, 193, 7), font=f_body_bold)
    
    cta_line1 = "👉 Fill the 1-Minute Application Form linked in the post description"
    cta_line2 = "📲 WhatsApp HR Directly: +91 9787806366 | Web: https://daasho.com"
    draw.text((95, cta_box_top + 55), cta_line1, fill=(255, 255, 255), font=f_body)
    draw.text((95, cta_box_top + 95), cta_line2, fill=(200, 225, 255), font=f_body_bold)

    # Save
    out_dir = "d:/infonix/daasho-recruitment-automation/creatives"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "Daasho_BDE_Official_Poster.png")
    poster.save(out_path, "PNG")
    print(f"[+] Saved high-resolution poster to: {out_path}")

    # Also save as JPEG for easy sharing
    out_jpg = os.path.join(out_dir, "Daasho_BDE_Official_Poster.jpg")
    poster.convert("RGB").save(out_jpg, "JPEG", quality=95)
    print(f"[+] Saved JPEG poster to: {out_jpg}")

if __name__ == "__main__":
    generate_poster()
