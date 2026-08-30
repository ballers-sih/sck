import imaplib
import os
import base64
import requests
from email import message_from_bytes
from email import policy
from email.generator import BytesGenerator
from io import BytesIO
from dotenv import load_dotenv

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
ENV_PATH = os.path.join(PROJECT_ROOT, ".env")
load_dotenv(dotenv_path=ENV_PATH)

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

SCKD_ADDRESS = os.getenv("SCKD_ADDRESS", "127.0.0.1")
SCKD_PORT = os.getenv("SCKD_PORT", "8000")
SCKD_URL = f"http://{SCKD_ADDRESS}:{SCKD_PORT}/submit"

for idx, email_id in enumerate(email_ids):
    res, msg_data = mail.fetch(email_id, "(RFC822)")
    for response_part in msg_data:
        if isinstance(response_part, tuple):
            msg = message_from_bytes(response_part[1], policy=policy.default)
            original_eml = None

            for part in msg.walk():
                filename = part.get_filename()
                if (
                    part.get_content_type() == "message/rfc822"
                    or part.get_content_type() == "application/rfc822"
                    or (filename and filename.lower().endswith(".eml"))
                ):
                    payload = part.get_payload()
                    if isinstance(payload, list) and payload:
                        nested_msg = payload[0]
                        buffer = BytesIO()
                        BytesGenerator(buffer, policy=policy.default).flatten(
                            nested_msg
                        )
                        original_eml = buffer.getvalue()
                    else:
                        original_eml = part.get_payload(decode=True)
                    break

            if original_eml is None:
                print(f"No .eml attachment found in email_{idx}")
                original_eml = response_part[1]

            file_path = os.path.join(XDG_CACHE_DIR, f"email_{idx}.eml")
            with open(file_path, "wb") as f:
                f.write(original_eml)
            with open(file_path, "rb") as f:
                encoded = base64.b64encode(f.read()).decode("ascii")
            response = requests.post(SCKD_URL, json={"content": encoded}, timeout=120)

            response.raise_for_status()

            print(f"Submitted email_{idx}.eml to sckd: ", f"{response.status_code}")
mail.logout()
