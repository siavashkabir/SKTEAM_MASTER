#!/data/data/com.termux/files/usr/bin/bash

{
echo "═══════════════════════════════════════════════════"
echo "🔍 دیاگ نقش deputy"
echo "═══════════════════════════════════════════════════"
echo ""

echo "═══ ۱. تابع is_deputy ═══"
grep -n "def is_deputy" database.py modules/*.py | grep -v ".bak"
LINE=$(grep -n "def is_deputy" database.py | head -1 | cut -d: -f1)
if [ -n "$LINE" ]; then
    sed -n "${LINE},$((LINE+20))p" database.py
fi
echo ""

echo "═══ ۲. تابع add_admin_to_db ═══"
LINE=$(grep -n "def add_admin_to_db" database.py | head -1 | cut -d: -f1)
if [ -n "$LINE" ]; then
    sed -n "${LINE},$((LINE+25))p" database.py
fi
echo ""

echo "═══ ۳. تابع promote_admin (توی admin.py) ═══"
grep -n "def promote_admin\|def add_admin" modules/admin.py
LINE=$(grep -n "def promote_admin" modules/admin.py | head -1 | cut -d: -f1)
if [ -n "$LINE" ]; then
    sed -n "${LINE},$((LINE+40))p" modules/admin.py
fi
echo ""

echo "═══ ۴. دیتابیس فعلی گروه ═══"
source venv/bin/activate
python3 << 'PYEOF'
import sqlite3
from config import DATABASE_PATH

conn = sqlite3.connect(DATABASE_PATH)
c = conn.cursor()

# group_admins
print("=== group_admins ===")
c.execute("SELECT * FROM group_admins WHERE chat_id=-1004349813270")
for r in c.fetchall(): print(f"  {r}")
print()

# admin_permissions
print("=== admin_permissions ===")
c.execute("SELECT * FROM admin_permissions WHERE chat_id=-1004349813270")
for r in c.fetchall(): print(f"  {r}")
print()

# deputy_perms
print("=== deputy_perms ===")
c.execute("SELECT * FROM deputy_perms WHERE chat_id=-1004349813270")
for r in c.fetchall(): print(f"  {r}")
print()

# تست is_deputy
sys.path.insert(0, '.')
print("=== تست is_deputy ===")
try:
    from database import is_deputy
    for uid in [8820561431, 8250087472, 8401175719, 7955185125]:
        print(f"  is_deputy(-1004349813270, {uid}): {is_deputy(-1004349813270, uid)}")
except Exception as e:
    print(f"  خطا: {e}")

conn.close()
PYEOF
echo ""

echo "═══════════════════════════════════════════════════"
} | tee ~/DIAG_DEPUTY.txt

echo ""
echo "✅ فایل: ~/DIAG_DEPUTY.txt"
