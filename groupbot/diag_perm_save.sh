#!/data/data/com.termux/files/usr/bin/bash

{
echo "═══════════════════════════════════════════════════"
echo "🔍 دیاگ ذخیره perms"
echo "═══════════════════════════════════════════════════"
echo ""

echo "═══ ۱. admin_permissions فعلی ═══"
source venv/bin/activate
python3 << 'PYEOF'
import sqlite3
from config import DATABASE_PATH

conn = sqlite3.connect(DATABASE_PATH)
c = conn.cursor()
c.execute("SELECT perm_name, enabled FROM admin_permissions WHERE chat_id=-1004349813270 AND user_id=8401175719")
rows = c.fetchall()
print(f"تعداد: {len(rows)}")
for r in rows:
    print(f"  {r}")
conn.close()
PYEOF
echo ""

echo "═══ ۲. توی start.py — pm_toggle چطور key رو ذخیره می‌کنه ═══"
grep -n "PROMOTE_WAIT\[uid\]\[\"perms\"\]" modules/start.py
LINE=$(grep -n 'PROMOTE_WAIT\[uid\]\["perms"\]' modules/start.py | head -1 | cut -d: -f1)
if [ -n "$LINE" ]; then
    sed -n "$((LINE-5)),$((LINE+5))p" modules/start.py
fi
echo ""

echo "═══ ۳. تعریف PROMOTE_WAIT ═══"
grep -n "PROMOTE_WAIT\[user.id\]" modules/start.py
LINE=$(grep -n 'PROMOTE_WAIT\[user.id\]' modules/start.py | head -1 | cut -d: -f1)
if [ -n "$LINE" ]; then
    sed -n "$((LINE-3)),$((LINE+15))p" modules/start.py
fi
echo ""

echo "═══ ۴. admin_permissions schema ═══"
python3 -c "
import sqlite3
from config import DATABASE_PATH
conn = sqlite3.connect(DATABASE_PATH)
c = conn.cursor()
c.execute('PRAGMA table_info(admin_permissions)')
for r in c.fetchall(): print(f'  {r}')
conn.close()
"
echo ""

echo "═══════════════════════════════════════════════════"
} | tee ~/DIAG_PERM_SAVE.txt

echo ""
echo "✅ فایل: ~/DIAG_PERM_SAVE.txt"
