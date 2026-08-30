import sys
import base64
import json
import os
import urllib.error
import urllib.request

from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


# =====================================================
# Communication with sckd
# =====================================================

def submit_email(file_path):
    # Read the .eml file
    with open(file_path, "rb") as file:
        email_data = file.read()

    # Convert email to Base64
    encoded_email = base64.b64encode(email_data).decode("ascii")

    # Create JSON payload
    payload = {
        "content": encoded_email
    }

    # Get sckd address and port
    address = os.getenv("SCKD_ADDRESS", "127.0.0.1")
    port = os.getenv("SCKD_PORT", "8000")

    url = f"http://{address}:{port}/submit"

    # Convert payload to JSON bytes
    data = json.dumps(payload).encode("utf-8")

    # Create POST request
    request = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json"
        },
        method="POST"
    )

    # Send request
    with urllib.request.urlopen(request) as response:
        response_data = response.read()

    # Convert response to Python dictionary
    return json.loads(response_data.decode("utf-8"))


# =====================================================
# Worker thread
# =====================================================

class ScanWorker(QThread):

    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, file_path):
        super().__init__()

        self.file_path = file_path

    def run(self):
        try:
            result = submit_email(self.file_path)

            self.finished.emit(result)

        except FileNotFoundError:
            self.error.emit("File not found.")

        except urllib.error.URLError as error:
            self.error.emit(
                f"Could not connect to sckd.\n\n{error}"
            )

        except Exception as error:
            self.error.emit(str(error))


# =====================================================
# Main GUI
# =====================================================

def main():

    app = QApplication(sys.argv)

    # -------------------------------------------------
    # Main window
    # -------------------------------------------------

    window = QWidget()

    window.setWindowTitle("Scam Check")

    window.resize(900, 700)

    window.setStyleSheet("""
        QWidget {
            background-color: #0f172a;
            color: #e2e8f0;
            font-family: "Segoe UI";
        }

        QFrame#card {
            background-color: #1e293b;
            border-radius: 12px;
        }

        QLabel#title {
            font-size: 28px;
            font-weight: bold;
            color: #f8fafc;
        }

        QLabel#subtitle {
            font-size: 14px;
            color: #94a3b8;
        }

        QLabel#section_title {
            font-size: 13px;
            font-weight: bold;
            color: #94a3b8;
        }

        QLabel#file_label {
            background-color: #0f172a;
            border-radius: 8px;
            padding: 12px;
            color: #cbd5e1;
        }

        QPushButton {
            border: none;
            border-radius: 8px;
            padding: 11px 20px;
            font-size: 14px;
            font-weight: bold;
        }

        QPushButton#browse_button {
            background-color: #334155;
            color: #f8fafc;
        }

        QPushButton#browse_button:hover {
            background-color: #475569;
        }

        QPushButton#check_button {
            background-color: #2563eb;
            color: white;
            padding: 13px;
        }

        QPushButton#check_button:hover {
            background-color: #1d4ed8;
        }

        QPushButton#check_button:disabled {
            background-color: #475569;
            color: #94a3b8;
        }

        QLabel#result {
            background-color: #0f172a;
            border-radius: 8px;
            padding: 16px;
            font-size: 20px;
            font-weight: bold;
        }

        QLabel#email_info {
            background-color: #0f172a;
            border-radius: 8px;
            padding: 14px;
            color: #cbd5e1;
            font-size: 13px;
        }

        QTextEdit {
            background-color: #0f172a;
            border: none;
            border-radius: 8px;
            padding: 12px;
            color: #cbd5e1;
            font-size: 13px;
        }
    """)

    # -------------------------------------------------
    # Main layout
    # -------------------------------------------------

    main_layout = QVBoxLayout()

    main_layout.setContentsMargins(
        35, 30, 35, 30
    )

    main_layout.setSpacing(18)

    # -------------------------------------------------
    # Header
    # -------------------------------------------------

    title = QLabel("SCAM CHECK")

    title.setObjectName("title")

    subtitle = QLabel(
        "Analyze suspicious emails for scams, "
        "malicious links and attachments."
    )

    subtitle.setObjectName("subtitle")

    main_layout.addWidget(title)

    main_layout.addWidget(subtitle)

    # -------------------------------------------------
    # File selection card
    # -------------------------------------------------

    file_card = QFrame()

    file_card.setObjectName("card")

    file_layout = QVBoxLayout()

    file_layout.setContentsMargins(
        20, 20, 20, 20
    )

    file_layout.setSpacing(12)

    file_section_title = QLabel("EMAIL FILE")

    file_section_title.setObjectName(
        "section_title"
    )

    file_layout.addWidget(
        file_section_title
    )

    file_row = QHBoxLayout()

    file_row.setSpacing(10)

    file_label = QLabel(
        "No file selected"
    )

    file_label.setObjectName(
        "file_label"
    )

    file_label.setAlignment(
        Qt.AlignmentFlag.AlignVCenter
    )

    browse_button = QPushButton("Browse")

    browse_button.setObjectName(
        "browse_button"
    )

    file_row.addWidget(
        file_label,
        1
    )

    file_row.addWidget(
        browse_button
    )

    file_layout.addLayout(file_row)

    file_card.setLayout(file_layout)

    main_layout.addWidget(file_card)

    # -------------------------------------------------
    # Check button
    # -------------------------------------------------

    check_button = QPushButton(
        "CHECK EMAIL"
    )

    check_button.setObjectName(
        "check_button"
    )

    main_layout.addWidget(
        check_button
    )

    # -------------------------------------------------
    # Analysis result card
    # -------------------------------------------------

    result_card = QFrame()

    result_card.setObjectName(
        "card"
    )

    result_layout = QVBoxLayout()

    result_layout.setContentsMargins(
        20, 20, 20, 20
    )

    result_layout.setSpacing(12)

    result_section_title = QLabel(
        "ANALYSIS RESULT"
    )

    result_section_title.setObjectName(
        "section_title"
    )

    result_layout.addWidget(
        result_section_title
    )

    # Main result
    result_label = QLabel(
        "Not checked"
    )

    result_label.setObjectName(
        "result"
    )

    result_label.setAlignment(
        Qt.AlignmentFlag.AlignCenter
    )

    result_layout.addWidget(
        result_label
    )

    # Email information
    email_info = QLabel(
        "No email analyzed yet."
    )

    email_info.setObjectName(
        "email_info"
    )

    email_info.setWordWrap(True)

    result_layout.addWidget(
        email_info
    )

    # Detailed report
    report_box = QTextEdit()

    report_box.setReadOnly(True)

    result_layout.addWidget(
        report_box,
        1
    )

    result_card.setLayout(
        result_layout
    )

    main_layout.addWidget(
        result_card,
        1
    )

    # -------------------------------------------------
    # State
    # -------------------------------------------------

    selected_file = None

    worker = None

    # -------------------------------------------------
    # Browse button
    # -------------------------------------------------

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

            file_label.setText(
                file_path
            )

            result_label.setText(
                "Not checked"
            )

            result_label.setStyleSheet("")

            email_info.setText(
                "No email analyzed yet."
            )

            report_box.clear()

    browse_button.clicked.connect(
        choose_file
    )

    # -------------------------------------------------
    # Scan completed
    # -------------------------------------------------

    def scan_finished(result):

        nonlocal worker

        scam = result["scam"]

        report = result["report"]

        # ---------------------------------------------
        # Display result
        # ---------------------------------------------

        if scam:

            result_label.setText(
                "⚠  SCAM DETECTED"
            )

            result_label.setStyleSheet("""
                background-color: #450a0a;
                color: #fca5a5;
                border-radius: 8px;
                padding: 16px;
                font-size: 20px;
                font-weight: bold;
            """)

        else:

            result_label.setText(
                "✓  EMAIL APPEARS CLEAN"
            )

            result_label.setStyleSheet("""
                background-color: #052e16;
                color: #86efac;
                border-radius: 8px;
                padding: 16px;
                font-size: 20px;
                font-weight: bold;
            """)

        # ---------------------------------------------
        # Extract basic email information
        # ---------------------------------------------

        sender = "Unknown"

        subject = "Unknown"

        for line in report.splitlines():

            if line.startswith("From:"):

                sender = line[5:].strip()

            elif line.startswith("Subject:"):

                subject = line[8:].strip()

        email_info.setText(
            f"<b>Sender:</b> {sender}<br>"
            f"<b>Subject:</b> {subject}"
        )

        # ---------------------------------------------
        # Display report
        # ---------------------------------------------

        report_box.setText(
            report
        )

        # ---------------------------------------------
        # Restore button
        # ---------------------------------------------

        check_button.setEnabled(
            True
        )

        browse_button.setEnabled(
            True
        )

        check_button.setText(
            "CHECK EMAIL"
        )

        worker = None

    # -------------------------------------------------
    # Scan error
    # -------------------------------------------------

    def scan_error(message):

        nonlocal worker

        result_label.setText(
            "⚠  SCAN ERROR"
        )

        result_label.setStyleSheet("""
            background-color: #451a03;
            color: #fdba74;
            border-radius: 8px;
            padding: 16px;
            font-size: 20px;
            font-weight: bold;
        """)

        email_info.setText(
            "The email could not be analyzed."
        )

        report_box.setText(
            message
        )

        check_button.setEnabled(
            True
        )

        browse_button.setEnabled(
            True
        )

        check_button.setText(
            "CHECK EMAIL"
        )

        worker = None

    # -------------------------------------------------
    # Check button
    # -------------------------------------------------

    def check_email():

        nonlocal worker

        if selected_file is None:

            result_label.setText(
                "Please select an .eml file first."
            )

            email_info.setText(
                ""
            )

            report_box.clear()

            return

        # ---------------------------------------------
        # Update UI while scanning
        # ---------------------------------------------

        check_button.setEnabled(
            False
        )

        browse_button.setEnabled(
            False
        )

        check_button.setText(
            "ANALYZING EMAIL..."
        )

        result_label.setText(
            "🔄  ANALYZING EMAIL..."
        )

        result_label.setStyleSheet("""
            background-color: #172554;
            color: #93c5fd;
            border-radius: 8px;
            padding: 16px;
            font-size: 20px;
            font-weight: bold;
        """)

        email_info.setText(
            "Scam Check is analyzing this email..."
        )

        report_box.clear()

        # ---------------------------------------------
        # Start worker thread
        # ---------------------------------------------

        worker = ScanWorker(
            selected_file
        )

        worker.finished.connect(
            scan_finished
        )

        worker.error.connect(
            scan_error
        )

        worker.start()

    check_button.clicked.connect(
        check_email
    )

    # -------------------------------------------------
    # Show window
    # -------------------------------------------------

    window.setLayout(
        main_layout
    )

    window.show()

    sys.exit(
        app.exec()
    )


if __name__ == "__main__":
    main()