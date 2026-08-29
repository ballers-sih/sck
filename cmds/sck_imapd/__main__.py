import imaplib
import os
from dotenv import load_dotenv

load_dotenv()

mail = imaplib.IMAP4_SSL("imap.gmail.com")
EMAIL_USER = os.environ.get("EMAIL_USER")
EMAIL_PASS = os.environ.get("EMAIL_PASS")
mail.login(EMAIL_USER, EMAIL_PASS)

mail.select("INBOX")

status, messages = mail.search(None, "ALL")
email_ids = messages[0].split()

xdg_cache = os.environ.get("XDG_CACHE_HOME", os.path.expanduser("~/.cache"))
XDG_CACHE_DIR = os.path.join(xdg_cache, "sck_app")
os.makedirs(XDG_CACHE_DIR, exist_ok=True) 

for idx, email_id in enumerate(email_ids):
    res, msg_data = mail.fetch(email_id, "(RFC822)")
    for response_part in msg_data:
        if isinstance(response_part, tuple):
            file_path = os.path.join(XDG_CACHE_DIR, f"email_{idx}.eml")
            with open(file_path, "wb") as f:
                f.write(response_part[1])

mail.logout()
