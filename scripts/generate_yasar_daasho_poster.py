import os
from PIL import Image, ImageDraw, ImageFont

def generate_yasar_poster():
    w, h = 1080, 1540  # High-definition portrait matching Varnika & Sandhiya
    img = Image.new("RGBA", (w, h), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Decorative top header bar
    draw.rectangle([0, 0, w, 14], fill=(11, 60, 149)) # Navy top border
    draw.rectangle([0, 14, w, 22], fill=(255, 193, 7)) # Yellow accent line

    # Fonts
    font_bold = "C:/Windows/Fonts/segoeuib.ttf"
    font_reg = "C:/Windows/Fonts/segoeui.ttf"
    font_title = "C:/Windows/Fonts/arialbd.ttf"
    font_script = "C:/Windows/Fonts/comicbd.ttf" if os.path.exists("C:/Windows/Fonts/comicbd.ttf") else font_bold

    f_huge = ImageFont.truetype(font_title, 42)
    f_hiring = ImageFont.truetype(font_title, 78)
    f_role = ImageFont.truetype(font_title, 34)
    f_card_title = ImageFont.truetype(font_bold, 24)
    f_body = ImageFont.truetype(font_reg, 21)
    f_body_b = ImageFont.truetype(font_bold, 21)
    f_sub = ImageFont.truetype(font_bold, 24)
    f_script = ImageFont.truetype(font_script, 26)
    f_bar = ImageFont.truetype(font_bold, 20)
    f_bar_sub = ImageFont.truetype(font_reg, 19)
    f_footer_name = ImageFont.truetype(font_bold, 27)
    f_footer_sub = ImageFont.truetype(font_reg, 20)
    f_btn = ImageFont.truetype(font_bold, 22)

    # 1. Top Left: Official Daasho Logo (on-white version for crisp blue text)
    logo_path = "d:/infonix/daasho-recruitment-automation/creatives/lockup-on-white.png"
    if os.path.exists(logo_path):
        logo = Image.open(logo_path).convert("RGBA")
        target_w = 340
        target_h = int(logo.height * (target_w / logo.width))
        logo = logo.resize((target_w, target_h), Image.Resampling.LANCZOS)
        img.paste(logo, (55, 45), logo)

    # Top Right: Slogan like Sandhiya's poster
    draw.text((700, 52), "Build Your Career", fill=(25, 135, 60), font=f_script)
    draw.text((740, 88), "With Us! *", fill=(25, 135, 60), font=f_script)

    # 2. Megaphone & "WE'RE HIRING!" (Sandhiya & Varnika style)
    draw.rounded_rectangle([55, 175, 430, 240], radius=32, fill=(255, 193, 7))
    draw.text((85, 182), ">>  WE'RE", fill=(11, 44, 115), font=f_huge)
    
    # Big Bold HIRING!
    draw.text((55, 245), "HIRING!", fill=(11, 44, 115), font=f_hiring)

    # Right of Hiring: Growth team callout box
    draw.rounded_rectangle([475, 245, w - 55, 335], radius=18, fill=(240, 246, 255), outline=(190, 215, 250), width=2)
    draw.text((500, 258), "Join Our Dynamic Growth Team!", fill=(11, 44, 115), font=f_sub)
    draw.text((500, 292), "Be a key driver of Chennai's everyday delivery platform.", fill=(70, 85, 110), font=ImageFont.truetype(font_reg, 18))

    # 3. Role Title Banner (Navy Pill)
    pill_y = 358
    draw.rounded_rectangle([55, pill_y, w - 55, pill_y + 75], radius=24, fill=(11, 44, 115))
    role_text = "BUSINESS DEVELOPMENT EXECUTIVE (BDE)"
    rw = draw.textlength(role_text, font=f_role)
    draw.text(((w - rw) // 2, pill_y + 18), role_text, fill=(255, 255, 255), font=f_role)

    # Sub slogan under pill
    slog = "Grow Your Career With Daasho  |  Field Sales & Merchant Onboarding"
    sw = draw.textlength(slog, font=f_sub)
    draw.text(((w - sw) // 2, pill_y + 88), slog, fill=(15, 45, 110), font=f_sub)

    # 4. Horizontal Quick Highlights Bar (Sandhiya & Varnika Style)
    bar_y = 485
    draw.rounded_rectangle([55, bar_y, w - 55, bar_y + 90], radius=18, fill=(11, 44, 115))
    
    cols = [
        ("Location", "Chennai, TN", 85),
        ("Salary", "Rs. 25,000+ / mo", 325),
        ("Role Type", "Field Sales", 585),
        ("Joining", "Immediate Joiners", 825)
    ]
    for title, val, cx in cols:
        draw.text((cx, bar_y + 16), title.upper(), fill=(255, 193, 7), font=f_bar)
        draw.text((cx, bar_y + 48), val, fill=(255, 255, 255), font=f_bar_sub)
        if cx < 800:
            draw.line([(cx + 205, bar_y + 15), (cx + 205, bar_y + 75)], fill=(30, 70, 150), width=1)

    # 5. Two Cards Side-by-Side (Varnika & Sandhiya Layout)
    card_w = 465
    c_top = 605
    c_h = 585

    # LEFT CARD: Key Responsibilities (Yellow Theme)
    draw.rounded_rectangle([55, c_top, 55 + card_w, c_top + c_h], radius=20, fill=(255, 253, 245), outline=(255, 205, 80), width=2)
    # Header
    draw.rounded_rectangle([55, c_top, 55 + card_w, c_top + 55], radius=20, fill=(255, 193, 7))
    draw.text((75, c_top + 14), "KEY RESPONSIBILITIES", fill=(11, 44, 115), font=f_card_title)

    resps = [
        ("Onboard neighborhood restaurants, grocery stores & local merchants.", 2),
        ("Pitch Daasho's zero-commission merchant partnership plans.", 2),
        ("Generate quality leads and conduct direct merchant visits.", 2),
        ("Build and maintain strong, lasting relationships with store owners.", 2),
        ("Assist merchants with app onboarding, menu setup & cataloging.", 2),
        ("Achieve weekly & monthly field onboarding targets.", 2),
        ("Collect market insights and report to growth managers.", 2)
    ]

    ry = c_top + 75
    for r, lines in resps:
        # Draw green checkmark badge
        draw.ellipse([75, ry + 2, 95, ry + 22], fill=(225, 245, 230))
        draw.text((80, ry + 1), "v", fill=(0, 150, 50), font=f_body_b)
        
        words = r.split()
        line1, line2 = "", ""
        for wd in words:
            if draw.textlength(line1 + " " + wd, font=f_body) < 380:
                line1 += " " + wd
            else:
                line2 += " " + wd
        draw.text((108, ry), line1.strip(), fill=(25, 35, 55), font=f_body)
        if line2:
            draw.text((108, ry + 26), line2.strip(), fill=(25, 35, 55), font=f_body)
            ry += 28
        ry += 42

    # RIGHT CARD: Eligibility & Requirements (Navy Theme)
    rx = 55 + card_w + 35
    draw.rounded_rectangle([rx, c_top, w - 55, c_top + c_h], radius=20, fill=(245, 248, 255), outline=(190, 215, 250), width=2)
    # Header
    draw.rounded_rectangle([rx, c_top, w - 55, c_top + 55], radius=20, fill=(11, 44, 115))
    draw.text((rx + 20, c_top + 14), "ELIGIBILITY & CRITERIA", fill=(255, 255, 255), font=f_card_title)

    reqs = [
        ("Language: TAMIL (Mandatory) -- Must speak fluently with merchants.", 2),
        ("Experience: 0 to 3 Years (Freshers with sales passion welcome!).", 2),
        ("Location: Chennai (Open to candidates across TN ready to relocate).", 2),
        ("Domain: Passion for on-ground field sales & merchant meetings.", 2),
        ("Mobility: Two-Wheeler (Bike/Scooter) + Valid Driving License.", 2),
        ("Joining: Immediate joiners or within 7 to 15 days strongly preferred.", 2),
        ("Benefits: Fixed Rs.25K+ /mo + High Monthly Incentives + PF & Insurance.", 2)
    ]

    eqy = c_top + 75
    for eq, lines in reqs:
        # Draw blue star badge
        draw.ellipse([rx + 20, eqy + 2, rx + 40, eqy + 22], fill=(220, 235, 255))
        draw.text((rx + 26, eqy + 1), "*", fill=(11, 44, 115), font=f_body_b)
        
        words = eq.split()
        line1, line2 = "", ""
        for wd in words:
            if draw.textlength(line1 + " " + wd, font=f_body) < 370:
                line1 += " " + wd
            else:
                line2 += " " + wd
        draw.text((rx + 52, eqy), line1.strip(), fill=(25, 35, 55), font=f_body)
        if line2:
            draw.text((rx + 52, eqy + 26), line2.strip(), fill=(25, 35, 55), font=f_body)
            eqy += 28
        eqy += 42

    # 6. Apply Button Banner (Middle Callout)
    btn_y = 1215
    btn_w = 440
    bx = (w - btn_w) // 2
    draw.rounded_rectangle([bx, btn_y, bx + btn_w, btn_y + 58], radius=29, fill=(255, 193, 7))
    btn_label = ">> APPLY NOW VIA GOOGLE FORM <<"
    draw.text(((w - draw.textlength(btn_label, font=f_btn)) // 2, btn_y + 16), btn_label, fill=(11, 44, 115), font=f_btn)

    # 7. Official Recruiter Contact Footer Bar (Mohamed Yasar)
    footer_top = 1295
    draw.rounded_rectangle([55, footer_top, w - 55, h - 35], radius=24, fill=(11, 44, 115))

    # Recruiter Profile Info
    draw.text((85, footer_top + 28), "HR RECRUITER CONTACT PERSON:", fill=(255, 193, 7), font=f_bar_sub)
    draw.text((85, footer_top + 58), "Mr. Mohamed Yasar", fill=(255, 255, 255), font=f_footer_name)
    draw.text((85, footer_top + 98), "Human Resources Executive - Recruitment", fill=(200, 225, 255), font=f_footer_sub)
    draw.text((85, footer_top + 130), "Daasho Technologies Private Limited | Chennai", fill=(180, 205, 240), font=ImageFont.truetype(font_reg, 18))

    # Phone & Email
    cx = 570
    draw.text((cx, footer_top + 42), "Phone / WhatsApp:", fill=(255, 193, 7), font=f_bar)
    draw.text((cx + 175, footer_top + 38), "+91 9787806366", fill=(255, 255, 255), font=f_footer_name)

    draw.text((cx, footer_top + 92), "Email:", fill=(255, 193, 7), font=f_bar)
    draw.text((cx + 65, footer_top + 92), "mohammedyasar7868908@gmail.com", fill=(255, 255, 255), font=f_bar)

    draw.text((cx, footer_top + 130), "Official Website: https://daasho.com", fill=(255, 215, 64), font=f_bar_sub)

    out_dir = "d:/infonix/daasho-recruitment-automation/creatives"
    out_path = os.path.join(out_dir, "Mohamed_Yasar_Daasho_BDE_Poster.jpg")
    img.convert("RGB").save(out_path, "JPEG", quality=95)
    print(f"[+] Successfully generated Mohamed Yasar's official Daasho BDE poster: {out_path}")

    # Copy to artifacts
    art_path = "C:/Users/HP/.gemini/antigravity/brain/f91a7f0c-1582-4970-902e-08ff240e2a61/mohamed_yasar_daasho_bde_poster.jpg"
    img.convert("RGB").save(art_path, "JPEG", quality=95)
    print(f"[+] Successfully saved to artifacts: {art_path}")

if __name__ == "__main__":
    generate_yasar_poster()
