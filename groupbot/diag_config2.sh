#!/data/data/com.termux/files/usr/bin/bash

ST=modules/start.py

{
echo "═══════════════════════════════════════════════════"
echo "🔍 دیاگ پیکربندی"
echo "═══════════════════════════════════════════════════"
echo ""

echo "═══ ۱. کد پیکربندی توی start.py — خط ۲۱۲۵ تا ۲۱۴۵ ═══"
sed -n '2125,2145p' "$ST" | cat -n
echo ""

echo "═══ ۲. کد پیکربندی — خط ۲۱۸۰ تا ۲۲۰۰ ═══"
sed -n '2180,2200p' "$ST" | cat -n
echo ""

echo "═══ ۳. همه جاهایی که پیکربندی هست ═══"
grep -n "پیکربندی\|config_menu\|گفتگو\|admin_list_menu" "$ST" | head -20
echo ""

echo "═══ ۴. کجا get_group_admins صدا زده می‌شه ═══"
grep -n "get_group_admins" "$ST"
echo ""

echo "═══ ۵. توی handler — چی نشون می‌ده ═══"
grep -n "admin_list_menu\|get_group_admins\|گروه.*تعداد\|تعداد.*ادمین" "$ST" | head -20
echo ""

echo "═══ ۶. تست عملی ═══"
source venv/bin/activate
python3 << 'PYEOF'
import sys
sys.path.insert(0, '.')

# چک get_group_admins
from database import get_group_admins
admins = get_group_admins(-1004349813270)
print(f"get_group_admins: {len(admins)} نتیجه")
for a in admins:
    print(f"  user_id={a.get('user_id')}, name={a.get('name')}")
print()

# چک get_all_admins (اگه هست)
try:
    from database import get_all_admins
    r = get_all_admins(-1004349813270)
    print(f"get_all_admins: {r}")
except Exception as e:
    print(f"get_all_admins: {e}")
PYEOF
echo ""

echo "═══════════════════════════════════════════════════"
} | tee ~/DIAG_CONFIG2.txt

echo ""
echo "✅ فایل: ~/DIAG_CONFIG2.txt"
