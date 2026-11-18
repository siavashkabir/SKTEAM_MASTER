#!/data/data/com.termux/files/usr/bin/bash

ST=modules/start.py

echo "═══ خط ۱۴۴۵ تا ۱۴۸۰ ═══"
sed -n '1445,1480p' "$ST" | cat -n
echo ""

echo "═══ خط ۱۵۹۰ تا ۱۶۱۵ ═══"
sed -n '1590,1615p' "$ST" | cat -n
echo ""

echo "═══ کدوم action اینو صدا می‌زنه؟ ═══"
sed -n '1440,1465p' "$ST" | grep -n "action\|if\|elif"
echo ""

