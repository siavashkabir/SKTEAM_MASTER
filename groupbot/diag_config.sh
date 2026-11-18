#!/data/data/com.termux/files/usr/bin/bash

{
echo "═══════════════════════════════════════════════════"
echo "🔍 دیاگ پیکربندی"
echo "═══════════════════════════════════════════════════"
echo ""

echo "═══ ۱. کجا «پیکربندی» توی start.py ═══"
grep -n "پیکربندی\|config_menu\|admin_list_menu\|get_group_admins" modules/start.py | head -20
echo ""

echo "═══ ۲. تابع admin_list_menu (توی admin_perms.py) ═══"
grep -n "def admin_list_menu" modules/admin_perms.py
LINE=$(grep -n "def admin_list_menu" modules/admin_perms.py | head -1 | cut -d: -f1)
if [ -n "$LINE" ]; then
    sed -n "${LINE},$((LINE+25))p" modules/admin_perms.py
fi
echo ""

echo "═══ ۳. تابع get_group_admins (توی admin_perms.py) ═══"
grep -n "def get_group_admins" modules/admin_perms.py
LINE=$(grep -n "def get_group_admins" modules/admin_perms.py | head -1 | cut -d: -f1)
if [ -n "$LINE" ]; then
    sed -n "${LINE},$((LINE+20))p" modules/admin_perms.py
fi
echo ""

echo "═══ ۴. توی start.py — کجا admin_list_menu صدا زده می‌شه ═══"
grep -n "admin_list_menu\|پیکربندی\|config" modules/start.py | head -20
echo ""

echo "═══ ۵. توی start.py — handler پیکربندی ═══"
grep -n "config\|admin_list\|g_op_config" modules/start.py | grep -iE "callback|handler|action" | head -20
echo ""

echo "═══ ۶. دیتابیس فعلی ═══"
source venv/bin/activate
python3 << 'PYEOF'
import sqlite3
from config import DATABASE_PATH
conn = sqlite3.connect(DATABASE_PATH)
c = conn.cursor()
print("=== group_admins ===")
c.execute("SELECT * FROM group_admins WHERE chat_id=-1004349813270")
for r in c.fetchall(): print(f"  {r}")
print()
print("=== deputies ===")
c.execute("SELECT * FROM deputies WHERE chat_id=-1004349813270")
for r in c.fetchall(): print(f"  {r}")
conn.close()
PYEOF
echo ""

echo "═══════════════════════════════════════════════════"
} | tee ~/DIAG_CONFIG.txt

echo ""
echo "✅ فایل: ~/DIAG_CONFIG.txt"
