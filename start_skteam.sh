#!/data/data/com.termux/files/usr/bin/bash

set -euo pipefail

if command -v termux-wake-lock >/dev/null 2>&1; then
    termux-wake-lock
fi

sleep 20
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/start_all.sh"
