#!/data/data/com.termux/files/usr/bin/bash
LOG="$HOME/sk_media/logs/hard_reset.log"
echo "[$(date)] HARD RESET START" > "$LOG"

pkill -9 -f "python3 -u player.py" 2>/dev/null
pkill -9 -f "proot --kill-on-exit" 2>/dev/null
sleep 5

curl -s -X POST http://127.0.0.1:8080/reset-current >> "$LOG" 2>&1
echo "" >> "$LOG"

cd "$HOME/sk_media"
: > logs/player.log
setsid proot-distro login ubuntu --isolated -- bash -c 'cd /root/sk_media && set -a && source /root/melody-player/.env && set +a && source /root/melody-player/venv/bin/activate && exec python3 -u player.py' < /dev/null >> logs/player.log 2>&1 &

sleep 2
echo "[$(date)] HARD RESET DONE" >> "$LOG"
