#!/data/data/com.termux/files/usr/bin/bash
# run_monitor.sh - اجرای connection_monitor با Lock File
LOCK_FILE="/data/data/com.termux/files/home/groupbot/.monitor.lock"
exec 9>"$LOCK_FILE"
if ! flock -n 9; then
    echo "[$(date '+%H:%M:%S')] [MONITOR LOCK] Already running. Exit."
    exit 0
fi
cd /data/data/com.termux/files/home/groupbot
source venv/bin/activate
exec python3 -u connection_monitor.py
