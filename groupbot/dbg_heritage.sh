#!/data/data/com.termux/files/usr/bin/bash

source venv/bin/activate

python3 << 'PYEOF'
import sqlite3
from config import DATABASE_PATH

conn = sqlite3.connect(DATABASE_PATH)
c = conn.cursor()

# چک کن گروه HERITAGE توی دیتابیس هست
print("═══ گروه‌ها ═══")
c.execute("SELECT chat_id, title FROM groups")
for r in c.fetchall():
    print(f"  {r}")
print()

# چک group_admins برای همه گروه‌ها
print("═══ group_admins ═══")
c.execute("SELECT chat_id, user_id, name FROM group_admins")
for r in c.fetchall():
    print(f"  {r}")
print()

conn.close()
PYEOF
echo ""

echo "═══ لاگ اخیر — CFG ═══"
tail -n 200 ~/groupbot_bot.log | grep -E "CFG|HANDLER DEBUG.*menu_admin" | tail -20
echo ""

echo "═══ لاگ اخیر — ADMIN PERMS ERR ═══"
tail -n 200 ~/groupbot_bot.log | grep "ADMIN PERMS ERR" | tail -5
echo ""

