import os
import json
import base64
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import tempfile
from dotenv import load_dotenv

from internal import parse_eml, roberta, scan_files, scan_url


def scan_eml(data: bytes) -> tuple[bool, str]:
    email = parse_eml.parse_eml(data)

    url_results = list()
    for url in email.message_links:
        try:
            status, result = scan_url.scan_url(url)
            url_results.append((url, status, result))
        except Exception as e:
            url_results.append((url, 1, {"error": str(e)}))

    attachment_results = list()
    with tempfile.TemporaryDirectory() as tmpdir:
        paths = list()
        for i, attachment in enumerate(email.attachments):
            try:
                data = base64.b64decode(attachment)
            except Exception as e:
                attachment_results.append(
                    (1, {"file": f"attachment-{i}", "error": f"invalid base64: {e}"})
                )
                continue

            path = f"{tmpdir}/attachment-{i}"
            with open(path, "wb") as file:
                file.write(data)
            paths.append(path)
        attachment_results = scan_files.scan_files(paths)

    try:
        roberta_result = roberta.scan_email(email.subject, email.message)
    except Exception as e:
        roberta_result = {"error": str(e)}

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

    report_lines = list()

    report_lines.append(f"Result: {"SCAM" if scam else "CLEAN"}")

    report_lines.append("")
    report_lines.append("AI Classifier:")

    if "error" in roberta_result:
        report_lines.append(f"\tError: {roberta_result["error"]}")
    else:
        report_lines.append(f"\tFraud: {roberta_result["fraud"]}")
        report_lines.append(
            f"\tFraud probability: {roberta_result["fraud_probability"] * 100}%"
        )

    report_lines.append("")
    report_lines.append("URLs:")

    if not url_results:
        report_lines.append("\tNo URLs found")

    for url, status, result in url_results:
        report_lines.append(f"\t{url}")

        if status != 0:
            report_lines.append(f"\t\tError: {result.get("error", "scan failed")}")
            continue

        report_lines.append(f"\t\tMalicious: {result.get('malicious', 0)}")
        report_lines.append(f"\t\tSuspicious: {result.get('suspicious', 0)}")
        report_lines.append(f"\t\tHarmless: {result.get('harmless', 0)}")
        report_lines.append(f"\t\tUndetected: {result.get('undetected', 0)}")

    report_lines.append("")
    report_lines.append("Attachments:")

    if not attachment_results:
        report_lines.append("\tNo attachments found.")

    for status, result in attachment_results:
        filename = result.get("file", "unknown")
        report_lines.append(f"\t{filename}")

        if status != 0:
            report_lines.append(f"\t\tError: {result.get('error', 'scan failed')}")
        else:
            report_lines.append(f"\t\tMalicious: {result.get('malicious', False)}")

    report_lines.append("")
    report_lines.append(f"From: {email.sender}")
    report_lines.append(f"Subject: {email.subject}")
    report_lines.append("")
    report_lines.append(f"Result: {"SCAM" if scam else "CLEAN"}")

    return scam, "\n".join(report_lines)


class sckdRequestHandler(BaseHTTPRequestHandler):
    def send_json(self, status: int, data: dict) -> None:
        body = json.dumps(data).encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()

        self.wfile.write(body)

    def do_POST(self) -> None:
        if self.path != "/submit":
            self.send_json(404, {"error": "not found"})
            return

        content_length = self.headers.get("Content-Length")

        if content_length is None:
            self.send_json(400, {"error": "missing content length"})
            return

        try:
            length = int(content_length)
            body = self.rfile.read(length)
            request = json.loads(body)

            content = request["content"]
            if not isinstance(content, str):
                raise ValueError("content must be a string")

            eml = base64.b64decode(content, validate=True)
        except (ValueError, KeyError, json.JSONDecodeError) as e:
            self.send_json(400, {"error": str(e)})
            return

        try:
            scam, report = scan_eml(eml)
        except Exception as e:
            self.send_json(500, {"error": str(e)})
            return

        self.send_json(200, {"scam": scam, "report": report})

    def do_GET(self) -> None:
        self.send_json(404, {"error": "not found"})


def main():
    load_dotenv()

    keys = ["VT_API_KEY", "SCKD_ADDRESS", "SCKD_PORT"]
    ENV = dict(zip(keys, map(lambda k: os.environ[k], keys)))

    server = ThreadingHTTPServer(
        (ENV["SCKD_ADDRESS"], int(ENV["SCKD_PORT"])), sckdRequestHandler
    )
    print(f"sckd listening on {ENV["SCKD_ADDRESS"]}:{ENV["SCKD_PORT"]}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
