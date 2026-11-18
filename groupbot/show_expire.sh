#!/data/data/com.termux/files/usr/bin/bash

echo "═══════════════════════════════════════════════════"
echo "🔍 دیاگ get_expire"
echo "═══════════════════════════════════════════════════"
echo ""

echo "─── ۱. تابع get_expire ───"
grep -n "def get_expire" modules/subscription.py
LINE=$(grep -n "def get_expire" modules/subscription.py | head -1 | cut -d: -f1)
echo "خط: $LINE"
sed -n "${LINE},$((LINE+30))p" modules/subscription.py
echo ""

echo "─── ۲. تست get_expire ───"
source venv/bin/activate
python3 << 'PYEOF'
from modules.subscription import get_expire, DATE_FMT
from datetime import datetime

print(f"DATE_FMT: {DATE_FMT}")
print(f"now: {datetime.now()}")
print()

for chat_id in [-1004349813270, -100191141484]:
    try:
        r = get_expire(chat_id)
        print(f"chat {chat_id}: get_expire = {r!r} (type: {type(r).__name__})")
    except Exception as e:
        print(f"chat {chat_id}: ERROR: {e}")
        import traceback
        traceback.print_exc()
PYEOF
echo ""

echo "─── ۳. دیتابیس مستقیم ───"
source venv/bin/activate
python3 << 'PYEOF'
import sqlite3
from config import DATABASE_PATH

conn = sqlite3.connect(DATABASE_PATH)
c = conn.cursor()

for chat_id in [-1004349813270, -100191141484]:
    print(f"=== chat {chat_id} ===")
    
    print("groups:")
    c.execute("SELECT * FROM groups WHERE chat_id=?", (chat_id,))
    for r in c.fetchall(): print(f"  {r}")
    
    print("subscriptions:")
    c.execute("SELECT * FROM subscriptions WHERE chat_id=?", (chat_id,))
    for r in c.fetchall(): print(f"  {r}")
    print()

conn.close()
PYEOF
echo ""

echo "═══════════════════════════════════════════════════"
