#!/usr/bin/env bash

sleep 150  # صبر برای رفع Flood

source venv/bin/activate

python3 << 'PYEOF'
import asyncio
from telegram import Bot
from config import BOT_TOKEN

CHATS = [-1004463882429, -1004349813270]


async def promote_all():
    bot = Bot(token=BOT_TOKEN)
    for cid in CHATS:
        print(f"\n═══ {cid} ═══")
        try:
            # با username بگیر
            ub = await bot.get_chat_member(cid, "@Skmusic001")
            print(f"  userbot: {ub.user.first_name} (@{ub.user.username}, id={ub.user.id})")
            print(f"  status: {ub.status}")
            
            if ub.status == "administrator":
                print(f"  ✅ از قبل ادمینه")
                continue
            
            if ub.status == "member":
                try:
                    await bot.promote_chat_member(
                        chat_id=cid,
                        user_id=ub.user.id,
                        can_delete_messages=True,
                        can_restrict_members=True,
                        can_pin_messages=True,
                        can_invite_users=True,
                        can_change_info=False,
                        can_promote_members=False,
                        can_manage_video_chats=True,
                        can_manage_chat=False,
                        is_anonymous=False,
                    )
                    print(f"  ✅ promote شد")
                except Exception as e:
                    print(f"  ❌ promote خطا: {e}")
        except Exception as e:
            print(f"  ❌ {e}")
        
        await asyncio.sleep(5)
    
    await bot.close()


asyncio.run(promote_all())
PYEOF
