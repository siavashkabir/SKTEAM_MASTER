#!/data/data/com.termux/files/usr/bin/bash

{
echo "═══════════════════════════════════════════════════"
echo "🔍 دیاگ دو مشکل"
echo "═══════════════════════════════════════════════════"
echo ""

echo "═══ ۱. get_target_role ═══"
grep -n "def get_target_role" modules/access.py
LINE=$(grep -n "def get_target_role" modules/access.py | head -1 | cut -d: -f1)
sed -n "${LINE},$((LINE+20))p" modules/access.py
echo ""

echo "═══ ۲. is_admin توی import access.py ═══"
grep -n "is_admin" modules/access.py | head -5
echo ""

echo "═══ ۳. admin_list_menu توی admin_perms.py ═══"
grep -n "def admin_list_menu\|def get_group_admins" modules/admin_perms.py
LINE=$(grep -n "def admin_list_menu" modules/admin_perms.py | head -1 | cut -d: -f1)
sed -n "${LINE},$((LINE+25))p" modules/admin_perms.py
echo ""

echo "═══ ۴. تست get_group_admins ═══"
source venv/bin/activate
python3 << 'PYEOF'
import sys
sys.path.insert(0, '.')
from database import get_group_admins
admins = get_group_admins(-1004349813270)
print(f"get_group_admins: {admins}")
print(f"تعداد: {len(admins)}")
PYEOF
echo ""

echo "═══ ۵. تست get_target_role ═══"
python3 << 'PYEOF'
import sys
sys.path.insert(0, '.')
from modules.access import get_target_role
chat_id = -1004349813270
for uid in [8401175719, 8250087472, 8820561431, 7955185125]:
    print(f"  {uid}: {get_target_role(chat_id, uid)}")
PYEOF
echo ""

echo "═══════════════════════════════════════════════════"
} | tee ~/DIAG_2PROB.txt

echo ""
echo "✅ فایل: ~/DIAG_2PROB.txt"
