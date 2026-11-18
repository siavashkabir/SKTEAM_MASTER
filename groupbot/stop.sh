#!/data/data/com.termux/files/usr/bin/bash
# Stop all services
echo "🛑 توقف همه سرویس‌ها..."
pkill -9 -f "main.py" ; echo "✅ ربات اصلی متوقف شد"
pkill -9 -f "backup_daemon.py" ; echo "✅ Backup Daemon متوقف شد"
pkill -9 -f "backup_watcher.py" ; echo "✅ Backup Watcher متوقف شد"
pkill -9 -f "connection_monitor.py" ; echo "✅ Connection Monitor متوقف شد"
echo "✅ همه سرویس‌ها متوقف شدن"
