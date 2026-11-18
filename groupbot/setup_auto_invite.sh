#!/data/data/com.termux/files/usr/bin/bash

TS=$(date +%Y%m%d_%H%M%S)

echo "═══════════════════════════════════════════════════"
echo "🚀 راه‌اندازی auto-invite + auto-promote userbot"
echo "═══════════════════════════════════════════════════"
echo ""

# ═══════════════════════════════════════════════════
# ۱. ماژول جدید
# ═══════════════════════════════════════════════════
echo "─── ۱. ساخت ماژول userbot_autojoin.py ───"

cat > modules/userbot_autojoin.py << 'PYEOF'
"""
Auto-invite و auto-promote userbot (@Skmusic001)
وقتی ربات Manager به گروه جدید می‌ره، userbot رو میاره + ادمینش می‌کنه.
"""
import asyncio
from telegram import ChatPermissions, Update
from telegram.ext import MessageHandler, filters, ContextTypes


USERBOT_ID = 8250087472
USERBOT_USERNAME = "Skmusic001"


async def on_bot_added(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """وقتی ربات به گروه جدید اضافه می‌شه"""
    msg = update.effective_message
    chat = update.effective_chat
    
    if not msg or not msg.new_chat_members:
        return
    if chat.type not in ("group", "supergroup"):
        return
    
    bot_id = context.bot.id
    
    # چک کن خود ربات اضافه شده
    bot_added = any(m.id == bot_id for m in msg.new_chat_members)
    if not bot_added:
        return
    
    print(f"[AUTOJOIN] ربات به گروه {chat.id} اضافه شد")
    
    # ۲ ثانیه صبر کن
    await asyncio.sleep(2)
    
    # ★ قدم ۱: userbot رو به گروه دعوت کن
    userbot_joined = False
    try:
        # چک کن userbot از قبل عضوه
        try:
            ub = await context.bot.get_chat_member(chat.id, USERBOT_ID)
            if ub.status not in ("left", "kicked"):
                userbot_joined = True
                print(f"[AUTOJOIN] userbot از قبل عضوه")
        except Exception:
            pass
        
        # اگه نیست، invite کن
        if not userbot_joined:
            try:
                await context.bot.unban_chat_member(
                    chat_id=chat.id,
                    user_id=USERBOT_ID,
                    only_if_banned=True
                )
            except Exception:
                pass
            
            # تلاش برای invite
            try:
                # تلگرام اجازه invite فقط با لینک رو می‌ده
                # پس باید از creator بخوایم
                print(f"[AUTOJOIN] userbot توی گروه نیست — از creator می‌خوایم")
                await context.bot.send_message(
                    chat_id=chat.id,
                    text=(
                        "🤖 برای فعال‌سازی کامل قابلیت‌های گروه:\n\n"
                        "لطفاً این اکانت رو به عنوان ادمین اضافه کنید:\n"
                        f"👤 @{USERBOT_USERNAME}\n\n"
                        "با دسترسی‌های:\n"
                        "✅ Delete messages\n"
                        "✅ Restrict members\n"
                        "✅ Pin messages\n"
                        "✅ Invite users\n"
                        "✅ Manage video chats"
                    )
                )
            except Exception as e:
                print(f"[AUTOJOIN] invite ERR: {e}")
    except Exception as e:
        print(f"[AUTOJOIN] ERR: {e}")
    
    # ★ قدم ۲: اگه userbot عضوه، ادمینش کن
    if userbot_joined:
        try:
            ub = await context.bot.get_chat_member(chat.id, USERBOT_ID)
            if ub.status == "administrator":
                print(f"[AUTOJOIN] userbot از قبل ادمینه")
            elif ub.status == "member":
                await context.bot.promote_chat_member(
                    chat_id=chat.id,
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
                print(f"[AUTOJOIN] ✅ userbot ادمین شد")
                try:
                    await context.bot.send_message(
                        chat_id=chat.id,
                        text="✅ دستیار گروه فعال شد."
                    )
                except Exception:
                    pass
        except Exception as e:
            print(f"[AUTOJOIN PROMOTE ERR] {e}")


def register(app):
    app.add_handler(
        MessageHandler(
            filters.StatusUpdate.NEW_CHAT_MEMBERS,
            on_bot_added,
            block=False
        ),
        group=-8
    )
    print("OK module userbot_autojoin loaded")
PYEOF

echo "✅ فایل ساخته شد"
echo ""

# ═══════════════════════════════════════════════════
# ۲. کامپایل
# ═══════════════════════════════════════════════════
echo "─── ۲. کامپایل ───"
cd ~/groupbot && source venv/bin/activate
if python3 -m py_compile modules/userbot_autojoin.py 2>&1; then
    echo "✅ کامپایل OK"
else
    echo "❌ خطا"
    exit 1
fi
echo ""

# ═══════════════════════════════════════════════════
# ۳. چک: userbot توی کدوم گروه‌هاست
# ═══════════════════════════════════════════════════
echo "─── ۳. چک: userbot کجاست؟ ───"
python3 << 'PYEOF'
import asyncio
import sys
sys.path.insert(0, '.')

_loop = asyncio.new_event_loop()
asyncio.set_event_loop(_loop)

from pyrogram import Client
from userbot_config import API_ID, API_HASH, STRING_SESSION

async def main():
    app = Client(name="userbot_check2", api_id=API_ID, api_hash=API_HASH, session_string=STRING_SESSION)
    await app.start()
    me = await app.get_me()
    print(f"✅ userbot: {me.first_name} (@{me.username}, id={me.id})")
    print()
    print("═══ گروه‌هایی که userbot عضوه ═══")
    count = 0
    async for dialog in app.get_dialogs():
        if dialog.chat.type in ("group", "supergroup"):
            count += 1
            print(f"  • {dialog.chat.title}")
            print(f"    id: {dialog.chat.id}")
    if count == 0:
        print("  ❌ توی هیچ گروهی نیست!")
    await app.stop()

_loop.run_until_complete(main())
PYEOF
echo ""

echo "═══════════════════════════════════════════════════"
echo "✅ آماده"
echo ""
echo "🎯 مرحله بعدی:"
echo ""
echo "1. userbot (@Skmusic001) رو دستی به گروه‌ها اضافه کن"
echo "   از اکانت خودت (Siavash) → Add Members"
echo ""
echo "2. userbot رو ادمین کن با دسترسی‌های لازم"
echo "   Group → Administrators → Add @Skmusic001"
echo ""
echo "3. بعد از این، هر گروهی که ربات Manager بره،"
echo "   به creator می‌گه userbot رو اضافه کنه"
echo "═══════════════════════════════════════════════════"
