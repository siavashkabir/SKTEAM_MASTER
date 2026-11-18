#!/data/data/com.termux/files/usr/bin/bash

ST=modules/start.py

echo "═══ کد فعلی پیکربندی (۱۵۵۰ تا ۱۶۰۰) ═══"
sed -n '1550,1600p' "$ST" | cat -n
echo ""

echo "═══ خطوط کلیدی ═══"
grep -n "_db_admins\|_tg_admins\|for _a in _db_admins\|for _oa in _tg_admins" "$ST"
echo ""

