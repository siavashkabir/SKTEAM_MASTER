#!/data/data/com.termux/files/usr/bin/bash

source venv/bin/activate

python3 << 'PYEOF'
US = "userbot_service.py"

with open(US, "r", encoding="utf-8") as f:
    content = f.read()

# اضافه کردن no_updates=True
old = '''    app = Client(
        name="userbot_service",
        api_id=API_ID,
        api_hash=API_HASH,
        session_string=STRING_SESSION,
    )'''

new = '''    app = Client(
        name="userbot_service",
        api_id=API_ID,
        api_hash=API_HASH,
        session_string=STRING_SESSION,
        no_updates=True,  # ★ بدون update handler
    )'''

if old in content:
    content = content.replace(old, new, 1)
    print("✅ no_updates=True اضافه شد")
else:
    print("⚠️ الگو پیدا نشد")
    idx = content.find("app = Client(")
    if idx > 0:
        print(content[idx:idx+300])

with open(US, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ ذخیره شد")
PYEOF

echo ""

if python3 -m py_compile userbot_service.py 2>&1; then
    echo "✅ کامپایل OK"
else
    echo "❌ خطا"
    exit 1
fi
echo ""

# ری‌استارت userbot
pkill -9 -f "userbot_service.py" 2>/dev/null
sleep 2

# پاک کردن جدول برای تست دوباره
python3 -c "
import sqlite3
from config import DATABASE_PATH
conn = sqlite3.connect(DATABASE_PATH)
c = conn.cursor()
c.execute(\"UPDATE userbot_join_queue SET status='pending' WHERE status='done'\")
c.execute('DELETE FROM userbot_join_queue')
conn.commit()
conn.close()
print('✅ جدول پاک شد')
"

nohup python3 -u userbot_service.py > ~/userbot_service.log 2>&1 &
sleep 8

echo ""
echo "─── لاگ ───"
tail -n 15 ~/userbot_service.log

echo ""
echo "═══════════════════════════════════════════════════"
echo "✅ Fix انجام شد"
echo ""
echo "🎯 حالا این رو بزن:"
echo "python3 trigger_autojoin.py"
echo ""
echo "بعد ۱۵ ثانیه صبر کن، این رو بزن:"
echo "tail -n 30 ~/userbot_service.log"
echo "═══════════════════════════════════════════════════"
