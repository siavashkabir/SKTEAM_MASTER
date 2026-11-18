#!/data/data/com.termux/files/usr/bin/bash

{
echo "═══════════════════════════════════════════════════"
echo "🔍 دیاگ پیکربندی + نامشخص"
echo "═══════════════════════════════════════════════════"
echo ""

echo "═══ ۱. خط ۲۱۴۵ تا ۲۱۷۰ (پیکربندی کامل) ═══"
sed -n '2145,2170p' modules/start.py | cat -n
echo ""

echo "═══ ۲. تعریف cv ═══"
grep -n "cv = \|cv=\|'cv'" modules/start.py | head -10
echo ""

echo "═══ ۳. دنبال 'نامشخص' توی کل ماژول‌ها ═══"
grep -rn "نامشخص" modules/*.py | grep -v ".bak"
echo ""

echo "═══ ۴. role_label و role_emoji توی access.py ═══"
LINE=$(grep -n "def role_label" modules/access.py | head -1 | cut -d: -f1)
sed -n "${LINE},$((LINE+15))p" modules/access.py
echo ""

LINE=$(grep -n "def role_emoji" modules/access.py | head -1 | cut -d: -f1)
sed -n "${LINE},$((LINE+15))p" modules/access.py
echo ""

echo "═══ ۵. admin_list_menu — چطور نمایش می‌ده ═══"
LINE=$(grep -n "def admin_list_menu" modules/admin_perms.py | head -1 | cut -d: -f1)
sed -n "${LINE},$((LINE+20))p" modules/admin_perms.py
echo ""

echo "═══ ۶. توی admin_perms.py — role_label چیه ═══"
grep -n "role_label\|def role" modules/admin_perms.py
echo ""

echo "═══ ۷. دستور پیکربندی توی handler ═══"
grep -n "پیکربندی\|config\b\|گروه.*تعداد\|تعداد.*ادمین\|گفتگو" modules/start.py | head -20
echo ""

echo "═══════════════════════════════════════════════════"
} | tee ~/DIAG_LAST.txt

echo ""
echo "✅ فایل: ~/DIAG_LAST.txt"
