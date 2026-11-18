#!/data/data/com.termux/files/usr/bin/bash
# run_bot.sh - اجرای ربات با Lock File
LOCK_FILE="/data/data/com.termux/files/home/groupbot/.bot.lock"
exec 9>"$LOCK_FILE"
if ! flock -n 9; then
    echo "[$(date '+%H:%M:%S')] [BOT LOCK] Already running. Exit."
    exit 0
fi
cd /data/data/com.termux/files/home/groupbot
source venv/bin/activate
exec python3 -u main.py
