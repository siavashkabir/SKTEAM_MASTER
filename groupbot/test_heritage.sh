#!/data/data/com.termux/files/usr/bin/bash

source venv/bin/activate

python3 << 'PYEOF'
import asyncio
from telegram import Bot
from config import BOT_TOKEN

async def test():
    bot = Bot(token=BOT_TOKEN)
    cid = -1004463882429
    try:
        chat = await bot.get_chat(cid)
        print(f"✅ chat: {chat.title}")
        print(f"   type: {chat.type}")
        
        admins = await bot.get_chat_administrators(cid)
        print(f"\n📊 تعداد ادمین‌ها: {len(admins)}")
        for i, a in enumerate(admins, 1):
            u = a.user
            uname = f"@{u.username}" if u.username else "(no username)"
            is_bot = "🤖" if u.is_bot else "👤"
            print(f"  {i}. {is_bot} {u.first_name} {uname} - {a.status}")
    except Exception as e:
        print(f"❌ خطا: {e}")
    await bot.close()

asyncio.run(test())
PYEOF
