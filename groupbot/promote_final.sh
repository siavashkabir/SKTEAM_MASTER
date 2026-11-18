#!/usr/bin/env bash

echo "═══════════════════════════════════════════════════"
echo "🎯 promote نهایی"
echo "═══════════════════════════════════════════════════"
echo ""

source venv/bin/activate

# صبر برای Flood Control
echo "⏱️  صبر ۴۰۰ ثانیه (Flood Control)..."
sleep 400

python3 << 'PYEOF'
import asyncio
import sys
sys.path.insert(0, '.')

_loop = asyncio.new_event_loop()
asyncio.set_event_loop(_loop)

from pyrogram import Client
from userbot_config import API_ID, API_HASH, STRING_SESSION

CHATS = [-1004463882429, -1004349813270]


async def send_messages():
    # ★ از همون نامی که service استفاده می‌کنه → cache مشترک
    app = Client(name="userbot_service", api_id=API_ID, api_hash=API_HASH, session_string=STRING_SESSION, no_updates=True)
    await app.start()
    me = await app.get_me()
    print(f"✅ userbot: @{me.username} (id={me.id})")
    print()
    
    for cid in CHATS:
        try:
            # ★ resolve peer
            peer = await app.resolve_peer(cid)
            print(f"  ✅ peer resolve: {cid} → {type(peer).__name__}")
            
            # پیام بفرست
            msg = await app.send_message(cid, "🔔")
            print(f"  ✅ پیام: msg_id={msg.id}")
            await asyncio.sleep(2)
        except Exception as e:
            print(f"  ❌ {cid}: {e}")
    
    await app.stop()


_loop.run_until_complete(send_messages())
PYEOF

echo ""
echo "⏱️  صبر ۵ ثانیه، بعد promote..."
sleep 5

python3 << 'PYEOF'
import asyncio
from telegram import Bot
from config import BOT_TOKEN

USERBOT_ID = 8250087472
CHATS = [-1004463882429, -1004349813270]


async def promote_all():
    bot = Bot(token=BOT_TOKEN)
    for cid in CHATS:
        print(f"\n═══ {cid} ═══")
        try:
            ub = await bot.get_chat_member(cid, USERBOT_ID)
            print(f"  ✅ {ub.user.first_name} ({ub.status})")
            
            if ub.status == "administrator":
                print(f"  ✅ از قبل ادمینه")
                continue
            
            if ub.status == "member":
                try:
                    await bot.promote_chat_member(
                        chat_id=cid,
                        user_id=USERBOT_ID,
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
                    print(f"  ❌ promote: {e}")
        except Exception as e:
            print(f"  ❌ {e}")
        
        await asyncio.sleep(5)
    
    await bot.close()
    print()
    print("═══════════════════════════════════════════════════")


asyncio.run(promote_all())
PYEOF
