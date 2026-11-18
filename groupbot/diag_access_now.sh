#!/data/data/com.termux/files/usr/bin/bash

AC=modules/access.py
DS=modules/deputy_settings.py

{
echo "═══════════════════════════════════════════════════"
echo "🔍 دیاگ کامل پنل دسترسی — $(date)"
echo "═══════════════════════════════════════════════════"
echo ""

echo "═══ ۱. access.py — خط ۱ تا ۱۵ (import ها) ═══"
sed -n '1,15p' "$AC"
echo ""

echo "═══ ۲. access.py — توابع موجود ═══"
grep -n "^def \|^async def " "$AC"
echo ""

echo "═══ ۳. access.py — همه callback_data ها ═══"
grep -n "callback_data=" "$AC"
echo ""

echo "═══ ۴. access.py — توابع perms صدا زده شده ═══"
grep -n "get_user_perm\|set_user_perm\|toggle_user_perm\|has_user_perm\|get_admin_perm\|set_admin_perm" "$AC"
echo ""

echo "═══ ۵. توی database.py — توابع perms ═══"
grep -n "^def " ../groupbot/database.py | grep -i perm
echo ""

echo "═══ ۶. کجاها access_menu یا build_access_menu صدا زده می‌شه ═══"
grep -rn "access_menu\|build_access_menu\|guide_access" modules/*.py | grep -v ".bak"
echo ""

echo "═══ ۷. رجیستر access.py ═══"
tail -10 "$AC"
echo ""

echo "═══ ۸. توی deputy_settings.py — چیزها ═══"
grep -n "^def \|^async def \|callback_data=" "$DS"
echo ""

echo "═══ ۹. توی owner_guide.py — بخش access ═══"
grep -n "guide_access\|دسترسی" modules/owner_guide.py
echo ""

echo "═══ ۱۰. توی start.py — کجا 'افزودن دسترسی' یا 'دسترسی' هست ═══"
grep -n "افزودن دسترسی\|دسترسی\|access" modules/start.py | head -30
echo ""

echo "═══ ۱۱. تست: get_user_perms صدا زده می‌شه؟ ═══"
source venv/bin/activate
python3 << 'PYEOF'
import sys
sys.path.insert(0, '.')
try:
    from modules import access
    print("✅ import access OK")
except Exception as e:
    print(f"❌ import access ERR: {e}")
    import traceback
    traceback.print_exc()

try:
    from database import get_user_perms, toggle_user_perm, has_user_perm, get_all_deputy_perms
    print("✅ import database perms OK")
except Exception as e:
    print(f"❌ import database perms ERR: {e}")
PYEOF
echo ""

echo "═══ ۱۲. آخرین ۳۰ خط لاگ — access ═══"
tail -n 200 ~/groupbot_bot.log | grep -iE "access|acc_|perm" | tail -20
echo ""

echo "═══════════════════════════════════════════════════"
} | tee ~/DIAG_ACCESS_NOW.txt

echo ""
echo "✅ فایل: ~/DIAG_ACCESS_NOW.txt"
