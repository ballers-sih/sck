from dataclasses import dataclass
from email import policy
from email.parser import BytesParser
from base64 import b64encode
import re
import sys

@dataclass
class ParsedEmail:
    sender: str
    message: str
    message_links: list[str]
    attachments: list[str]


def parse_eml(data: bytes) -> ParsedEmail:
    email = BytesParser(policy=policy.default).parsebytes(data)

    sender = email.get("From", "")
    message_parts = []
    links = []
    attachments = []

    for part in email.walk():
        if part.is_multipart():
            continue

        content_type = part.get_content_type()
        disposition = part.get_content_disposition()

        if disposition == "attachment":
            payload = part.get_payload(decode=True)
            if isinstance(payload, bytes):
                attachments.append(b64encode(payload).decode("ascii"))
            continue

        if content_type == "text/plain":
            message_parts.append(part.get_content())
        elif content_type == "text/html":
            html = part.get_content()
            message_parts.append(html)
            links.extend(extract_links(html))

    return ParsedEmail(
        sender=sender,
        message="\n".join(message_parts),
        message_links=list(dict.fromkeys(links)),
        attachments=attachments,
    )


def extract_links(html: str) -> list[str]:
    return re.findall(
        r"https?://[^\s\"'<>]+",
        html,
    )

if __name__ == "__main__":
    path = sys.argv[1]
    with open(path, "rb") as file:
        data = file.read()

    print(parse_eml(data))
