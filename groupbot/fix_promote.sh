#!/data/data/com.termux/files/usr/bin/bash

echo "═══════════════════════════════════════════════════"
echo "🔍 چک وضعیت userbot توی گروه‌ها"
echo "═══════════════════════════════════════════════════"
echo ""

cd ~/groupbot && source venv/bin/activate

python3 << 'PYEOF'
import asyncio
from telegram import Bot
from config import BOT_TOKEN

USERBOT_USERNAME = "Skmusic001"  # از @
CHATS = [-1004463882429, -1004349813270]  # فقط گروه‌های معتبر

async def check_and_promote():
    bot = Bot(token=BOT_TOKEN)
    
    for cid in CHATS:
        print(f"\n═══ گروه {cid} ═══")
        try:
            # ۱. چک گروه وجود داره
            chat = await bot.get_chat(cid)
            print(f"  ✅ گروه: {chat.title}")
        except Exception as e:
            print(f"  ❌ گروه پیدا نشد: {e}")
            continue
        
        # ۲. چک userbot با username
        try:
            ub = await bot.get_chat_member(cid, "@" + USERBOT_USERNAME)
            print(f"  ✅ userbot پیدا شد: {ub.user.first_name} (@{ub.user.username})")
            print(f"     user id: {ub.user.id}")
            print(f"     status: {ub.status}")
            
            if ub.status in ("left", "kicked"):
                print(f"  ⚠️ userbot توی گروه نیست — باید اول اضافه‌ش کنی")
                continue
            
            if ub.status == "administrator":
                print(f"  ✅ userbot الان ادمینه!")
                continue
            
            # ۳. promote با ID واقعی
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
                print(f"  ✅ userbot promote شد!")
            except Exception as e:
                print(f"  ❌ promote خطا: {e}")
        except Exception as e:
            print(f"  ❌ userbot پیدا نشد: {e}")
            print(f"     → userbot رو دستی به گروه اضافه کن")
    
    await bot.close()

asyncio.run(check_and_promote())
PYEOF

echo ""
echo "═══════════════════════════════════════════════════"
