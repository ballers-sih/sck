export ROBERTA_MODEL="$PWD/.models/roberta-email-fraud-detector"
hf download cunxin/roberta-email-fraud-detector --local-dir "$ROBERTA_MODEL"

export CLAMAV_DB="$PWD/.clamav"

mkdir -p "$CLAMAV_DB"

cat > "$CLAMAV_DB/freshclam.conf" <<EOF
DatabaseDirectory $CLAMAV_DB
DatabaseOwner $(id -un)
UpdateLogFile $CLAMAV_DB/freshclam.log
PidFile $CLAMAV_DB/freshclam.pid
DatabaseMirror database.clamav.net
EOF

freshclam --config-file="$CLAMAV_DB/freshclam.conf"

