#!/data/data/com.termux/files/usr/bin/bash

{
echo "═══════════════════════════════════════════════════"
echo "🔍 دیاگ نهایی"
echo "═══════════════════════════════════════════════════"
echo ""

echo "═══ ۱. admin_permissions فعلی کاربر ═══"
source venv/bin/activate
python3 << 'PYEOF'
import sqlite3
from config import DATABASE_PATH
conn = sqlite3.connect(DATABASE_PATH)
c = conn.cursor()
c.execute("SELECT perm_name, enabled FROM admin_permissions WHERE chat_id=-1004349813270 AND user_id=8401175719")
rows = c.fetchall()
print(f"تعداد: {len(rows)}")
for r in rows: print(f"  {r}")
conn.close()
PYEOF
echo ""

echo "═══ ۲. access_handler — کد 'ناشناخته' ═══"
grep -n "ناشناخته\|نقش فعلی" modules/access.py
LINE=$(grep -n "نقش فعلی" modules/access.py | head -1 | cut -d: -f1)
if [ -n "$LINE" ]; then
    sed -n "$((LINE-5)),$((LINE+30))p" modules/access.py
fi
echo ""

echo "═══ ۳. admin_list_menu — کامل ═══"
LINE=$(grep -n "def admin_list_menu" modules/admin_perms.py | head -1 | cut -d: -f1)
sed -n "${LINE},$((LINE+25))p" modules/admin_perms.py
echo ""

echo "═══ ۴. کجا admin_list_menu صدا زده می‌شه ═══"
grep -n "admin_list_menu" modules/*.py
echo ""

echo "═══ ۵. acc_ap_ handler ═══"
LINE=$(grep -n 'if action.startswith("acc_ap_"):' modules/access.py | head -1 | cut -d: -f1)
if [ -n "$LINE" ]; then
    sed -n "${LINE},$((LINE+35))p" modules/access.py
fi
echo ""

echo "═══ ۶. get_admin_perm توی database ═══"
grep -n "def get_admin_perm\|def set_admin_perm\|def get_all_perms" database.py
LINE=$(grep -n "def get_all_perms" database.py | head -1 | cut -d: -f1)
if [ -n "$LINE" ]; then
    sed -n "${LINE},$((LINE+15))p" database.py
fi
echo ""

echo "═══════════════════════════════════════════════════"
} | tee ~/DIAG_FINAL.txt

echo ""
echo "✅ فایل: ~/DIAG_FINAL.txt"
