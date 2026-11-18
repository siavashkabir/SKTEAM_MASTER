#!/data/data/com.termux/files/usr/bin/bash

echo "═══════════════════════════════════════════════════"
echo "🔍 کد پیکربندی"
echo "═══════════════════════════════════════════════════"
echo ""

echo "─── 'تعداد ادمین' کجاست؟ ───"
grep -rn "تعداد ادمین" modules/*.py | grep -v ".bak"
echo ""

echo "─── خط ۲۱۵۰ تا ۲۱۷۵ ───"
sed -n '2150,2175p' modules/start.py | cat -n
echo ""

echo "─── خط ۲۳۰۰ تا ۲۳۳۵ ───"
sed -n '2300,2335p' modules/start.py | cat -n
echo ""

echo "─── 'پیکربندی' کجاست؟ ───"
grep -n "پیکربندی" modules/start.py
echo ""

echo "═══════════════════════════════════════════════════"
