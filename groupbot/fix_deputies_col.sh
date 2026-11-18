#!/data/data/com.termux/files/usr/bin/bash

DB=database.py
TS=$(date +%Y%m%d_%H%M%S)

cp "$DB" "$DB.bak_depcol_$TS"
echo "✅ بک‌آپ: $DB.bak_depcol_$TS"
echo ""

source venv/bin/activate

python3 << 'PYEOF'
DB = "/data/data/com.termux/files/home/groupbot/database.py"

with open(DB, "r", encoding="utf-8") as f:
    content = f.read()

# fix INSERT to deputies
old = '''        # ۲. جدول deputies (چون is_deputy از این می‌خونه)
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
        )'''

new = '''        # ۲. جدول deputies (چون is_deputy از این می‌خونه)
        # ستون‌های واقعی: chat_id, user_id, first_name, username, added_by, added_at
        c.execute("""
            CREATE TABLE IF NOT EXISTS deputies (
                chat_id INTEGER,
                user_id INTEGER,
                first_name TEXT,
                username TEXT,
                added_by TEXT,
                added_at TEXT,
                PRIMARY KEY (chat_id, user_id)
            )
        """)
        from datetime import datetime as _dt
        c.execute(
            "INSERT OR REPLACE INTO deputies (chat_id, user_id, first_name, added_by, added_at) VALUES (?, ?, ?, ?, ?)",
            (chat_id, user_id, name, "bot", _dt.now().strftime("%Y-%m-%d %H:%M:%S"))
        )'''

if old in content:
    content = content.replace(old, new, 1)
    print("✅ INSERT deputies اصلاح شد")
else:
    print("⚠️ الگو پیدا نشد — تلاش با regex")
    import re
    pattern = r'c\.execute\(\s*"INSERT OR REPLACE INTO deputies \(chat_id, user_id, name\).*?\n\s*\)'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        old_block = match.group(0)
        new_block = '''c.execute(
            "INSERT OR REPLACE INTO deputies (chat_id, user_id, first_name, added_by, added_at) VALUES (?, ?, ?, ?, ?)",
            (chat_id, user_id, name, "bot", __import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )'''
        content = content.replace(old_block, new_block, 1)
        print("✅ با regex اصلاح شد")
    else:
        print("❌ پیدا نشد")
        exit(1)

with open(DB, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ ذخیره شد")
PYEOF

echo ""

if python3 -m py_compile "$DB" 2>&1; then
    echo "✅ کامپایل OK"
else
    echo "❌ خطا — rollback!"
    cp "$DB.bak_depcol_$TS" "$DB"
    exit 1
fi
echo ""

echo "─── تست عملی ───"
python3 << 'PYEOF'
import sys
sys.path.insert(0, '.')
from database import add_admin_to_db, is_deputy, remove_admin_from_db

chat_id = -1004349813270
user_id = 8401175719  # کاربر تست

print(f"قبل: is_deputy = {is_deputy(chat_id, user_id)}")
add_admin_to_db(chat_id, user_id, "Siavash")
print(f"بعد: is_deputy = {is_deputy(chat_id, user_id)}")
PYEOF
echo ""

echo "═══════════════════════════════════════════════════"
echo "✅ Fix انجام شد"
echo ""
echo "🎯 ری‌استارت:"
echo "pkill -9 -f 'python3 -u'; sleep 3; rm -f .bot.lock; nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 & sleep 15"
echo "═══════════════════════════════════════════════════"
