# Load .env into the current PowerShell process environment
$ENV_FILE = Join-Path $PSScriptRoot ".env"

if (Test-Path $ENV_FILE) {
    Get-Content $ENV_FILE |
        Where-Object { $_ -and $_ -notmatch '^\s*#' } |
        ForEach-Object {
            $key, $value = $_ -split '=', 2

            if ($key -and $value) {
                [Environment]::SetEnvironmentVariable(
                    $key.Trim(),
                    $value.Trim().Trim('"').Trim("'"),
                    "Process"
                )
            }
        }
}

# Project root
$PROJECT_ROOT = $PSScriptRoot

# RoBERTa model
if (-not $env:ROBERTA_MODEL) {
    $env:ROBERTA_MODEL = Join-Path $PROJECT_ROOT ".models\roberta-email-fraud-detector"
}

# Download the model if needed
if (-not (Test-Path $env:ROBERTA_MODEL)) {
    New-Item -ItemType Directory -Force -Path $env:ROBERTA_MODEL | Out-Null

    hf download cunxin/roberta-email-fraud-detector `
        --local-dir "$env:ROBERTA_MODEL"
}

# ClamAV database directory
if (-not $env:CLAMAV_DB) {
    $env:CLAMAV_DB = Join-Path $PROJECT_ROOT ".clamav"
}

New-Item -ItemType Directory -Force -Path $env:CLAMAV_DB | Out-Null

# Create freshclam.conf
$FRESHCLAM_CONF = Join-Path $env:CLAMAV_DB "freshclam.conf"

@"
DatabaseDirectory $env:CLAMAV_DB
UpdateLogFile $env:CLAMAV_DB\freshclam.log
PidFile $env:CLAMAV_DB\freshclam.pid
DatabaseMirror database.clamav.net
"@ | Set-Content -Path $FRESHCLAM_CONF

# Update ClamAV databases
freshclam --config-file="$FRESHCLAM_CONF"
