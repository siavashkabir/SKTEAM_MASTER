#!/data/data/com.termux/files/usr/bin/bash

ST=modules/start.py

echo "═══ خط ۱۵۱۵ تا ۱۵۸۰ ═══"
sed -n '1515,1580p' "$ST" | cat -n
echo ""

echo "═══ خط ۱۵۸۰ تا ۱۶۲۰ ═══"
sed -n '1580,1620p' "$ST" | cat -n
