#!/data/data/com.termux/files/usr/bin/bash
# bot_watchdog.sh - چک کردن ربات + connection_monitor

cd /data/data/com.termux/files/home/groupbot

# --- چک ربات ---
if ! pgrep -f "python3 -u main.py" > /dev/null 2>&1; then
    echo "[$(date '+%H:%M:%S')] [WATCHDOG] Bot is DOWN. Starting..."
    nohup bash /data/data/com.termux/files/home/groupbot/run_bot.sh > /data/data/com.termux/files/home/groupbot_watchdog.log 2>&1 &
    echo "[$(date '+%H:%M:%S')] [WATCHDOG] Bot started."
else
    echo "[$(date '+%H:%M:%S')] [WATCHDOG] Bot is running."
fi

# --- چک connection_monitor ---
if ! pgrep -f "python3 -u connection_monitor.py" > /dev/null 2>&1; then
    echo "[$(date '+%H:%M:%S')] [WATCHDOG] Monitor is DOWN. Starting..."
    nohup bash /data/data/com.termux/files/home/groupbot/run_monitor.sh > /data/data/com.termux/files/home/groupbot_monitor_runner.log 2>&1 &
    echo "[$(date '+%H:%M:%S')] [WATCHDOG] Monitor started."
else
    echo "[$(date '+%H:%M:%S')] [WATCHDOG] Monitor is running."
fi
