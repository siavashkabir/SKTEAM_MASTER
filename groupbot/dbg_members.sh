#!/data/data/com.termux/files/usr/bin/bash

source venv/bin/activate

{
echo "═══ ۱. ساختار جدول members ═══"
python3 << 'PYEOF'
import sqlite3
from config import DATABASE_PATH
conn = sqlite3.connect(DATABASE_PATH)
c = conn.cursor()
c.execute("PRAGMA table_info(members)")
print("ستون‌های members:")
for r in c.fetchall(): print(f"  {r}")
print()

# نمونه
c.execute("SELECT * FROM members LIMIT 3")
print("نمونه:")
for r in c.fetchall(): print(f"  {r}")
conn.close()
PYEOF
echo ""

echo "═══ ۲. خطای HERITAGE ═══"
tail -n 300 ~/groupbot_bot.log | grep -B 2 -A 10 "CFG MEMBERS ERR\|get_chat_administrators\|Forbidden\|ChatAdminRequired" | tail -40
echo ""

echo "═══ ۳. کد ترکیبی توی خط 1590-1620 ═══"
sed -n '1590,1620p' modules/start.py | cat -n
echo ""

} | tee ~/DBG_MEMBERS.txt

echo "✅ فایل: ~/DBG_MEMBERS.txt"
