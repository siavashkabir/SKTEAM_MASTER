#!/data/data/com.termux/files/usr/bin/bash

DB=database.py
TS=$(date +%Y%m%d_%H%M%S)

cp "$DB" "$DB.bak_depsync_$TS"
echo "✅ بک‌آپ: $DB.bak_depsync_$TS"
echo ""

source venv/bin/activate

python3 << 'PYEOF'
DB = "/data/data/com.termux/files/home/groupbot/database.py"

with open(DB, "r", encoding="utf-8") as f:
    content = f.read()

# تابع add_admin_to_db رو بازنویسی کن
old = '''def add_admin_to_db(chat_id, user_id, name):
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
        return False'''

new = '''def add_admin_to_db(chat_id, user_id, name):
    """اضافه کردن ادمین به هر دو جدول group_admins و deputies"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        
        # ۱. گروه group_admins
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
        
        # ۲. جدول deputies (چون is_deputy از این می‌خونه)
        c.execute("""
            CREATE TABLE IF NOT EXISTS deputies (
                chat_id INTEGER,
                user_id INTEGER,
                name TEXT,
                PRIMARY KEY (chat_id, user_id)
            )
        """)
        c.execute(
            "INSERT OR REPLACE INTO deputies (chat_id, user_id, name) VALUES (?, ?, ?)",
            (chat_id, user_id, name)
        )
        
        conn.commit()
        conn.close()
        print(f"[DB] add_admin_to_db: chat={chat_id}, user={user_id}, name={name} (both tables)")
        return True
    except Exception as e:
        print(f"[DB ERR] add_admin_to_db: {e}")
        return False'''

if old in content:
    content = content.replace(old, new, 1)
    print("✅ add_admin_to_db اصلاح شد")
else:
    print("⚠️ الگو پیدا نشد — تلاش با regex")
    import re
    pattern = r'def add_admin_to_db\(chat_id, user_id, name\):.*?return False'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        content = content.replace(match.group(0), new, 1)
        print("✅ با regex اصلاح شد")
    else:
        print("❌ پیدا نشد")
        exit(1)

# تابع remove_admin_from_db هم اضافه کن اگه نیست
if "def remove_admin_from_db" not in content:
    remove_func = '''

def remove_admin_from_db(chat_id, user_id):
    """حذف ادمین از هر دو جدول"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        c.execute("DELETE FROM group_admins WHERE chat_id=? AND user_id=?", (chat_id, user_id))
        c.execute("DELETE FROM deputies WHERE chat_id=? AND user_id=?", (chat_id, user_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[DB ERR] remove_admin_from_db: {e}")
        return False

'''
    content += remove_func
    print("✅ remove_admin_from_db اضافه شد")

with open(DB, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ ذخیره شد")
PYEOF

echo ""

if python3 -m py_compile "$DB" 2>&1; then
    echo "✅ کامپایل OK"
else
    echo "❌ خطا — rollback!"
    cp "$DB.bak_depsync_$TS" "$DB"
    exit 1
fi
echo ""

echo "─── تست ───"
python3 << 'PYEOF'
import sys
sys.path.insert(0, '.')
from database import add_admin_to_db, is_deputy, remove_admin_from_db

chat_id = -1004349813270
user_id = 8820561431  # Rozhan

print(f"قبل از add: is_deputy = {is_deputy(chat_id, user_id)}")
add_admin_to_db(chat_id, user_id, "Rozhan Test")
print(f"بعد از add: is_deputy = {is_deputy(chat_id, user_id)}")

# پاک کن
remove_admin_from_db(chat_id, user_id)
print(f"بعد از remove: is_deputy = {is_deputy(chat_id, user_id)}")
PYEOF
echo ""

echo "═══════════════════════════════════════════════════"
echo "✅ Fix انجام شد"
echo ""
echo "🎯 ری‌استارت:"
echo "pkill -9 -f 'python3 -u'; sleep 3; rm -f .bot.lock; nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 & sleep 15"
echo "═══════════════════════════════════════════════════"
