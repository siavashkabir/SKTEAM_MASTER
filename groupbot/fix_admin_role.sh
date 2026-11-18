#!/data/data/com.termux/files/usr/bin/bash

DB=database.py
TS=$(date +%Y%m%d_%H%M%S)

cp "$DB" "$DB.bak_adminrole_$TS"
echo "✅ بک‌آپ: $DB.bak_adminrole_$TS"
echo ""

source venv/bin/activate

python3 << 'PYEOF'
DB = "/data/data/com.termux/files/home/groupbot/database.py"

with open(DB, "r", encoding="utf-8") as f:
    content = f.read()

# fix add_admin_to_db — فقط group_admins
old_start = 'def add_admin_to_db(chat_id, user_id, name):'
old_end = '# ═══════════════════════════════════════════════════\n# Group Admins — اضافه شده در fix v5'

# پیدا کردن تابع فعلی
import re
pattern = r'def add_admin_to_db\(chat_id, user_id, name\):.*?(?=\n\ndef |\n\n# |\Z)'
match = re.search(pattern, content, re.DOTALL)

if not match:
    print("❌ add_admin_to_db پیدا نشد")
    exit(1)

old_func = match.group(0)

new_func = '''def add_admin_to_db(chat_id, user_id, name):
    """اضافه کردن ادمین به جدول group_admins"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS group_admins (
                chat_id INTEGER,
                user_id INTEGER,
                name TEXT,
                PRIMARY KEY (chat_id, user_id)
            )
        """)
        c.execute(
            "INSERT OR REPLACE INTO group_admins (chat_id, user_id, name) VALUES (?, ?, ?)",
            (chat_id, user_id, name)
        )
        conn.commit()
        conn.close()
        print(f"[DB] add_admin_to_db: chat={chat_id}, user={user_id}, name={name}")
        return True
    except Exception as e:
        print(f"[DB ERR] add_admin_to_db: {e}")
        return False


def is_admin(chat_id, user_id):
    """چک می‌کنه که کاربر ادمین گروهه"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        c.execute("SELECT user_id FROM group_admins WHERE chat_id=? AND user_id=?", (chat_id, user_id))
        row = c.fetchone()
        conn.close()
        return row is not None
    except Exception as e:
        print(f"[IS ADMIN ERR] {e}")
        return False


def get_all_admins(chat_id):
    """گرفتن همه ادمین‌های گروه"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        c.execute("SELECT user_id, name FROM group_admins WHERE chat_id=?", (chat_id,))
        rows = c.fetchall()
        conn.close()
        return rows
    except Exception as e:
        print(f"[GET ALL ADMINS ERR] {e}")
        return []


def remove_admin_from_db(chat_id, user_id):
    """حذف ادمین از جدول group_admins"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        c.execute("DELETE FROM group_admins WHERE chat_id=? AND user_id=?", (chat_id, user_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[DB ERR] remove_admin_from_db: {e}")
        return False
'''

content = content.replace(old_func, new_func, 1)
print("✅ add_admin_to_db + is_admin اضافه شد")

with open(DB, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ ذخیره شد")
PYEOF

echo ""

if python3 -m py_compile "$DB" 2>&1; then
    echo "✅ کامپایل OK"
else
    echo "❌ خطا — rollback!"
    cp "$DB.bak_adminrole_$TS" "$DB"
    exit 1
fi
echo ""

echo "═══════════════════════════════════════════════════"
echo "✅ Fix انجام شد"
echo ""
echo "🎯 ری‌استارت:"
echo "pkill -9 -f 'python3 -u'; sleep 3; rm -f .bot.lock; nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 & sleep 15"
echo "═══════════════════════════════════════════════════"
