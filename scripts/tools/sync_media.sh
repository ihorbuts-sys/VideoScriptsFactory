#!/usr/bin/env bash
# Uploads, downloads or checks the media in media_manifest.json against the Drive folder VideoScriptsFactor-media.
#   scripts/tools/sync_media.sh upload [--include-optional] [--dry-run]
#   scripts/tools/sync_media.sh download [--dest DIR]
#   scripts/tools/sync_media.sh status
# Needs rclone with a Google Drive remote named "gdrive" (or MEDIA_REMOTE=<name>), and Python 3 with Pillow for upload.
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
remote="${MEDIA_REMOTE:-gdrive}"

setup_help() {
  cat <<'EOF'
rclone is not set up. One-time setup:
  brew install rclone
  rclone config
    n                 (new remote)
    gdrive            (name)
    drive             (storage: Google Drive)
    Enter             (client_id, empty)
    Enter             (client_secret, empty)
    1                 (scope: full access)
    Enter             (service_account_file, empty)
    n                 (edit advanced config)
    y                 (authenticate in the browser; sign in with the account that owns the Drive folder)
    n                 (shared drive: no, unless the folder is in one)
    y                 (keep this remote)
    q                 (quit)
EOF
}

if ! command -v rclone >/dev/null 2>&1; then setup_help; exit 1; fi
if ! rclone listremotes 2>/dev/null | grep -qx "${remote}:"; then setup_help; exit 1; fi

python="${PYTHON:-python3}"
if [ "${1:-}" = "upload" ] && ! "$python" -I -c "import PIL" >/dev/null 2>&1; then
  echo "Pillow is missing for $python: run '$python -m pip install Pillow' or set PYTHON to a Python that has it." >&2
  exit 1
fi
MEDIA_REMOTE="$remote" exec "$python" -I "$here/media_sync.py" "$@"
