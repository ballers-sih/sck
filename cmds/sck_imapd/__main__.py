import imaplib
import smtplib
import os
import base64
import requests
import time
from email import message_from_bytes
from email import policy
from email.generator import BytesGenerator
import re
from email.message import EmailMessage
from io import BytesIO
from dotenv import load_dotenv


def convert_forwarded_email(msg):
    body = ""

    for part in msg.walk():
        if part.get_content_type() == "text/plain":
            body = part.get_content()
            break

    marker = "---------- Forwarded message ---------"

    if marker not in body:
        return None

    forwarded = body.split(marker, 1)[1]

    match = re.search(
        r"From:\s*(.+?)\r?\n"
        r"Date:\s*(.+?)\r?\n"
        r"Subject:\s*(.+?)\r?\n"
        r"To:\s*(.+?)\r?\n"
        r"\r?\n"
        r"(.*)",
        forwarded,
        re.DOTALL,
    )

    if not match:
        return None

    new_email = EmailMessage()

    new_email["From"] = match.group(1).strip().replace("\r", "").replace("\n", "")
    new_email["Date"] = match.group(2).strip().replace("\r", "").replace("\n", "")
    new_email["Subject"] = match.group(3).strip().replace("\r", "").replace("\n", "")
    new_email["To"] = match.group(4).strip().replace("\r", "").replace("\n", "")

    message = match.group(5).strip()

    new_email.set_content(message)

    html_message = message.replace("&", "&amp;")
    html_message = html_message.replace("<", "&lt;")
    html_message = html_message.replace(">", "&gt;")
    html_message = html_message.replace("\n", "<br>\n")

    new_email.add_alternative(
        f"<html><body>{html_message}</body></html>", subtype="html"
    )

    buffer = BytesIO()

    BytesGenerator(buffer, policy=policy.default).flatten(new_email)

    return buffer.getvalue()


load_dotenv(os.getcwd() + "/.env")

mail = imaplib.IMAP4_SSL("imap.gmail.com")
EMAIL_USER = os.environ["EMAIL_USER"]
EMAIL_PASS = os.environ["EMAIL_PASS"]
mail.login(EMAIL_USER, EMAIL_PASS)

mail.select("INBOX")

xdg_cache = os.environ.get("XDG_CACHE_HOME", os.path.expanduser("~/.cache"))
XDG_CACHE_DIR = os.path.join(xdg_cache, "sck_app")
os.makedirs(XDG_CACHE_DIR, exist_ok=True)

SCKD_ADDRESS = os.environ["SCKD_ADDRESS"]
SCKD_PORT = os.environ["SCKD_PORT"]
SCKD_URL = f"http://{SCKD_ADDRESS}:{SCKD_PORT}/submit"

idx = 0
while True:
    print("Checking Gmail...")

    status, messages = mail.search(None, "UNSEEN")
    print("Search status:", status)
    print("Raw messages:", messages)

    email_ids = messages[0].split()
    print("Unread emails:", email_ids)

    success_or_not = []

    for email_id in email_ids:
        print("current:", email_id)
        res, msg_data = mail.fetch(email_id, "(RFC822)")

        for response_part in msg_data:
            if isinstance(response_part, tuple):
                raw_email = response_part[1]
                msg = message_from_bytes(raw_email, policy=policy.default)

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
                    forwarded_eml = convert_forwarded_email(msg)

                    if forwarded_eml is not None:
                        original_eml = forwarded_eml
                    else:
                        original_eml = raw_email

                file_path = os.path.join(XDG_CACHE_DIR, f"email_{idx}.eml")

                with open(file_path, "wb") as f:
                    f.write(original_eml)

                with open(file_path, "rb") as f:
                    encoded = base64.b64encode(f.read()).decode("ascii")

                response = requests.post(
                    SCKD_URL, json={"content": encoded}, timeout=120
                )

                response.raise_for_status()

                print(f"Submitted email_{idx}.eml to sckd: ", response.status_code)
                result = response.json()
                report = result["report"]

                smtp_message = EmailMessage()
                try:
                    smtp_message["From"] = EMAIL_USER
                    smtp_message["To"] = msg["From"]
                    smtp_message["Subject"] = "Scam Check Report"
                    smtp_message.set_content(report)
                except Exception as e:
                    success_or_not.append("not")

                success_or_not.append("success")

                with smtplib.SMTP("smtp.gmail.com", 587, timeout=30) as smtp:
                    print('1')
                    smtp.starttls()
                    print('2')
                    smtp.login(EMAIL_USER, EMAIL_PASS)
                    print('3')
                    smtp.send_message(smtp_message)
                    print('4')

                print(f"Report sent to {msg['From']}")
                mail.store(email_id, "+FLAGS", "\\Seen")
                idx += 1

    time.sleep(5)
