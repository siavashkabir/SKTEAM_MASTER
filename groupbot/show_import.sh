#!/data/data/com.termux/files/usr/bin/bash

AC=modules/access.py

echo "─── خط ۱ تا ۱۵ ───"
sed -n '1,15p' "$AC" | cat -n
echo ""

echo "─── خط ۱ تا ۲۰ با نمایش دقیق ───"
head -20 "$AC" | cat -A | head -20
