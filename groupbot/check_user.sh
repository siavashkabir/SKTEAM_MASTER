#!/data/data/com.termux/files/usr/bin/bash

{
echo "═══════════════════════════════════════════════════"
echo "🔍 چک کاربر 8401175719"
echo "═══════════════════════════════════════════════════"
echo ""

source venv/bin/activate

python3 << 'PYEOF'
import sqlite3
from config import DATABASE_PATH

conn = sqlite3.connect(DATABASE_PATH)
c = conn.cursor()

chat_id = -1004349813270
user_id = 8401175719

print("=== group_admins ===")
c.execute("SELECT * FROM group_admins WHERE chat_id=?", (chat_id,))
rows = c.fetchall()
for r in rows: print(f"  {r}")
print(f"تعداد: {len(rows)}")
print()

print(f"=== آیا {user_id} توی group_admins هست؟ ===")
c.execute("SELECT * FROM group_admins WHERE chat_id=? AND user_id=?", (chat_id, user_id))
r = c.fetchone()
print(f"  نتیجه: {r}")
print()

print("=== admin_permissions ===")
c.execute("SELECT * FROM admin_permissions WHERE chat_id=? AND user_id=?", (chat_id, user_id))
rows = c.fetchall()
for r in rows: print(f"  {r}")
print(f"تعداد: {len(rows)}")
print()

print("=== تست get_group_admins ===")
try:
    from database import get_group_admins
    admins = get_group_admins(chat_id)
    for a in admins: print(f"  {a}")
except Exception as e:
    print(f"  خطا: {e}")

conn.close()
PYEOF
echo ""

echo "═══ کد پیکربندی توی start.py (خط ۲۱۲۵ تا ۲۱۴۰) ═══"
sed -n '2125,2140p' modules/start.py | cat -n
echo ""

echo "═══ admin_list_menu چطور call می‌شه ═══"
grep -n "admin_list_menu\|get_group_admins" modules/start.py
echo ""

echo "═══════════════════════════════════════════════════"
} | tee ~/CHECK_USER.txt

echo ""
echo "✅ فایل: ~/CHECK_USER.txt"
