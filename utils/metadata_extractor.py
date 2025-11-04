import re

def extract_email_phone_location(text):
    email = None
    phone = None
    location = None

    
    email_match = re.search(r'[\w\.-]+@[\w\.-]+', text)
    if email_match:
        email = email_match.group(0)

    
    phone_match = re.search(r'(\+?\d{1,3})?[\s\-]?\(?\d{3,4}\)?[\s\-]?\d{3,4}[\s\-]?\d{3,4}', text)
    if phone_match:
        phone = phone_match.group(0)

    
    location_match = re.search(r'(Location|Address)\s*[:\-]?\s*(.+)', text, re.IGNORECASE)
    if location_match:
        location = location_match.group(2).split('\n')[0]

    return email or "-", phone or "-", location or "-"
