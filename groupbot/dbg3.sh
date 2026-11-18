#!/data/data/com.termux/files/usr/bin/bash

NSFW=modules/nsfw.py

echo "═══════════════════════════════════════════════════"
echo "🔍 دیاگ کامل check_nsfw"
echo "═══════════════════════════════════════════════════"
echo ""

echo "─── ۱. check_nsfw چطور شروع می‌شه ───"
LINE=$(grep -n "async def check_nsfw" "$NSFW" | head -1 | cut -d: -f1)
echo "خط شروع: $LINE"
echo ""
sed -n "${LINE},$((LINE+30))p" "$NSFW"
echo ""

echo "─── ۲. registered group ───"
grep -n "check_nsfw" "$NSFW"
echo ""

echo "─── ۳. پروسه فعال ───"
pgrep -af "python3 -u"
echo ""

echo "─── ۴. آخرین ۵۰ خط لاگ ───"
tail -n 50 ~/groupbot_bot.log
echo ""

echo "─── ۵. grep در لاگ ───"
tail -n 200 ~/groupbot_bot.log | grep -iE "nsfw|check_nsfw|middleware" | tail -20
echo ""

echo "═══════════════════════════════════════════════════"
