#!/usr/bin/env bash

echo "═══════════════════════════════════════════════════"
echo "📊 وضعیت کلی"
echo "═══════════════════════════════════════════════════"
echo ""

echo "─── ۱. پروسه‌های Termux ───"
pgrep -af "python3 -u main.py" || echo "❌ ربات Manager خاموش"
pgrep -af "userbot_service.py" || echo "❌ userbot خاموش"
echo ""

echo "─── ۲. آخرین خطاهای ربات ───"
tail -n 200 ~/groupbot_bot.log | grep -E "NameError|Traceback|ERROR" | tail -5 || echo "✅ بدون خطا"
echo ""

echo "─── ۳. promote userbot در دیتابیس ───"
source venv/bin/activate
python3 << 'PYEOF'
import sqlite3
from config import DATABASE_PATH
conn = sqlite3.connect(DATABASE_PATH)
c = conn.cursor()
c.execute("SELECT chat_id, user_id, name FROM group_admins WHERE user_id=8250087472")
rows = c.fetchall()
if rows:
    print(f"✅ userbot در {len(rows)} گروه ذخیره شده:")
    for r in rows: print(f"  {r}")
else:
    print("❌ userbot توی group_admins نیست")
conn.close()
PYEOF
echo ""

echo "─── ۴. Ubuntu — چک موزیک‌پلیر ───"
proot-distro login ubuntu -- bash -c "
cd ~/music_player 2>/dev/null && source venv/bin/activate 2>/dev/null && python3 -c \"
try:
    import pyrogram
    print('✅ pyrogram: OK')
except: print('❌ pyrogram')
try:
    import pytgcalls
    print('✅ pytgcalls: OK')
except: print('❌ pytgcalls')
try:
    import ntgcalls
    print('✅ ntgcalls: OK')
except: print('❌ ntgcalls')
\"
" 2>&1 | tail -10

echo ""
echo "═══════════════════════════════════════════════════"
