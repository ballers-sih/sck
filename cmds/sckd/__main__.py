import os
import base64
import json
import tempfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from dotenv import load_dotenv

from internal import parse_eml, scan_files, scan_url, roberta

HOST = os.environ["SCKD_ADDRESS"]
PORT = int(os.environ["SCKD_PORT"])


def scan_eml(data: bytes) -> tuple[bool, str]:
    email = parse_eml.parse_eml(data)

    url_results = []
    for url in email.message_links:
        try:
            status, result = scan_url.scan_url(url)
            url_results.append((url, status, result))
        except Exception as e:
            url_results.append((url, 1, {"error": str(e)}))

    attachment_results = []

    with tempfile.TemporaryDirectory() as tmpdir:
        paths = []

        for i, attachment in enumerate(email.attachments):
            try:
                data = base64.b64decode(attachment)
            except Exception as e:
                attachment_results.append(
                    {
                        "file": f"attachment-{i}",
                        "error": f"invalid base64: {e}",
                    }
                )
                continue

            path = f"{tmpdir}/attachment-{i}"
            with open(path, "wb") as file:
                file.write(data)

            paths.append(path)

        attachment_results = scan_files.scan_files(paths)

    try:
        roberta_result = roberta.scan_email(
            email.subject,
            email.message,
        )
    except Exception as e:
        roberta_result = {
            "error": str(e),
        }

    scam = False

    for result in attachment_results:
        status, report = result
        if status == 0 and report.get("malicious") is True:
            scam = True

    for _, status, result in url_results:
        if status == 0:
            if result.get("malicious", 0) > 2:
                scam = True
            elif result.get("suspicious", 0) > 2:
                scam = True

    if roberta_result.get("fraud") is True:
        scam = True

    report_lines = [
        f"From: {email.sender}",
        f"Subject: {email.subject}",
        "",
        "=== Message classifier ===",
    ]

    if "error" in roberta_result:
        report_lines.append(f"Error: {roberta_result['error']}")
    else:
        report_lines.append(f"Fraud: {roberta_result['fraud']}")
        report_lines.append(
            f"Fraud probability: " f"{roberta_result['fraud_probability']:.4f}"
        )
        report_lines.append(
            f"Normal probability: " f"{roberta_result['normal_probability']:.4f}"
        )

    report_lines.append("")
    report_lines.append("=== URLs ===")

    if not url_results:
        report_lines.append("No URLs found.")

    for url, status, result in url_results:
        report_lines.append(f"{url}")

        if status != 0:
            report_lines.append(f"  Error: {result.get('error', 'scan failed')}")
            continue

        report_lines.append(f"  Malicious: {result.get('malicious', 0)}")
        report_lines.append(f"  Suspicious: {result.get('suspicious', 0)}")
        report_lines.append(f"  Harmless: {result.get('harmless', 0)}")
        report_lines.append(f"  Undetected: {result.get('undetected', 0)}")

    report_lines.append("")
    report_lines.append("=== Attachments ===")

    if not attachment_results:
        report_lines.append("No attachments found.")

    for status, result in attachment_results:
        filename = result.get("file", "unknown")
        report_lines.append(filename)

        if status != 0:
            report_lines.append(f"  Error: {result.get('error', 'scan failed')}")
        else:
            report_lines.append(f"  Malicious: {result.get('malicious', False)}")

    report_lines.append("")
    report_lines.append(f"=== RESULT: {'SCAM' if scam else 'CLEAN'} ===")

    return scam, "\n".join(report_lines)


class SCKHandler(BaseHTTPRequestHandler):
    def send_json(self, status: int, data: dict) -> None:
        body = json.dumps(data).encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()

        self.wfile.write(body)

    def do_POST(self) -> None:
        if self.path != "/submit":
            self.send_json(
                404,
                {"error": "not found"},
            )
            return

        content_length = self.headers.get("Content-Length")

        if content_length is None:
            self.send_json(
                400,
                {"error": "missing Content-Length"},
            )
            return

        try:
            length = int(content_length)
            body = self.rfile.read(length)
            request = json.loads(body)

            content = request["content"]
            if not isinstance(content, str):
                raise ValueError("content must be a string")

            eml = base64.b64decode(
                content,
                validate=True,
            )
        except (ValueError, KeyError, json.JSONDecodeError) as e:
            self.send_json(
                400,
                {"error": str(e)},
            )
            return

        try:
            scam, report = scan_eml(eml)
        except Exception as e:
            self.send_json(
                500,
                {"error": str(e)},
            )
            return

        self.send_json(
            200,
            {
                "scam": scam,
                "report": report,
            },
        )

    def do_GET(self) -> None:
        self.send_json(
            404,
            {"error": "not found"},
        )

    def log_message(self, format: str, *args: object) -> None:
        print(format % args)


def main() -> None:
    load_dotenv()

    server = ThreadingHTTPServer(
        (HOST, PORT),
        SCKHandler,
    )

    print(f"sckd listening on {HOST}:{PORT}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
