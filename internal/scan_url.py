import base64
import os
import sys
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import json

VT_API = "https://www.virustotal.com/api/v3"


def _vt_url_id(url: str) -> str:
    return (
        base64.urlsafe_b64encode(url.encode())
        .decode()
        .rstrip("=")
    )


def _get_vt(path: str) -> dict:
    api_key = os.environ["VT_API_KEY"]

    request = Request(
        f"{VT_API}{path}",
        headers={"x-apikey": api_key},
    )

    with urlopen(request, timeout=10) as response:
        return json.load(response)


def scan_url(url: str) -> tuple:
    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise ValueError(f"invalid URL: {url}")

    url_id = _vt_url_id(url)

    try:
        url_data = _get_vt(f"/urls/{url_id}")["data"]["attributes"]
    except HTTPError as e:
        if e.code == 404:
            return 1, {}
        raise

    stats = url_data.get("last_analysis_stats", {})

    return 0, {
        "malicious": stats["malicious"],
        "suspicious": stats["suspicious"],
        "harmless": stats["harmless"],
        "undetected": stats["undetected"],
    }


if __name__ == "__main__":
    url = sys.argv[1]
    print(scan_url(url))
