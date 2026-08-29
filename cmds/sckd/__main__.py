import sys
import base64
import json
import os
import urllib.error
import urllib.request

from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QFileDialog,
    QTextEdit,
)


def submit_email(file_path):
    # Read the .eml file
    with open(file_path, "rb") as file:
        email_data = file.read()

    # Convert the email to Base64
    encoded_email = base64.b64encode(email_data).decode("ascii")

    # Create the JSON payload
    payload = {
        "content": encoded_email
    }

    # Get the sckd address and port
    address = os.getenv("SCKD_ADDRESS", "127.0.0.1")
    port = os.getenv("SCKD_PORT", "8000")

    url = f"http://{address}:{port}/submit"

    # Convert the payload to JSON bytes
    data = json.dumps(payload).encode("utf-8")

    # Create the POST request
    request = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json"
        },
        method="POST"
    )

    # Send the request
    with urllib.request.urlopen(request) as response:
        response_data = response.read()

    # Convert the response to a Python dictionary
    return json.loads(response_data.decode("utf-8"))


def main():
    app = QApplication(sys.argv)

    window = QWidget()
    window.setWindowTitle("Scam Check")
    window.resize(700, 500)

    layout = QVBoxLayout()

    title = QLabel("Scam Check")
    layout.addWidget(title)

    file_label = QLabel("No file selected")
    layout.addWidget(file_label)

    browse_button = QPushButton("Browse")
    layout.addWidget(browse_button)

    check_button = QPushButton("Check Email")
    layout.addWidget(check_button)

    result_label = QLabel("Result: Not checked")
    layout.addWidget(result_label)

    report_box = QTextEdit()
    report_box.setReadOnly(True)
    layout.addWidget(report_box)

    selected_file = None

    def choose_file():
        nonlocal selected_file

        file_path, _ = QFileDialog.getOpenFileName(
            window,
            "Select an email file",
            "",
            "Email files (*.eml)"
        )

        if file_path:
            selected_file = file_path
            file_label.setText(file_path)
            result_label.setText("Result: Not checked")
            report_box.clear()

    browse_button.clicked.connect(choose_file)

    def check_email():
        if selected_file is None:
            result_label.setText("Result: Please select an .eml file first.")
            return

        try:
            result = submit_email(selected_file)

            scam = result["scam"]
            report = result["report"]

            if scam:
                result_label.setText("Result: SCAM")
            else:
                result_label.setText("Result: CLEAN")

            report_box.setText(report)

        except FileNotFoundError:
            result_label.setText("Error: File not found.")
            report_box.clear()

        except urllib.error.URLError as error:
            result_label.setText("Error: Could not connect to sckd.")
            report_box.setText(str(error))

        except Exception as error:
            result_label.setText("Error")
            report_box.setText(str(error))

    check_button.clicked.connect(check_email)

    window.setLayout(layout)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()