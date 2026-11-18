#!/data/data/com.termux/files/usr/bin/bash

echo "═══ ۱. kill همه پروسه‌ها ═══"
pkill -9 -f "python3"
pkill -9 -f "main.py"
pkill -9 -f "connection_monitor"
sleep 5

# اگه باز هست، kill -9 برای هر PID
for pid in $(pgrep -f "python3"); do
    kill -9 "$pid" 2>/dev/null
done
sleep 3

echo "پروسه‌های باقی‌مونده:"
pgrep -af "python3" || echo "✅ تمیز"

echo ""
echo "═══ ۲. حذف lock ═══"
rm -f ~/groupbot/.bot.lock ~/groupbot/.monitor.lock

echo ""
echo "═══ ۳. راه‌اندازی (فقط یک نسخه) ═══"
cd ~/groupbot
source venv/bin/activate
nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 &
echo "✅ یک نسخه بالا اومد"
sleep 15

echo ""
echo "═══ ۴. چک: چند نسخه؟ ═══"
pgrep -af "python3 -u main.py"

echo ""
echo "═══ ۵. پیدا کردن chat_id واقعی HERITAGE ═══"
echo "پیام اخیر توی HERITAGE رو ببینیم:"
sleep 5
tail -n 100 ~/groupbot_bot.log | grep -E "HERITAGE|خبر|HANDLER DEBUG" | head -20

echo ""
echo "═══════════════════════════════════════════════════"
