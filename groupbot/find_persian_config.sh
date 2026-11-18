#!/data/data/com.termux/files/usr/bin/bash

echo "═══ ۱. کجا 'پیکربندی' توی کل ماژول‌ها هست ═══"
grep -rn "پیکربندی" modules/*.py | grep -v ".bak" | head -20
echo ""

echo "═══ ۲. توی start.py — persian_handler keywords ═══"
grep -n "پیکربندی\|refresh\|/refresh" modules/start.py | head -20
echo ""

echo "═══ ۳. خط ۱۴۵۰ تا ۱۴۷۰ ═══"
sed -n '1450,1470p' modules/start.py | cat -n
echo ""

echo "═══ ۴. خط ۱۵۹۵ تا ۱۶۱۰ ═══"
sed -n '1595,1610p' modules/start.py | cat -n
echo ""

echo "═══ ۵. کدوم تابع این بخشه؟ ═══"
awk 'NR<1620 && /^(async )?def / {last=$0; line=NR} END{}' modules/start.py
grep -n "^async def \|^def " modules/start.py | awk -F: '$1 < 1610 && $1 > 1400 {print}'
echo ""

echo "═══ ۶. do_refresh کجاست ═══"
grep -n "def do_refresh" modules/start.py
LINE=$(grep -n "def do_refresh" modules/start.py | head -1 | cut -d: -f1)
if [ -n "$LINE" ]; then
    sed -n "${LINE},$((LINE+10))p" modules/start.py
fi
echo ""

