#!/data/data/com.termux/files/usr/bin/bash

echo "═══ پروسه‌های فعلی ═══"
pgrep -af "python3 -u"

echo ""
echo "═══ kill همه ═══"
pkill -9 -f "python3 -u main.py"
pkill -9 -f "connection_monitor.py"
pkill -9 -f "python3 -u"
sleep 3

echo ""
echo "═══ چک ═══"
REMAIN=$(pgrep -af "python3")
if [ -n "$REMAIN" ]; then
    echo "هنوز هست:"
    echo "$REMAIN"
    pgrep -f "python3" | while read pid; do
        kill -9 "$pid" 2>/dev/null
    done
    sleep 2
fi

echo ""
echo "═══ حذف lock ═══"
rm -f ~/groupbot/.bot.lock
rm -f ~/groupbot/.monitor.lock
echo "✅"

echo ""
echo "═══ راه‌اندازی مجدد (فقط یک نسخه) ═══"
cd ~/groupbot
source venv/bin/activate
nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 &
echo "✅ یک نسخه بالا اومد"
sleep 15

echo ""
echo "═══ چک نهایی ═══"
pgrep -af "python3 -u"

echo ""
echo "═══════════════════════════════════════════════════"
