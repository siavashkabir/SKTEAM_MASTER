#!/data/data/com.termux/files/usr/bin/bash

source venv/bin/activate

python3 << 'PYEOF'
import sqlite3
from config import DATABASE_PATH

conn = sqlite3.connect(DATABASE_PATH)
c = conn.cursor()

# آخرین رکوردهای members — chat_id های جدید
print("═══ آخرین ۱۰ chat_id توی members ═══")
c.execute("SELECT DISTINCT chat_id FROM members ORDER BY rowid DESC LIMIT 10")
for r in c.fetchall():
    # برای هر chat_id، تعداد اعضا
    c2 = conn.cursor()
    c2.execute("SELECT COUNT(*) FROM members WHERE chat_id=?", (r[0],))
    count = c2.fetchone()[0]
    # آخرین پیام
    c2.execute("SELECT first_name, username FROM members WHERE chat_id=? ORDER BY rowid DESC LIMIT 1", (r[0],))
    last = c2.fetchone()
    print(f"  {r[0]}: {count} عضو، آخرین: {last}")

print()
print("═══ گروه‌ها ═══")
c.execute("SELECT chat_id, title FROM groups")
for r in c.fetchall():
    print(f"  {r[0]} | {r[1]}")

print()
print("═══ chat_id HERITAGE که کاربر Siavash هست ═══")
# آیدی Siavash = 7955185125
c.execute("SELECT DISTINCT chat_id FROM members WHERE user_id=7955185125")
for r in c.fetchall():
    print(f"  {r[0]}")

conn.close()
PYEOF
echo ""

