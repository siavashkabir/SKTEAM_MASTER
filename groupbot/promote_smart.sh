#!/usr/bin/env bash

echo "═══════════════════════════════════════════════════"
echo "🎯 promote هوشمند: اول userbot پیام بفرسته"
echo "═══════════════════════════════════════════════════"
echo ""

source venv/bin/activate

python3 << 'PYEOF'
import asyncio
import sys
sys.path.insert(0, '.')

_loop = asyncio.new_event_loop()
asyncio.set_event_loop(_loop)

from pyrogram import Client
from userbot_config import API_ID, API_HASH, STRING_SESSION

CHATS = [-1004463882429, -1004349813270]


async def send_and_promote():
    # ★ قدم ۱: userbot پیام می‌فرسته
    print("─── قدم ۱: userbot پیام می‌فرسته ───")
    app = Client(name="userbot_send", api_id=API_ID, api_hash=API_HASH, session_string=STRING_SESSION, no_updates=True)
    await app.start()
    
    for cid in CHATS:
        try:
            msg = await app.send_message(cid, "🔔 فعال‌سازی")
            print(f"  ✅ پیام به {cid} فرستاده شد (msg_id={msg.id})")
            await asyncio.sleep(2)
        except Exception as e:
            print(f"  ❌ {cid}: {e}")
    
    await app.stop()
    print()
    
    # ★ قدم ۲: ۵ ثانیه صبر
    print("⏱️  صبر ۵ ثانیه...")
    await asyncio.sleep(5)
    
    # ★ قدم ۳: Bot API promote
    print()
    print("─── قدم ۳: Bot API promote ───")
    from telegram import Bot
    from config import BOT_TOKEN
    bot = Bot(token=BOT_TOKEN)
    
    for cid in CHATS:
        print(f"\n═══ {cid} ═══")
        try:
            # با ID امتحان کن
            ub = await bot.get_chat_member(cid, 8250087472)
            print(f"  ✅ پیدا شد: {ub.user.first_name} ({ub.status})")
            
            if ub.status == "administrator":
                print(f"  ✅ از قبل ادمینه")
                continue
            
            if ub.status == "member":
                try:
                    await bot.promote_chat_member(
                        chat_id=cid,
                        user_id=8250087472,
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
                    print(f"  ✅ promote شد!")
                except Exception as e:
                    print(f"  ❌ promote خطا: {e}")
        except Exception as e:
            print(f"  ❌ {e}")
        
        await asyncio.sleep(3)
    
    await bot.close()
    print()
    print("═══════════════════════════════════════════════════")
    print("✅ تمام")
    print("═══════════════════════════════════════════════════")


_loop.run_until_complete(send_and_promote())
PYEOF
