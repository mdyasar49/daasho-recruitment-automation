import urllib.request
import re

url = "https://docs.google.com/spreadsheets/d/1kxEeoG4dVSXgl5qfDTHGf3LlyEPgMQjrlAjvWFzzZ28/edit"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    html = urllib.request.urlopen(req).read().decode('utf-8', errors='ignore')
    forms = re.findall(r'https://docs\.google\.com/forms/[^\s"\'<>]+', html)
    print("Found Google Forms links:", set(forms))
    
    # Also look for forms.gle
    forms_gle = re.findall(r'https://forms\.gle/[^\s"\'<>]+', html)
    print("Found forms.gle links:", set(forms_gle))

    # Look for any form IDs
    form_ids = re.findall(r'form[a-zA-Z0-9_\-]{20,}', html)
    print("Found form mentions:", set(form_ids[:10]))
except Exception as e:
    print("Error:", e)
