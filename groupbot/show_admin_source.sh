#!/data/data/com.termux/files/usr/bin/bash

ST=modules/start.py

echo "═══ کد ساخت admins ═══"
grep -n "get_administrators\|admins =" "$ST" | head -10
echo ""

echo "═══ خط ۲۰۹۵ تا ۲۱۲۰ ═══"
sed -n '2095,2120p' "$ST" | cat -n
echo ""

echo "═══ خط ۲۱۲۵ تا ۲۱۷۰ ═══"
sed -n '2125,2170p' "$ST" | cat -n
echo ""

echo "═══ تعداد ادمین‌ها + مالکین ═══"
grep -n "تعداد ادمین\|مالکین:" "$ST" | head -5
echo ""

