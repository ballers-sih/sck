import os
import sys
import subprocess
from pathlib import Path


def scan_file(path: str) -> tuple[int, dict]:
    file = Path(path)

    if not file.is_file():
        return 1, {
            "file": str(path),
            "error": "file does not exist",
        }

    try:
        result = subprocess.run(
            ["clamscan", "--no-summary", "--database", os.environ["CLAMAV_DB"], str(path)],
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        return 1, {
            "file": str(path),
            "error": "clamscan not found",
        }

    # clamscan exit status:
    # 0 = clean
    # 1 = malicious
    # 2 = error
    if result.returncode == 0:
        return 0, {
            "file": str(path),
            "malicious": False,
        }

    if result.returncode == 1:
        return 0, {
            "file": str(path),
            "malicious": True,
        }

    return 1, {
        "file": str(path),
        "error": result.stderr.strip() or "clamscan failed",
    }


def scan_files(paths: list[str]) -> list[tuple[int, dict]]:
    return [scan_file(path) for path in paths]


def main():
    for result in scan_files(sys.argv[1:]):
        print(result)


if __name__ == "__main__":
    main()
