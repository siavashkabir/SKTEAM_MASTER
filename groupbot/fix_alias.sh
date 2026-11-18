#!/data/data/com.termux/files/usr/bin/bash

DB=database.py
TS=$(date +%Y%m%d_%H%M%S)

cp "$DB" "$DB.bak_alias_$TS"
echo "✅ بک‌آپ: $DB.bak_alias_$TS"

source venv/bin/activate

python3 << 'PYEOF'
DB = "/data/data/com.termux/files/home/groupbot/database.py"

with open(DB, "r", encoding="utf-8") as f:
    content = f.read()

if "def admin_list_menu" in content:
    print("⚠️ از قبل هست")
    exit(0)

# اضافه کردن تابع در آخر فایل
new_func = '''

def admin_list_menu(uid, chat_id, admins):
    """Alias — استفاده از همون تابع admin_perms"""
    try:
        from modules.admin_perms import admin_list_menu as _alm
        return _alm(uid, chat_id, admins)
    except Exception as e:
        print(f"[ADMIN LIST ALIAS ERR] {e}")
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ خطا در ساخت منو", callback_data="menu_close:" + str(uid))]
        ])
'''

content += new_func

with open(DB, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ admin_list_menu به database.py اضافه شد")
PYEOF

echo ""

if python3 -m py_compile "$DB" 2>&1; then
    echo "✅ کامپایل OK"
else
    echo "❌ خطا — rollback!"
    cp "$DB.bak_alias_$TS" "$DB"
    exit 1
fi
echo ""

echo "─── تست ───"
python3 << 'PYEOF'
import sys
sys.path.insert(0, '.')
try:
    from database import admin_list_menu, get_group_admins
    print("✅ import OK")
    admins = get_group_admins(-1004349813270)
    print(f"admins: {len(admins)}")
    kb = admin_list_menu(7955185125, -1004349813270, admins)
    print(f"✅ admin_list_menu کار می‌کنه ({len(kb.inline_keyboard)} دکمه)")
except Exception as e:
    print(f"❌ خطا: {e}")
    import traceback
    traceback.print_exc()
PYEOF
echo ""

echo "═══════════════════════════════════════════════════"
echo "✅ Fix انجام شد"
echo ""
echo "🎯 ری‌استارت:"
echo "pkill -9 -f 'python3 -u'; sleep 3; rm -f .bot.lock; nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 & sleep 15"
echo "═══════════════════════════════════════════════════"
