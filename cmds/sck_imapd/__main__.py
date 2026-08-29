import imaplib
import os

mail = imaplib.IMAP4_SSL("imap.gmail.com")
mail.login("scamchecke@gmail.com", "qyeg tqtv llyu mfmm")


mail.select("INBOX")

status, messages = mail.search(None, "ALL")
email_ids = messages[0].split()

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SCKD_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", "sckd"))

for idx, email_id in enumerate(email_ids):
    res, msg_data = mail.fetch(email_id, "(RFC822)")
    for response_part in msg_data:
        if isinstance(response_part, tuple):
            file_path = os.path.join(SCKD_DIR, f"email_{idx}.eml")
            with open(file_path, "wb") as f:
                f.write(response_part[1])

mail.logout()
