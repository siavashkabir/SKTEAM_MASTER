#!/data/data/com.termux/files/usr/bin/bash

ST=modules/start.py

echo "═══ خط ۱۵۳۵ تا ۱۵۹۰ (کد کامل پیکربندی) ═══"
sed -n '1535,1590p' "$ST" | cat -n
echo ""

echo "═══ همه جا 'admins' استفاده شده (توی خط ۱۵۰۰ تا ۱۶۰۰) ═══"
sed -n '1500,1600p' "$ST" | grep -n "admins\|owners\|_admin\|_owner"
echo ""

