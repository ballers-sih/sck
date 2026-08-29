# sck - scam check

SIH internal hackathon

Team: `ballers`

# usage

# components

1. `sckd`, the scam check daemon, exposes a single HTTP endpoint `/submit` which
   accepts a base64-encoded rfc-compliant .eml and responds with the report

   ```
   /submit (JSON)

   {
     "content": "<base64-encoded-.eml-file>"
   }
   ```

   ```
   /submit response (JSON)

   {
     "scam": <true|false>,
     "report": "report-text"
   }
   ```

2. `sck_cli` and `sck_gui` which can submit arbitrary .eml files to `sckd` at
   `http://$SCKD_ADDRESS:$SCKD_PORT/submit` and displays the report

3. `sck_imapd` which watches an IMAP mailbox for forwarded emails, extracts the
   original .eml and submits to `sckd` at
   `http://$SCKD_ADDRESS:$SCKD_PORT/submit` and sends the report using SMTP
