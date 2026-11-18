#!/data/data/com.termux/files/usr/bin/bash

source venv/bin/activate

python3 << 'PYEOF'
from modules.nsfw import is_enabled, is_nsfw_sub_activated, is_group_toggle_on, get_setting
from config import OWNER_ID

chat_id = -1004349813270

print(f"chat_id: {chat_id}")
print()

# چک هر کدوم
try:
    print(f"is_group_toggle_on: {is_group_toggle_on(chat_id)}")
except Exception as e:
    print(f"is_group_toggle_on ERR: {e}")

try:
    print(f"is_nsfw_sub_activated: {is_nsfw_sub_activated(chat_id)}")
except Exception as e:
    print(f"is_nsfw_sub_activated ERR: {e}")
    import traceback
    traceback.print_exc()

try:
    print(f"is_enabled: {is_enabled(chat_id)}")
except Exception as e:
    print(f"is_enabled ERR: {e}")
    import traceback
    traceback.print_exc()
print()

# چک تنظیمات
print("تنظیمات NSFW:")
print(f"  nsfw_enabled: {get_setting(chat_id, 'nsfw_enabled', '?')}")
print(f"  nsfw_sub_activated: {get_setting(chat_id, 'nsfw_sub_activated', '?')}")
print()

# ساختار جداول
import sqlite3
from config import DATABASE_PATH
conn = sqlite3.connect(DATABASE_PATH)
c = conn.cursor()

print("nsfw_subs (اگه هست):")
try:
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%nsfw%'")
    for r in c.fetchall(): print(f"  جدول: {r[0]}")
except: pass
print()

print("subscriptions گروه تست:")
c.execute("SELECT * FROM subscriptions WHERE chat_id=?", (chat_id,))
for r in c.fetchall(): print(f"  {r}")
print()

print("groups گروه تست:")
c.execute("SELECT * FROM groups WHERE chat_id=?", (chat_id,))
for r in c.fetchall(): print(f"  {r}")

conn.close()
PYEOF
echo ""
echo "═══════════════════════════════════════════════════"

echo "─── تابع is_nsfw_sub_activated ───"
LINE=$(grep -n "def is_nsfw_sub_activated" modules/nsfw.py | head -1 | cut -d: -f1)
if [ -n "$LINE" ]; then
    sed -n "${LINE},$((LINE+20))p" modules/nsfw.py
fi
