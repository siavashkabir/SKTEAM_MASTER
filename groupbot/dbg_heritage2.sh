#!/data/data/com.termux/files/usr/bin/bash

source venv/bin/activate

{
echo "═══ ۱. لاگ CFG ═══"
tail -n 100 ~/groupbot_bot.log | grep "CFG" | tail -10
echo ""

echo "═══ ۲. لاگ ADMIN PERMS ═══"
tail -n 100 ~/groupbot_bot.log | grep "ADMIN PERMS" | tail -10
echo ""

echo "═══ ۳. کد فعلی حلقه ترکیبی (line 1575-1630) ═══"
sed -n '1575,1630p' modules/start.py | cat -n
echo ""

echo "═══ ۴. تست get_chat_administrators برای HERITAGE ═══"
python3 << 'PYEOF'
import asyncio
from telegram import Bot
from config import BOT_TOKEN

async def test():
    bot = Bot(token=BOT_TOKEN)
    for chat_id in [-10044639682429, -1004349813270]:
        try:
            admins = await bot.get_chat_administrators(chat_id)
            print(f"chat {chat_id}: {len(admins)} admins")
            for a in admins[:3]:
                print(f"  - {a.user.first_name} (id={a.user.id}, status={a.status})")
        except Exception as e:
            print(f"chat {chat_id}: ERROR {e}")
    await bot.close()

asyncio.run(test())
PYEOF
echo ""

} | tee ~/DBG_HERITAGE2.txt

echo "✅ فایل: ~/DBG_HERITAGE2.txt"
