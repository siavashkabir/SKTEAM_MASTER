#!/data/data/com.termux/files/usr/bin/bash

ST=modules/start.py

echo "═══════════════════════════════════════════════════"
echo "🔍 خط ۲۱۴۵ تا ۲۱۶۰"
echo "═══════════════════════════════════════════════════"
echo ""

sed -n '2145,2160p' "$ST" | cat -n
echo ""

echo "═══ admin_list_menu — کجا تعریف شده ═══"
grep -n "def admin_list_menu" modules/*.py
echo ""

echo "═══ get_group_admins — کجا تعریف شده ═══"
grep -n "def get_group_admins" database.py modules/*.py
echo ""

echo "═══════════════════════════════════════════════════"
