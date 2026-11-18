#!/data/data/com.termux/files/usr/bin/bash

DB=database.py

echo "═══════════════════════════════════════════════════"
echo "🔍 چک: fix_deputy_sync اعمال شده؟"
echo "═══════════════════════════════════════════════════"
echo ""

echo "─── add_admin_to_db فعلی ───"
LINE=$(grep -n "def add_admin_to_db" "$DB" | head -1 | cut -d: -f1)
if [ -n "$LINE" ]; then
    sed -n "${LINE},$((LINE+40))p" "$DB"
fi
echo ""

echo "─── جدول deputies هست؟ ───"
source venv/bin/activate
python3 << 'PYEOF'
import sqlite3
from config import DATABASE_PATH

conn = sqlite3.connect(DATABASE_PATH)
c = conn.cursor()

# جدول‌های موجود
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in c.fetchall()]
print(f"جدول‌ها: {tables}")
print()

for t in ['deputies', 'group_admins']:
    if t in tables:
        c.execute(f"PRAGMA table_info({t})")
        print(f"=== {t} ستون‌ها ===")
        for r in c.fetchall(): print(f"  {r}")
        c.execute(f"SELECT * FROM {t} WHERE chat_id=-1004349813270")
        print(f"=== {t} داده‌ها ===")
        for r in c.fetchall(): print(f"  {r}")
        print()
    else:
        print(f"❌ جدول {t} وجود نداره")
        print()

# تست is_deputy
print("=== تست is_deputy ===")
try:
    from database import is_deputy
    for uid in [8401175719, 8820561431, 8250087472]:
        print(f"  is_deputy(-1004349813270, {uid}): {is_deputy(-1004349813270, uid)}")
except Exception as e:
    print(f"  خطا: {e}")

conn.close()
PYEOF
echo ""

echo "═══════════════════════════════════════════════════"
