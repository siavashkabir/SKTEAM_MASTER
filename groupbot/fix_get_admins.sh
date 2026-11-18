#!/data/data/com.termux/files/usr/bin/bash

DB=database.py
TS=$(date +%Y%m%d_%H%M%S)

cp "$DB" "$DB.bak_getadmins_$TS"
echo "✅ بک‌آپ: $DB.bak_getadmins_$TS"
echo ""

source venv/bin/activate

python3 << 'PYEOF'
DB = "/data/data/com.termux/files/home/groupbot/database.py"

with open(DB, "r", encoding="utf-8") as f:
    content = f.read()

# اگه هست، skip
if "def get_group_admins(" in content:
    print("⚠️ get_group_admins از قبل هست")
    exit(0)

# اضافه کن به آخر فایل
new_func = '''

def get_group_admins(chat_id):
    """گرفتن همه ادمین‌های گروه از جدول group_admins"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        c.execute("SELECT user_id, name FROM group_admins WHERE chat_id=?", (chat_id,))
        rows = c.fetchall()
        conn.close()
        return [{"user_id": r[0], "name": r[1]} for r in rows]
    except Exception as e:
        print(f"[DB ERR] get_group_admins: {e}")
        return []


def get_admin_list(chat_id):
    """گرفتن لیست ادمین‌ها (alias)"""
    return get_group_admins(chat_id)
'''

content += new_func

with open(DB, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ get_group_admins اضافه شد")
PYEOF

echo ""

if python3 -m py_compile "$DB" 2>&1; then
    echo "✅ کامپایل OK"
else
    echo "❌ خطا — rollback!"
    cp "$DB.bak_getadmins_$TS" "$DB"
    exit 1
fi
echo ""

# تست
echo "─── تست ───"
python3 << 'PYEOF'
import sys
sys.path.insert(0, '.')
try:
    from database import get_group_admins
    admins = get_group_admins(-1004349813270)
    print(f"✅ get_group_admins: {admins}")
except Exception as e:
    print(f"❌ خطا: {e}")
PYEOF
echo ""

echo "═══════════════════════════════════════════════════"
echo "✅ Fix انجام شد"
echo ""
echo "🎯 ری‌استارت:"
echo "pkill -9 -f 'python3 -u'; sleep 3; rm -f .bot.lock; nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 & sleep 15"
echo "═══════════════════════════════════════════════════"
