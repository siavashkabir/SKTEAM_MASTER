#!/data/data/com.termux/files/usr/bin/bash

AD=modules/admin.py

echo "─── خطوط ۱۰۰ تا ۱۴۰ ───"
sed -n '100,140p' "$AD" | cat -n
echo ""

echo "─── با cat -A برای indent دقیق ───"
sed -n '100,140p' "$AD" | cat -A | head -40
