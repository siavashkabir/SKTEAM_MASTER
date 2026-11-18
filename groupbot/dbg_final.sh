#!/data/data/com.termux/files/usr/bin/bash

source venv/bin/activate

{
echo "═══ ۱. chat_id های واقعی گروه‌ها ═══"
python3 << 'PYEOF'
import asyncio
from telegram import Bot
from config import BOT_TOKEN

async def test():
    bot = Bot(token=BOT_TOKEN)
    # آخرین آپدیت‌ها
    try:
        updates = await bot.get_updates(limit=20, timeout=2)
        print(f"تعداد updates: {len(updates)}")
        for u in updates[-10:]:
            if u.message:
                print(f"  msg chat={u.message.chat.id} title={u.message.chat.title}")
            elif u.callback_query and u.callback_query.message:
                print(f"  cb chat={u.callback_query.message.chat.id} title={u.callback_query.message.chat.title}")
    except Exception as e:
        print(f"خطا: {e}")
    await bot.close()

asyncio.run(test())
PYEOF
echo ""

echo "═══ ۲. تست دستی برای هر گروه ═══"
python3 << 'PYEOF'
import asyncio
from telegram import Bot
from config import BOT_TOKEN

async def test():
    bot = Bot(token=BOT_TOKEN)
    for chat_id in [-10044639682429, -100191141484, -1004349813270]:
        try:
            chat = await bot.get_chat(chat_id)
            print(f"chat {chat_id}: title={chat.title}")
            admins = await bot.get_chat_administrators(chat_id)
            print(f"  admins: {len(admins)}")
            for a in admins[:5]:
                print(f"    - {a.user.first_name} (id={a.user.id}, status={a.status})")
        except Exception as e:
            print(f"chat {chat_id}: ERROR {e}")
    await bot.close()

asyncio.run(test())
PYEOF
echo ""

echo "═══ ۳. آخرین خطاهای CFG MEMBERS ═══"
tail -n 500 ~/groupbot_bot.log | grep -B 1 -A 2 "CFG MEMBERS ERR" | tail -20
echo ""

} | tee ~/DBG_FINAL.txt

echo "✅ فایل: ~/DBG_FINAL.txt"
