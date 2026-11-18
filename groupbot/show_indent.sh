#!/data/data/com.termux/files/usr/bin/bash

ST=modules/start.py

echo "═══ خط ۲۱۷۰ تا ۲۱۷۵ با cat -A (نمایش indent دقیق) ═══"
sed -n '2170,2175p' "$ST" | cat -A
echo ""

echo "═══ خط ۲۲۰۸ تا ۲۲۱۵ ═══"
sed -n '2208,2215p' "$ST" | cat -A
echo ""

