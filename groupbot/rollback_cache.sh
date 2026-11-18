#!/data/data/com.termux/files/usr/bin/bash

ST=modules/start.py
SS=modules/shared_state.py

echo "─── بک‌آپ‌ها ───"
ls -lt "$ST".bak_cache_* 2>/dev/null | head -3
echo ""

LATEST_ST=$(ls -t "$ST".bak_cache_* 2>/dev/null | head -1)
LATEST_SS=$(ls -t "$SS".bak_cache_* 2>/dev/null | head -1)

echo "restore start.py از: $LATEST_ST"
cp "$LATEST_ST" "$ST"

if [ -n "$LATEST_SS" ]; then
    echo "restore shared_state.py از: $LATEST_SS"
    cp "$LATEST_SS" "$SS"
fi
echo ""

cd ~/groupbot
source venv/bin/activate

echo "─── کامپایل تست ───"
if python3 -m py_compile "$ST" 2>&1 && python3 -m py_compile "$SS" 2>&1; then
    echo "✅ کامپایل OK"
else
    echo "❌ خطا"
    exit 1
fi
echo ""
echo "═══════════════════════════════════════════════════"
echo "✅ Rollback انجام شد"
echo ""
echo "🎯 ری‌استارت:"
echo "pkill -9 -f 'python3 -u'; sleep 3; rm -f .bot.lock; nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 & sleep 15"
echo "═══════════════════════════════════════════════════"
