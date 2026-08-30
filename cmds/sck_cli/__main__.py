import argparse
import base64
import json
import os
import urllib.error
import urllib.request
from dotenv import load_dotenv


def submit_email(file_path):
    # Read the .eml file
    with open(file_path, "rb") as file:
        email_data = file.read()

    # Convert the email to Base64
    encoded_email = base64.b64encode(email_data).decode("ascii")

    # Create the JSON payload
    payload = {"content": encoded_email}

    # Get the sckd address and port
    address = os.environ["SCKD_ADDRESS"]
    port = os.environ["SCKD_PORT"]

    url = f"http://{address}:{port}/submit"

    # Convert the payload to JSON bytes
    data = json.dumps(payload).encode("utf-8")

    # Create the POST request
    request = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}, method="POST"
    )

    # Send the request
    with urllib.request.urlopen(request) as response:
        response_data = response.read()

    # Convert the response from JSON to a Python dictionary
    return json.loads(response_data.decode("utf-8"))


def main():
    load_dotenv()

    parser = argparse.ArgumentParser(description="Submit an .eml file to sckd.")

    parser.add_argument("file", help="Path to the .eml file")

    args = parser.parse_args()

    try:
        result = submit_email(args.file)

        print("Scam:", result["scam"])
        print()
        print("Report:")
        print(result["report"])

    except FileNotFoundError:
        print(f"Error: file not found: {args.file}")

    except urllib.error.URLError as error:
        print(f"Error: could not connect to sckd: {error}")

    except Exception as error:
        print(f"Error: {error}")


if __name__ == "__main__":
    main()
