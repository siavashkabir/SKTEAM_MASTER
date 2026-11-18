#!/data/data/com.termux/files/usr/bin/bash

TS=$(date +%Y%m%d_%H%M%S)

echo "═══════════════════════════════════════════════════"
echo "🚀 راه‌اندازی auto-promote userbot"
echo "═══════════════════════════════════════════════════"
echo ""

# ★ ۱. ساخت ماژول جدید: userbot_autopromote.py
echo "─── ۱. ساخت ماژول userbot_autopromote.py ───"

cat > modules/userbot_autopromote.py << 'PYEOF'
"""
Auto-promote userbot به ادمین وقتی به گروه اضافه می‌شه.
userbot id = 8250087472 (Sk team video player / @Skmusic001)
"""
from telegram import ChatPermissions, Update
from telegram.ext import MessageHandler, filters, ContextTypes


USERBOT_ID = 8250087472  # @Skmusic001
USERBOT_USERNAME = "Skmusic001"


async def on_new_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """وقتی کاربر جدیدی اضافه می‌شه"""
    msg = update.effective_message
    chat = update.effective_chat
    
    if not msg or not msg.new_chat_members:
        return
    if chat.type not in ("group", "supergroup"):
        return
    
    # چک: آیا userbot اضافه شده؟
    for member in msg.new_chat_members:
        if member.id == USERBOT_ID or (member.username and member.username.lower() == USERBOT_USERNAME.lower()):
            print(f"[AUTOPROMOTE] userbot در {chat.id} اضافه شد، شروع promote...")
            
            try:
                # promote با دسترسی‌های لازم
                await context.bot.promote_chat_member(
                    chat_id=chat.id,
                    user_id=member.id,
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
                print(f"[AUTOPROMOTE] ✅ userbot در {chat.id} ادمین شد")
                
                await context.bot.send_message(
                    chat_id=chat.id,
                    text=f"✅ دستیار به عنوان ادمین اضافه شد."
                )
            except Exception as e:
                print(f"[AUTOPROMOTE ERR] {e}")
                try:
                    await context.bot.send_message(
                        chat_id=chat.id,
                        text=f"⚠️ نتونستم دستیار رو ادمین کنم.\n"
                             f"لطفاً دستی به عنوان ادمین با دسترسی «حذف پیام‌ها» اضافه‌ش کن."
                    )
                except Exception:
                    pass


def register(app):
    app.add_handler(
        MessageHandler(
            filters.StatusUpdate.NEW_CHAT_MEMBERS,
            on_new_members,
            block=False
        ),
        group=-7  # قبل از خیلی از handlerها
    )
    print("OK module userbot_autopromote loaded")
PYEOF

echo "✅ فایل ساخته شد"
echo ""

# ★ ۲. کامپایل تست
echo "─── ۲. کامپایل ───"
cd ~/groupbot && source venv/bin/activate
if python3 -m py_compile modules/userbot_autopromote.py 2>&1; then
    echo "✅ کامپایل OK"
else
    echo "❌ خطا"
    exit 1
fi
echo ""

# ★ ۳. promote دستی userbot توی گروه‌های فعلی
echo "─── ۳. promote دستی userbot توی گروه‌های فعلی ───"
python3 << 'PYEOF'
import asyncio
from telegram import Bot
from config import BOT_TOKEN

USERBOT_ID = 8250087472
CHATS = [-1004463882429, -1004349813270, -100191141484]

async def promote_all():
    bot = Bot(token=BOT_TOKEN)
    for cid in CHATS:
        try:
            # چک کن userbot عضوه
            member = await bot.get_chat_member(cid, USERBOT_ID)
            if member.status in ("left", "kicked"):
                print(f"  ⚠️ {cid}: userbot توی گروه نیست")
                continue
            
            # promote
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
            print(f"  ✅ {cid}: userbot ادمین شد")
        except Exception as e:
            print(f"  ❌ {cid}: {e}")
    await bot.close()

asyncio.run(promote_all())
PYEOF
echo ""

echo "═══════════════════════════════════════════════════"
echo "✅ آماده"
echo ""
echo "🎯 ری‌استارت:"
echo "pkill -9 -f 'python3 -u main.py'; sleep 3; rm -f .bot.lock; nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 & sleep 15"
echo ""
echo "بعد تست کن:"
echo "  توی گروه «حذف 50» بزن"
echo "  الان باید پیام‌های ربات‌های دیگه هم پاک شن"
echo "═══════════════════════════════════════════════════"
