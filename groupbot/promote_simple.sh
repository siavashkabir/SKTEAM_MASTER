#!/data/data/com.termux/files/usr/bin/bash

source venv/bin/activate

python3 << 'PYEOF'
import asyncio
from telegram import Bot
from config import BOT_TOKEN

USERBOT_ID = 8250087472
CHATS = [-1004463882429, -1004349813270]

async def check_and_promote():
    bot = Bot(token=BOT_TOKEN)
    
    for cid in CHATS:
        print(f"\n═══ گروه {cid} ═══")
        try:
            # مستقیم با ID چک کن
            ub = await bot.get_chat_member(cid, USERBOT_ID)
            print(f"  ✅ userbot: {ub.user.first_name} (status={ub.status})")
            
            if ub.status == "administrator":
                print(f"  ✅ از قبل ادمینه")
            elif ub.status == "member":
                await bot.promote_chat_member(
                    chat_id=cid,
                    user_id=USERBOT_ID,
                    can_delete_messages=True,
                    can_restrict_members=True,
                    can_pin_messages=True,
                    can_invite_users=True,
                    can_manage_video_chats=True,
                )
                print(f"  ✅ promote شد")
        except Exception as e:
            print(f"  ❌ {e}")
        
        # ۵ ثانیه بین درخواست‌ها
        await asyncio.sleep(5)
    
    await bot.close()

asyncio.run(check_and_promote())
PYEOF
