#!/data/data/com.termux/files/usr/bin/bash

{
echo "═══════════════════════════════════════════════════"
echo "🔍 دیاگ پاک‌سازی (purge)"
echo "═══════════════════════════════════════════════════"
echo ""

echo "═══ ۱. فایل purge.py ═══"
ls -la modules/purge.py 2>/dev/null && echo "✅ هست" || echo "❌ نیست"
echo ""

echo "═══ ۲. توابع purge.py ═══"
grep -n "^def \|^async def " modules/purge.py | head -20
echo ""

echo "═══ ۳. کد کامل purge.py ═══"
cat modules/purge.py
echo ""

echo "═══ ۴. کجا purge رجیستر شده ═══"
grep -rn "purge" modules/purge.py modules/start.py | grep -E "add_handler|CallbackQueryHandler|CommandHandler|register" | head -10
echo ""

echo "═══ ۵. توی start.py — purge چطور صدا زده می‌شه ═══"
grep -n "purge\|پاکسازی\|پاک سازی" modules/start.py | head -20
echo ""

echo "═══ ۶. callback_data های purge ═══"
grep -rn "purge_\|callback_data.*purge" modules/*.py | grep -v ".bak"
echo ""

echo "═══ ۷. خطاهای اخیر purge از لاگ ═══"
tail -n 500 ~/groupbot_bot.log | grep -iE "purge|پاکسازی|پاک سازی" | tail -20
echo ""

echo "═══════════════════════════════════════════════════"
} | tee ~/DIAG_PURGE.txt

echo ""
echo "✅ فایل: ~/DIAG_PURGE.txt"
echo "📏 خطوط: $(wc -l < ~/DIAG_PURGE.txt)"
