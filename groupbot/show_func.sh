#!/data/data/com.termux/files/usr/bin/bash

LINE=$(grep -n "async def check_nsfw" modules/nsfw.py | head -1 | cut -d: -f1)
echo "check_nsfw از خط: $LINE"
echo "═══════════════════════════════════════════════════"
echo ""

# ۳۵ خط بعد از شروع تابع
sed -n "${LINE},$((LINE+35))p" modules/nsfw.py

echo ""
echo "═══════════════════════════════════════════════════"
