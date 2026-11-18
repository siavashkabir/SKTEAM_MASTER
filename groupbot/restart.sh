#!/data/data/com.termux/files/usr/bin/bash
# Restart all services
echo "🔄 ری‌استارت همه سرویس‌ها..."
bash "$HOME/groupbot/stop.sh"
sleep 3
bash "$HOME/groupbot/startup.sh"
