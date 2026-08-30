# sck - scam check

SIH internal hackathon

Team: `ballers`

# usage

1. Running the daemon

<details>

<summary>Click to expand: with [Nix](https://nixos.org/download)</summary>

```console
$ nix build github:ballers-sih/sck
$ nix develop github:ballers-sih/sck
$ result/bin/sckd
```

Remember to pass `VT_API_KEY` (your VirusTotal API Key) using `export` or in a
`.env`.

</details>

```console
$ git clone https://github.com/ballers-sih/sck
$ cd sck
$ pip install -e .
$ ./shell-hook.sh
$ sckd
```

Remember to pass `VT_API_KEY` (your VirusTotal API Key) using `export` or in a
`.env`.

2. Running a client

```console
$ nix build github:ballers-sih/sck
$ export SCKD_ADDRESS=127.0.0.1
$ export SCKD_PORT=7079
```

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
