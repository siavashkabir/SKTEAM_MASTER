#!/data/data/com.termux/files/usr/bin/bash

ST=modules/start.py

echo "═══════════════════════════════════════════════════"
echo "🔍 کد کامل پیکربندی"
echo "═══════════════════════════════════════════════════"
echo ""

echo "─── خط ۲۱۴۰ تا ۲۱۷۰ ───"
sed -n '2140,2170p' "$ST" | cat -n
echo ""

echo "─── خط ۲۲۸۰ تا ۲۳۳۵ ───"
sed -n '2280,2335p' "$ST" | cat -n
echo ""

echo "═══ کد کامل پیدا کردن منوی 'تعداد ادمین' ═══"
grep -n "تعداد ادمین\|لیست ادمین" "$ST"
echo ""

echo "═══ همه جا admin_list_menu صدا زده می‌شه ═══"
grep -n "admin_list_menu\|get_group_admins\|get_group_admins_list" "$ST"
echo ""

echo "═══ کل ساختار action = 'menu_admin_perms' و اطرافش ═══"
LINE=$(grep -n 'action == "menu_admin_perms"' "$ST" | head -1 | cut -d: -f1)
if [ -n "$LINE" ]; then
    sed -n "${LINE},$((LINE+50))p" "$ST"
fi
echo ""

echo "═══════════════════════════════════════════════════"
