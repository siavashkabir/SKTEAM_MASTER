#!/data/data/com.termux/files/usr/bin/bash

ST=modules/start.py

echo "═══ خط ۱۵۷۰ تا ۱۶۰۰ (کد متن پیکربندی) ═══"
sed -n '1570,1600p' "$ST" | cat -n
echo ""

echo "═══ خط ۱۵۵۵ تا ۱۵۷۵ ═══"
sed -n '1555,1575p' "$ST" | cat -n
echo ""

