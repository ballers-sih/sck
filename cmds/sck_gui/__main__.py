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


# ============================================================
# COMMUNICATE WITH SCKD
# ============================================================

def submit_email(file_path):
    """
    Read an .eml file, convert it to Base64,
    send it to sckd, and return the response.
    """

    with open(file_path, "rb") as file:
        email_data = file.read()

    encoded_email = base64.b64encode(
        email_data
    ).decode("ascii")

    payload = {
        "content": encoded_email
    }

    address = os.getenv(
        "SCKD_ADDRESS",
        "127.0.0.1"
    )

    port = os.getenv(
        "SCKD_PORT",
        "8000"
    )

    url = f"http://{address}:{port}/submit"

    data = json.dumps(
        payload
    ).encode("utf-8")

    request = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json"
        },
        method="POST"
    )

    with urllib.request.urlopen(
        request
    ) as response:

        response_data = response.read()

    return json.loads(
        response_data.decode("utf-8")
    )


# ============================================================
# WORKER THREAD
# ============================================================

class ScanWorker(QThread):

    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, file_path):

        super().__init__()

        self.file_path = file_path

    def run(self):

        try:

            result = submit_email(
                self.file_path
            )

            self.finished.emit(
                result
            )

        except FileNotFoundError:

            self.error.emit(
                "The selected file could not be found."
            )

        except urllib.error.URLError as error:

            self.error.emit(
                f"Could not connect to sckd.\n\n{error}"
            )

        except Exception as error:

            self.error.emit(
                str(error)
            )


# ============================================================
# MAIN GUI
# ============================================================

def main():

    app = QApplication(
        sys.argv
    )

    window = QWidget()

    window.setWindowTitle(
        "Scam Check"
    )

    window.resize(
        950,
        750
    )

    window.setMinimumSize(
        750,
        600
    )

    # ========================================================
    # STYLES
    # ========================================================

    window.setStyleSheet("""
        /* ================================
        NORD THEME
        ================================ */

        QWidget {
            background-color: #2E3440;
            color: #ECEFF4;
            font-family: "Segoe UI";
        }

        /* ---------- HEADER ---------- */

        QLabel#title {
            font-size: 30px;
            font-weight: bold;
            color: #ECEFF4;
        }

        QLabel#subtitle {
            font-size: 14px;
            color: #D8DEE9;
        }

        QLabel#section_title {
            font-size: 13px;
            font-weight: bold;
            color: #88C0D0;
        }

        /* ---------- CARDS ---------- */

        QFrame#card {
            background-color: #3B4252;
            border-radius: 12px;
        }

        /* ---------- FILE ---------- */

        QLabel#file_label {
            background-color: #2E3440;
            border-radius: 8px;
            padding: 12px;
            color: #D8DEE9;
        }

        /* ---------- BUTTONS ---------- */

        QPushButton {
            border: none;
            border-radius: 8px;
            padding: 11px 20px;
            font-size: 14px;
            font-weight: bold;
        }

        QPushButton#browse_button {
            background-color: #4C566A;
            color: #ECEFF4;
        }

        QPushButton#browse_button:hover {
            background-color: #5E81AC;
        }

        QPushButton#check_button {
            background-color: #5E81AC;
            color: #ECEFF4;
            padding: 14px;
            font-size: 15px;
        }

        QPushButton#check_button:hover {
            background-color: #81A1C1;
        }

        QPushButton#check_button:disabled {
            background-color: #4C566A;
            color: #D8DEE9;
        }

        QPushButton#clear_button {
            background-color: #4C566A;
            color: #ECEFF4;
        }

        QPushButton#clear_button:hover {
            background-color: #5E81AC;
        }

        QPushButton#clear_button:disabled {
            color: #616A7D;
        }

        /* ---------- RESULT ---------- */

        QLabel#result {
            background-color: #2E3440;
            border-radius: 8px;
            padding: 18px;
            font-size: 21px;
            font-weight: bold;
            color: #ECEFF4;
        }

        QLabel#email_info {
            background-color: #2E3440;
            border-radius: 8px;
            padding: 14px;
            color: #D8DEE9;
            font-size: 13px;
        }

        QTextEdit {
            background-color: #2E3440;
            border: none;
            border-radius: 8px;
            padding: 12px;
            color: #D8DEE9;
            font-size: 13px;
        }

        QTextEdit:focus {
            border: 1px solid #88C0D0;
        }
    """)

    # ========================================================
    # MAIN LAYOUT
    # ========================================================

    main_layout = QVBoxLayout()

    main_layout.setContentsMargins(
        35,
        30,
        35,
        30
    )

    main_layout.setSpacing(
        18
    )

    # ========================================================
    # HEADER
    # ========================================================

    title = QLabel(
        "SCAM CHECK"
    )

    title.setObjectName(
        "title"
    )

    subtitle = QLabel(
        "Analyze suspicious emails for scams, "
        "malicious links and attachments."
    )

    subtitle.setObjectName(
        "subtitle"
    )

    main_layout.addWidget(
        title
    )

    main_layout.addWidget(
        subtitle
    )

    # ========================================================
    # FILE CARD
    # ========================================================

    file_card = QFrame()

    file_card.setObjectName(
        "card"
    )

    file_layout = QVBoxLayout()

    file_layout.setContentsMargins(
        20,
        20,
        20,
        20
    )

    file_layout.setSpacing(
        12
    )

    file_title = QLabel(
        "EMAIL FILE"
    )

    file_title.setObjectName(
        "section_title"
    )

    file_layout.addWidget(
        file_title
    )

    file_row = QHBoxLayout()

    file_row.setSpacing(
        10
    )

    file_label = QLabel(
        "No .eml file selected"
    )

    file_label.setObjectName(
        "file_label"
    )

    file_label.setWordWrap(
        True
    )

    browse_button = QPushButton(
        "Browse"
    )

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

    file_layout.addLayout(
        file_row
    )

    file_card.setLayout(
        file_layout
    )

    main_layout.addWidget(
        file_card
    )

    # ========================================================
    # BUTTONS
    # ========================================================

    button_row = QHBoxLayout()

    button_row.setSpacing(
        10
    )

    check_button = QPushButton(
        "CHECK EMAIL"
    )

    check_button.setObjectName(
        "check_button"
    )

    clear_button = QPushButton(
        "CLEAR"
    )

    clear_button.setObjectName(
        "clear_button"
    )

    clear_button.setEnabled(
        False
    )

    button_row.addWidget(
        check_button,
        4
    )

    button_row.addWidget(
        clear_button,
        1
    )

    main_layout.addLayout(
        button_row
    )

    # ========================================================
    # RESULT CARD
    # ========================================================

    result_card = QFrame()

    result_card.setObjectName(
        "card"
    )

    result_layout = QVBoxLayout()

    result_layout.setContentsMargins(
        20,
        20,
        20,
        20
    )

    result_layout.setSpacing(
        12
    )

    result_title = QLabel(
        "ANALYSIS RESULT"
    )

    result_title.setObjectName(
        "section_title"
    )

    result_layout.addWidget(
        result_title
    )

    # Main result
    result_label = QLabel(
        "Ready to analyze"
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
        "Select an .eml file to begin."
    )

    email_info.setObjectName(
        "email_info"
    )

    email_info.setWordWrap(
        True
    )

    result_layout.addWidget(
        email_info
    )

    # Detailed report
    report_box = QTextEdit()

    report_box.setReadOnly(
        True
    )

    report_box.setPlaceholderText(
        "The detailed analysis report will appear here."
    )

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

    # ========================================================
    # STATE
    # ========================================================

    selected_file = None

    worker = None

    # ========================================================
    # BROWSE
    # ========================================================

    def choose_file():

        nonlocal selected_file

        file_path, _ = QFileDialog.getOpenFileName(
            window,
            "Select an email file",
            "",
            "Email files (*.eml)"
        )

        if not file_path:

            return

        selected_file = file_path

        file_label.setText(
            file_path
        )

        result_label.setText(
            "Ready to analyze"
        )

        result_label.setStyleSheet(
            ""
        )

        email_info.setText(
            "File selected. Click CHECK EMAIL to begin."
        )

        report_box.clear()

        clear_button.setEnabled(
            True
        )

    browse_button.clicked.connect(
        choose_file
    )

    # ========================================================
    # CLEAR
    # ========================================================

    def clear_results():

        nonlocal selected_file

        selected_file = None

        file_label.setText(
            "No .eml file selected"
        )

        result_label.setText(
            "Ready to analyze"
        )

        result_label.setStyleSheet(
            ""
        )

        email_info.setText(
            "Select an .eml file to begin."
        )

        report_box.clear()

        clear_button.setEnabled(
            False
        )

    clear_button.clicked.connect(
        clear_results
    )

    # ========================================================
    # SCAN FINISHED
    # ========================================================

    def scan_finished(result):

        nonlocal worker

        scam = result.get(
            "scam",
            False
        )

        report = result.get(
            "report",
            "No report was returned."
        )

        # ----------------------------------------------------
        # SCAM RESULT
        # ----------------------------------------------------

        if scam:

            result_label.setText(
                "⚠  SCAM DETECTED"
            )

            result_label.setStyleSheet("""
                background-color: #450a0a;
                color: #fca5a5;
                border-radius: 8px;
                padding: 18px;
                font-size: 21px;
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
                padding: 18px;
                font-size: 21px;
                font-weight: bold;
            """)

        # ----------------------------------------------------
        # EXTRACT EMAIL INFORMATION
        # ----------------------------------------------------

        sender = "Unknown"

        subject = "Unknown"

        for line in report.splitlines():

            if line.startswith("From:"):

                sender = line[
                    len("From:"):
                ].strip()

            elif line.startswith("Subject:"):

                subject = line[
                    len("Subject:"):
                ].strip()

        email_info.setText(
            f"<b>Sender:</b> {sender}<br>"
            f"<b>Subject:</b> {subject}"
        )

        # ----------------------------------------------------
        # REPORT
        # ----------------------------------------------------

        report_box.setText(
            report
        )

        # ----------------------------------------------------
        # RESTORE BUTTONS
        # ----------------------------------------------------

        check_button.setEnabled(
            True
        )

        browse_button.setEnabled(
            True
        )

        clear_button.setEnabled(
            True
        )

        check_button.setText(
            "CHECK EMAIL"
        )

        worker = None

    # ========================================================
    # SCAN ERROR
    # ========================================================

    def scan_error(message):

        nonlocal worker

        result_label.setText(
            "⚠  SCAN ERROR"
        )

        result_label.setStyleSheet("""
            background-color: #451a03;
            color: #fdba74;
            border-radius: 8px;
            padding: 18px;
            font-size: 21px;
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

        clear_button.setEnabled(
            True
        )

        check_button.setText(
            "CHECK EMAIL"
        )

        worker = None

    # ========================================================
    # CHECK EMAIL
    # ========================================================

    def check_email():

        nonlocal worker

        # ----------------------------------------------------
        # No file selected
        # ----------------------------------------------------

        if selected_file is None:

            result_label.setText(
                "Please select an .eml file first."
            )

            result_label.setStyleSheet("""
                background-color: #422006;
                color: #fde68a;
                border-radius: 8px;
                padding: 18px;
                font-size: 18px;
                font-weight: bold;
            """)

            email_info.setText(
                "Use the Browse button to select an email file."
            )

            return

        # ----------------------------------------------------
        # Check extension
        # ----------------------------------------------------

        if not selected_file.lower().endswith(
            ".eml"
        ):

            result_label.setText(
                "Invalid file type"
            )

            email_info.setText(
                "Please select an .eml email file."
            )

            return

        # ----------------------------------------------------
        # Disable controls
        # ----------------------------------------------------

        check_button.setEnabled(
            False
        )

        browse_button.setEnabled(
            False
        )

        clear_button.setEnabled(
            False
        )

        check_button.setText(
            "ANALYZING EMAIL..."
        )

        # ----------------------------------------------------
        # Loading state
        # ----------------------------------------------------

        result_label.setText(
            "🔄  ANALYZING EMAIL..."
        )

        result_label.setStyleSheet("""
            background-color: #172554;
            color: #93c5fd;
            border-radius: 8px;
            padding: 18px;
            font-size: 21px;
            font-weight: bold;
        """)

        email_info.setText(
            "Scam Check is analyzing this email. "
            "Please wait..."
        )

        report_box.clear()

        # ----------------------------------------------------
        # Start worker
        # ----------------------------------------------------

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

    # ========================================================
    # SHOW WINDOW
    # ========================================================

    window.setLayout(
        main_layout
    )

    window.show()

    sys.exit(
        app.exec()
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()