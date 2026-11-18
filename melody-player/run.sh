#!/data/data/com.termux/files/usr/bin/bash
cd "$(dirname "$0")"
set -a; source .env; set +a
exec python main.py
