#!/data/data/com.termux/files/usr/bin/bash

source venv/bin/activate

{
echo "═══ ۱. chat_id که توی callback میاد برای HERITAGE ═══"
tail -n 200 ~/groupbot_bot.log | grep "HANDLER DEBUG.*menu_admin" | tail -10
echo ""

echo "═══ ۲. خطای get_chat_administrators ═══"
tail -n 300 ~/groupbot_bot.log | grep -B 2 -A 5 "CFG MEMBERS\|ChatAdminRequired\|Forbidden" | tail -30
echo ""

echo "═══ ۳. چک chat.id واقعی برای همه گروه‌های دیتابیس ═══"
python3 << 'PYEOF'
import sqlite3
from config import DATABASE_PATH
conn = sqlite3.connect(DATABASE_PATH)
c = conn.cursor()
c.execute("SELECT chat_id, title FROM groups")
for r in c.fetchall():
    print(f"  chat_id={r[0]}, title={r[1]}")
conn.close()
PYEOF
echo ""

echo "═══ ۴. تست با هر chat_id از دیتابیس ═══"
python3 << 'PYEOF'
import asyncio
from telegram import Bot
from config import BOT_TOKEN

async def test():
    bot = Bot(token=BOT_TOKEN)
    for chat_id in [-10044639682429, -1004349813270, -100191141484]:
        try:
            admins = await bot.get_chat_administrators(chat_id)
            print(f"✅ chat {chat_id}: {len(admins)} admins")
            for a in admins[:3]:
                print(f"     - {a.user.first_name} ({a.status})")
        except Exception as e:
            print(f"❌ chat {chat_id}: {e}")
    await bot.close()

asyncio.run(test())
PYEOF
echo ""

} | tee ~/DBG_H3.txt
