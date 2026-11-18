from telegram import Update, ChatPermissions
from telegram.ext import ContextTypes, MessageHandler, filters
from database import is_group_owner, is_bot_admin
from config import OWNER_ID
from datetime import datetime

NL = chr(10)

BAN_TRIGGERS = ["بن", "ban"]
UNBAN_TRIGGERS = ["حذف بن", "رهایی بن", "آزاد", "آنبن", "انبن", "unban"]
MUTE_TRIGGERS = ["سکوت", "خفه", "mute"]
UNMUTE_TRIGGERS = ["رهایی", "حذف سکوت", "آنسکوت", "انسکوت", "unmute"]
KICK_TRIGGERS = ["کیک", "اخراج", "kick"]


async def is_admin_user(chat, user_id):
    try:
        if user_id == OWNER_ID or is_bot_admin(user_id):
            return True
        if is_group_owner(chat.id, user_id):
            return True
        m = await chat.get_member(user_id)
        if m.status in ("administrator", "creator"):
            return True
    except Exception:
        pass
    return False


async def notify_owner(context, chat_id, notif_type, text):
    try:
        from modules.notifications import send_notification
        await send_notification(context, chat_id, notif_type, text)
    except Exception as e:
        print("[MOD NOTIF ERR] " + str(e))


async def get_target(msg, context):
    """گرفتن کاربر هدف از ریپلای یا از آیدی عددی توی متن"""
    # حالت اول: ریپلای
    if msg.reply_to_message and msg.reply_to_message.from_user:
        return msg.reply_to_message.from_user, None
    # حالت دوم: آیدی عددی توی متن
    parts = msg.text.strip().split()
    for p in parts:
        p = p.replace("-", "").strip()
        if p.isdigit() and len(p) > 5:
            try:
                uid = int(p)
                # اگه منفی بود، یعنی آیدی گروه
                if uid < 0:
                    continue
                m = await context.bot.get_chat_member(msg.chat.id, uid)
                return m.user, None
            except Exception as e:
                print("[GET TARGET ERR] " + str(e))
                continue
    # حالت سوم: فوروارد شده
    if msg.forward_from:
        return msg.forward_from, None
    return None, None


async def moderation_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    if not msg or not chat or not user:
        return
    if chat.type not in ("group", "supergroup"):
        return
    if not msg.text:
        return

    text = msg.text.strip()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    # بررسی اینکه کدوم دستور رو داده (با کلمه دقیق یا شروع‌کننده)
    def matches(triggers):
        t = text.lower()
        for tr in triggers:
            if t == tr.lower() or t.startswith(tr.lower() + " "):
                return True
        return False

    # ========== آنبن / حذف بن ==========
    if matches(UNBAN_TRIGGERS):
        if not await is_admin_user(chat, user.id):
            return
        target, _ = await get_target(msg, context)
        if not target:
            await msg.reply_text("❌ روی پیام کاربر ریپلای بزنید یا آیدی عددی رو بنویسید.")
            return
        try:
            await chat.unban_member(target.id, only_if_banned=True)
            await msg.reply_text("✅ " + (target.first_name or "کاربر") + " آزاد شد.")
            # ارسال لینک دعوت در صورت فعال بودن تنظیمات
            try:
                from database import get_setting
                if get_setting(chat.id, "invite_after_unban", "0") == "1":
                    try:
                        link = await context.bot.create_chat_invite_link(chat_id=chat.id, member_limit=1)
                        invite_url = link.invite_link
                        await context.bot.send_message(
                            chat_id=target.id,
                            text="👋 سلام " + (target.first_name or "دوست") + " عزیز!" + NL + NL +
                                 "شما در گروه " + (chat.title or "گروه") + " آزاد شدید." + NL + NL +
                                 "برای بازگشت به گروه، روی لینک زیر بزنید:" + NL +
                                 invite_url + NL + NL +
                                 "⚠️ این لینک فقط برای یک نفر کار می‌کند."
                        )
                        await msg.reply_text("📩 لینک دعوت به پیوی " + (target.first_name or "کاربر") + " ارسال شد.")
                    except Exception as e2:
                        print("[INVITE LINK ERR] " + str(e2))
            except Exception as e:
                print("[INVITE CHECK ERR] " + str(e))
            notif = ("🔔 اعلان مدیریت گروه" + NL + "━━━━━━━━━━━━━━━━" + NL +
                     "👤 کاربر: " + (target.first_name or "کاربر") + NL +
                     "📱 آیدی: " + str(target.id) + NL +
                     "⚡ اقدام: آنبن" + NL +
                     "👮 توسط: " + (user.first_name or "ادمین") + NL +
                     "🕒 زمان: " + now)
            await notify_owner(context, chat.id, "ban", notif)
        except Exception as e:
            print("[UNBAN ERR] " + str(e))
            await msg.reply_text("❌ خطا: " + str(e))
        return

    # ========== بن ==========
    if matches(BAN_TRIGGERS):
        if not await is_admin_user(chat, user.id):
            return
        target, _ = await get_target(msg, context)
        if not target:
            await msg.reply_text("❌ روی پیام کاربر ریپلای بزنید.")
            return
        try:
            await chat.ban_member(target.id)
            await msg.reply_text("🔨 " + (target.first_name or "کاربر") + " بن شد.")
            notif = ("🔔 اعلان مدیریت گروه" + NL + "━━━━━━━━━━━━━━━━" + NL +
                     "👤 کاربر: " + (target.first_name or "کاربر") + " (@" + (target.username or "ندارد") + ")" + NL +
                     "📱 آیدی: " + str(target.id) + NL +
                     "⚡ اقدام: بن" + NL +
                     "👮 توسط: " + (user.first_name or "ادمین") + " (@" + (user.username or "ندارد") + ")" + NL +
                     "🕒 زمان: " + now)
            await notify_owner(context, chat.id, "ban", notif)
        except Exception as e:
            print("[BAN ERR] " + str(e))
            await msg.reply_text("❌ خطا: " + str(e))
        return

    # ========== آزاد کردن کامل (رهایی) ==========
    if matches(UNMUTE_TRIGGERS):
        if not await is_admin_user(chat, user.id):
            return
        target, _ = await get_target(msg, context)
        if not target:
            await msg.reply_text("❌ روی پیام کاربر ریپلای بزنید یا آیدی عددی رو بنویسید.")
            return
        try:
            # اول کاربر رو آنبن کن (اگه بن بوده)
            try:
                await chat.unban_member(target.id, only_if_banned=True)
            except Exception:
                pass
            # بعد همه محدودیت‌ها رو بردار
            await chat.restrict_member(target.id, ChatPermissions(
                can_send_messages=True,
                can_send_audios=True,
                can_send_documents=True,
                can_send_photos=True,
                can_send_videos=True,
                can_send_video_notes=True,
                can_send_voice_notes=True,
                can_send_polls=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
                can_change_info=False,
                can_invite_users=True,
                can_pin_messages=False
            ))
            await msg.reply_text("✅ همه محدودیت‌های " + (target.first_name or "کاربر") + " برداشته شد.")
            notif = ("🔔 اعلان مدیریت گروه" + NL + "━━━━━━━━━━━━━━━━" + NL +
                     "👤 کاربر: " + (target.first_name or "کاربر") + NL +
                     "⚡ اقدام: رهایی (حذف همه محدودیت‌ها)" + NL +
                     "👮 توسط: " + (user.first_name or "ادمین") + NL +
                     "🕒 زمان: " + now)
            await notify_owner(context, chat.id, "mute", notif)
        except Exception as e:
            print("[UNMUTE ERR] " + str(e))
            await msg.reply_text("❌ خطا: " + str(e))
        return

    # ========== سکوت ==========
    if matches(MUTE_TRIGGERS):
        if not await is_admin_user(chat, user.id):
            return
        target, _ = await get_target(msg, context)
        if not target:
            await msg.reply_text("❌ روی پیام کاربر ریپلای بزنید.")
            return
        try:
            await chat.restrict_member(target.id, ChatPermissions(can_send_messages=False))
            await msg.reply_text("🤐 " + (target.first_name or "کاربر") + " ساکت شد!\nدهنتو بستی حالا! کم حرف بزن 🫢")
            notif = ("🔔 اعلان مدیریت گروه" + NL + "━━━━━━━━━━━━━━━━" + NL +
                     "👤 کاربر: " + (target.first_name or "کاربر") + " (@" + (target.username or "ندارد") + ")" + NL +
                     "📱 آیدی: " + str(target.id) + NL +
                     "⚡ اقدام: سکوت" + NL +
                     "👮 توسط: " + (user.first_name or "ادمین") + " (@" + (user.username or "ندارد") + ")" + NL +
                     "🕒 زمان: " + now)
            await notify_owner(context, chat.id, "mute", notif)
        except Exception as e:
            print("[MUTE ERR] " + str(e))
            await msg.reply_text("❌ خطا: " + str(e))
        return

    # ========== اخراج ==========
    if matches(KICK_TRIGGERS):
        if not await is_admin_user(chat, user.id):
            return
        target, _ = await get_target(msg, context)
        if not target:
            await msg.reply_text("❌ روی پیام کاربر ریپلای بزنید.")
            return
        try:
            await chat.ban_member(target.id)
            await chat.unban_member(target.id)
            await msg.reply_text("👢 " + (target.first_name or "کاربر") + " اخراج شد.")
            notif = ("🔔 اعلان مدیریت گروه" + NL + "━━━━━━━━━━━━━━━━" + NL +
                     "👤 کاربر: " + (target.first_name or "کاربر") + " (@" + (target.username or "ندارد") + ")" + NL +
                     "📱 آیدی: " + str(target.id) + NL +
                     "⚡ اقدام: اخراج" + NL +
                     "👮 توسط: " + (user.first_name or "ادمین") + " (@" + (user.username or "ندارد") + ")" + NL +
                     "🕒 زمان: " + now)
            await notify_owner(context, chat.id, "ban", notif)
        except Exception as e:
            print("[KICK ERR] " + str(e))
            await msg.reply_text("❌ خطا: " + str(e))
        return




# ========== لینک گروه ==========
LINK_TRIGGERS = ["لینک", "link"]


async def link_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    if not msg or not chat or not user:
        return
    if chat.type not in ("group", "supergroup"):
        return
    if not msg.text:
        return
    text = msg.text.strip().lower()
    if text not in LINK_TRIGGERS:
        return
    # چک دسترسی: سازنده، مالک گروه، ادمین ربات، ادمین تلگرام، یا ادمین ربات با دسترسی link
    allowed = False
    try:
        from database import get_admin_perm, is_group_owner, is_bot_admin
        from config import OWNER_ID
        if user.id == OWNER_ID or is_bot_admin(user.id):
            allowed = True
        elif is_group_owner(chat.id, user.id):
            allowed = True
        elif get_admin_perm(chat.id, user.id, "link"):
            allowed = True
    except Exception as e:
        print("[LINK PERM ERR] " + str(e))
    if not allowed:
        return
    # باز کردن منوی لینک
    try:
        from modules.link import link_main_menu
        from telegram import InlineKeyboardMarkup
        kb = link_main_menu(user.id, chat.id)
        await msg.reply_text(
            "🔗 مدیریت لینک گروه" + chr(10) + chr(10) +
            "یکی از گزینه‌های زیر را انتخاب کنید:",
            reply_markup=kb
        )
    except Exception as e:
        print("[LINK OPEN ERR] " + str(e))
        await msg.reply_text("❌ خطا: " + str(e))



def register(app):
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, moderation_handler), group=8)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, link_handler), group=9)
