import re
from datetime import datetime
from telegram import Update
from telegram.ext import MessageHandler, filters, ContextTypes
from database import (
    get_all_locks, save_member, increment_message_count,
    add_bot_chat, remove_bot_chat, get_setting, is_vip
)

NL = chr(10)

URL_PATTERN = re.compile(r"(https?://|t\.me/|telegram\.me/|www\.)", re.IGNORECASE)
TAG_PATTERN = re.compile(r"@[a-zA-Z0-9_]+")
HASHTAG_PATTERN = re.compile(r"#\S+")
ENGLISH_PATTERN = re.compile(r"[a-zA-Z]")

MEDIA_LOCK_KEYS = ["photo", "video", "voice", "music", "sticker", "gif", "file", "location", "contact"]


async def check_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await check_flood(update, context)
    except Exception as _fe:
        print("[FLOOD CHECK ERR]", str(_fe))
    msg = update.effective_message
    chat = update.effective_chat
    if not msg or not chat:
        return

    if chat.type not in ("group", "supergroup"):
        return

    try:
        add_bot_chat(chat.id, chat.title or "")
    except Exception:
        pass

    if msg.from_user:
        try:
            increment_message_count(chat.id, msg.from_user.id)
        except Exception:
            pass

    # چک ادمین
    is_admin = False
    try:
        member = await chat.get_member(msg.from_user.id)
        if member.status in ("administrator", "creator"):
            is_admin = True
    except Exception:
        pass

    if is_admin:
        return

    # چک VIP
    vip = False
    if msg.from_user:
        try:
            vip = is_vip(chat.id, msg.from_user.id)
        except Exception:
            vip = False

    locks = get_all_locks(chat.id)
    text = msg.text or msg.caption or ""
    should_delete = False
    # چک فحش
    if locks.get("badwords", 1):
        try:
            text_check = (text or "").lower()
            for bad_word in BAD_WORDS:
                if bad_word in text_check:
                    should_delete = True
                    break
        except Exception:
            pass

    if locks.get("photo", 0) and msg.photo:
        should_delete = True
    if locks.get("video", 0) and msg.video:
        should_delete = True
    if locks.get("voice", 0) and msg.voice:
        should_delete = True
    if locks.get("music", 0) and msg.audio:
        should_delete = True
    if locks.get("sticker", 0) and msg.sticker:
        should_delete = True
    if locks.get("gif", 0) and msg.animation:
        should_delete = True
    if locks.get("file", 0) and msg.document and not msg.animation:
        should_delete = True
    if locks.get("location", 0) and msg.location:
        should_delete = True
    if locks.get("contact", 0) and msg.contact:
        should_delete = True
    if locks.get("selfie", 0) and msg.photo:
        should_delete = True
    if locks.get("text", 0) and msg.text and not msg.text.startswith("/"):
        should_delete = True
    # ═══ قفل‌های اضافی (اصلاح شده) ═══
    if locks.get("link", 0) and text:
        import re as _re_link
        if _re_link.search(r'https?://|t\.me/|www\.', text, _re_link.IGNORECASE):
            should_delete = True
    if locks.get("telegram", 0) and text:
        if "t.me/" in text or "telegram.me/" in text:
            should_delete = True
    if locks.get("hashtag", 0) and text:
        import re as _re_ht
        if _re_ht.search(r'#\w+', text):
            should_delete = True
    if locks.get("web", 0) and text:
        import re as _re_web
        if _re_web.search(r'https?://', text):
            should_delete = True
    if locks.get("emoji", 0) and text:
        import re as _re_em
        if _re_em.search(r'[\U0001F300-\U0001F9FF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF]', text):
            should_delete = True
    if locks.get("spoiler", 0) and msg.text:
        from telegram import MessageEntity
        if msg.entities and any(e.type == MessageEntity.SPOILER for e in msg.entities):
            should_delete = True
    if locks.get("nopersian", 0) and text:
        import re as _re_fa
        if text.strip() and not _re_fa.search(r'[\u0600-\u06FF]', text):
            should_delete = True
    if locks.get("english", 0) and text:
        import re as _re_en
        if text.strip() and _re_en.search(r'[a-zA-Z]', text):
            _fa_chars = len(_re_en.findall(r'[\u0600-\u06FF]', text))
            _en_chars = len(_re_en.findall(r'[a-zA-Z]', text))
            if _en_chars > _fa_chars:
                should_delete = True
    if locks.get("underline", 0) and msg.text:
        from telegram import MessageEntity
        if msg.entities and any(e.type == MessageEntity.UNDERLINE for e in msg.entities):
            should_delete = True
    if locks.get("post", 0) and msg.is_automatic_forward:
        should_delete = True
    if locks.get("reaction", 0):
        # reaction ها پیام نیستن، جدا انجام می‌شه (بعداً)
        pass
    if locks.get("bots", 0) and msg.new_chat_members:
        for _m in msg.new_chat_members:
            if _m.is_bot and _m.id != context.bot.id:
                try:
                    await context.bot.ban_chat_member(chat.id, _m.id)
                    return
                except Exception:
                    pass
async def auto_delete_message(context):
    job = context.job
    try:
        await context.bot.delete_message(chat_id=job.chat_id, message_id=job.data)
    except Exception:
        pass


def is_welcome_enabled(chat_id):
    try:
        val = get_setting(chat_id, "welcome_enabled", "1")
        return val == "1"
    except Exception:
        return True


async def welcome_new(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    chat = update.effective_chat
    if not msg or not msg.new_chat_members or not chat:
        return
    if chat.type not in ("group", "supergroup"):
        return

    for m in msg.new_chat_members:
        if m.id == context.bot.id:
            try:
                add_bot_chat(chat.id, chat.title or "")
            except Exception:
                pass
            continue

        try:
            now = datetime.now().strftime("%Y-%m-%d %H:%M")
            save_member(chat.id, m.id, m.first_name or "", m.username or "", now)
        except Exception:
            pass

        if not is_welcome_enabled(chat.id):
            continue

        name = m.first_name or "کاربر"
        mention = "[" + name + "](tg://user?id=" + str(m.id) + ")"

        custom_text = get_setting(chat.id, "welcome_text", None)
        if custom_text:
            try:
                text = custom_text.replace("{mention}", mention).replace("{group_name}", str(chat.title))
            except Exception:
                text = custom_text
        else:
            text = "🎉 خوش آمدی " + mention + " عزیز!" + NL + NL + "به گروه " + str(chat.title) + " خوش آمدی"

        media_id = get_setting(chat.id, "welcome_media", None)
        media_type = get_setting(chat.id, "welcome_media_type", "none")
        sent = None
        try:
            if media_id and media_type == "photo":
                sent = await msg.reply_photo(photo=media_id, caption=text, parse_mode="Markdown")
            elif media_id and media_type == "animation":
                sent = await msg.reply_animation(animation=media_id, caption=text, parse_mode="Markdown")
            elif media_id and media_type == "video":
                sent = await msg.reply_video(video=media_id, caption=text, parse_mode="Markdown")
            else:
                sent = await msg.reply_text(text, parse_mode="Markdown")
        except Exception:
            try:
                sent = await msg.reply_text(text)
            except Exception:
                pass

        delete_seconds = get_setting(chat.id, "welcome_delete_seconds", "0")
        try:
            seconds = int(delete_seconds)
        except Exception:
            seconds = 0

        if seconds > 0 and sent and context.job_queue:
            try:
                context.job_queue.run_once(auto_delete_message, seconds, chat_id=chat.id, data=sent.message_id, name="wdel_" + str(sent.message_id))
            except Exception:
                pass


async def goodbye(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    chat = update.effective_chat
    if not msg or not msg.left_chat_member or not chat:
        return
    if chat.type not in ("group", "supergroup"):
        return
    m = msg.left_chat_member
    if m.id == context.bot.id:
        try:
            remove_bot_chat(chat.id)
        except Exception:
            pass
        return
    name = m.first_name or "کاربر"
    text = "👋 " + name + " از گروه خارج شد. خدانگهدار"
    try:
        await msg.reply_text(text)
    except Exception:
        pass


def register(app):
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new, block=False), group=0)
    app.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, goodbye, block=False), group=0)
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, check_message, block=False), group=0)


# ==================== ANTI-FLOOD ====================
from datetime import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler

FLOOD_TRACKER = {}   # {chat_id: {user_id: [timestamps]}}
FLOOD_WARNS = {}     # {chat_id: {user_id: count}}


def _is_exempt(user_id, chat_id):
    """چک می‌کنه کاربر مستثناست یا نه"""
    try:
        from config import OWNER_ID, BAD_WORDS
        from database import is_bot_admin, is_group_owner, is_vip, is_deputy
        if user_id == OWNER_ID:
            return True
        if is_bot_admin(user_id):
            return True
        if is_group_owner(chat_id, user_id):
            return True
        try:
            if is_vip(chat_id, user_id):
                return True
        except Exception:
            pass
        try:
            if is_deputy(chat_id, user_id):
                return True
        except Exception:
            pass
    except Exception:
        pass
    return False


async def check_flood(update, context):
    """چک کردن رگبار"""
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    if not msg or not chat or not user:
        return
    if chat.type not in ("group", "supergroup"):
        return

    locks = get_all_locks(chat.id)
    if not locks.get("antiflood", 0):
        return

    if _is_exempt(user.id, chat.id):
        return

    from database import get_setting, set_setting

    try:
        msg_limit = int(get_setting(chat.id, "antiflood_msg_limit", "5"))
        sec_limit = int(get_setting(chat.id, "antiflood_sec_limit", "3"))
        warn_limit = int(get_setting(chat.id, "antiflood_warn_limit", "3"))
        punish = get_setting(chat.id, "antiflood_punish", "mute")
        mute_min = int(get_setting(chat.id, "antiflood_mute_min", "5"))
    except Exception:
        msg_limit, sec_limit, warn_limit, mute_min = 5, 3, 3, 5
        punish = "mute"

    now = datetime.now()
    cid = chat.id
    uid = user.id
    FLOOD_TRACKER.setdefault(cid, {}).setdefault(uid, [])
    times = FLOOD_TRACKER[cid][uid]
    times.append(now)
    # حذف timestamps قدیمی‌تر از بازه
    cutoff = now.timestamp() - sec_limit
    FLOOD_TRACKER[cid][uid] = [t for t in times if t.timestamp() > cutoff]

    if len(FLOOD_TRACKER[cid][uid]) < msg_limit:
        return

    # کاربر رگبار کرده
    FLOOD_TRACKER[cid][uid] = []
    FLOOD_WARNS.setdefault(cid, {}).setdefault(uid, 0)
    FLOOD_WARNS[cid][uid] += 1
    warn_count = FLOOD_WARNS[cid][uid]

    # پاک کردن پیام‌ها
    try:
        await msg.delete()
    except Exception:
        pass

    if warn_count < warn_limit:
        try:
            await context.bot.send_message(
                chat_id=cid,
                text=f"⚠️ {user.first_name} عزیز، لطفاً آرام‌تر! ({warn_count}/{warn_limit})",
                reply_to_message_id=None
            )
        except Exception:
            pass
        return

    # جریمه
    FLOOD_WARNS[cid][uid] = 0
    try:
        if punish == "mute":
            from telegram import ChatPermissions
            until = now.timestamp() + (mute_min * 60)
            await context.bot.restrict_chat_member(
                chat_id=cid,
                user_id=uid,
                permissions=ChatPermissions(can_send_messages=False),
                until_date=int(until)
            )
            await context.bot.send_message(
                chat_id=cid,
                text=f"🔇 {user.first_name} به مدت {mute_min} دقیقه سکوت شد (رگبار)."
            )
        elif punish == "kick":
            await context.bot.ban_chat_member(chat_id=cid, user_id=uid)
            await context.bot.unban_chat_member(chat_id=cid, user_id=uid)
            await context.bot.send_message(
                chat_id=cid,
                text=f"👢 {user.first_name} به خاطر رگبار از گروه اخراج شد."
            )
        elif punish == "ban":
            await context.bot.ban_chat_member(chat_id=cid, user_id=uid)
            await context.bot.send_message(
                chat_id=cid,
                text=f"🚫 {user.first_name} به خاطر رگبار بن شد."
            )
    except Exception as e:
        print("[FLOOD PUNISH ERR]", str(e))


def build_flood_menu(chat_id, uid=0):
    """منوی تنظیمات antiflood"""
    from database import get_setting
    try:
        msg_limit = get_setting(chat_id, "antiflood_msg_limit", "5")
        sec_limit = get_setting(chat_id, "antiflood_sec_limit", "3")
        warn_limit = get_setting(chat_id, "antiflood_warn_limit", "3")
        punish = get_setting(chat_id, "antiflood_punish", "mute")
        mute_min = get_setting(chat_id, "antiflood_mute_min", "5")
    except Exception:
        msg_limit, sec_limit, warn_limit, mute_min = "5", "3", "3", "5"
        punish = "mute"

    punish_label = {"mute": "🔇 سکوت", "kick": "👢 اخراج", "ban": "🚫 بن"}.get(punish, "🔇 سکوت")

    kb = [
        [InlineKeyboardButton(f"📨 تعداد پیام: {msg_limit}", callback_data=f"fl_msg:{uid}:{chat_id}")],
        [InlineKeyboardButton(f"⏱ بازه زمانی: {sec_limit} ثانیه", callback_data=f"fl_sec:{uid}:{chat_id}")],
        [InlineKeyboardButton(f"⚠️ حد اخطار: {warn_limit}", callback_data=f"fl_warn:{uid}:{chat_id}")],
        [InlineKeyboardButton(f"🔨 نوع جریمه: {punish_label}", callback_data=f"fl_pun:{uid}:{chat_id}")],
        [InlineKeyboardButton(f"⏳ مدت سکوت: {mute_min} دقیقه", callback_data=f"fl_mute:{uid}:{chat_id}")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data=f"menu_locks:{uid}")],
    ]
    return InlineKeyboardMarkup(kb)


async def flood_cb_handler(update, context):
    query = update.callback_query
    user = query.from_user
    data = query.data
    parts = data.split(":")
    action = parts[0]
    uid = int(parts[1]) if len(parts) > 1 else user.id
    chat_id = int(parts[2]) if len(parts) > 2 else query.message.chat_id

    if user.id != uid:
        await query.answer("⛔ این منو مال شما نیست!", show_alert=True)
        return

    from database import get_setting, set_setting

    if action == "fl_menu":
        try:
            await query.edit_message_text(
                "🛡 *تنظیمات ضد رگبار*\n\nاز دکمه‌ها برای تنظیم استفاده کن:",
                reply_markup=build_flood_menu(chat_id, uid),
                parse_mode="Markdown"
            )
        except Exception:
            pass
        await query.answer()
        return

    # تغییر مقادیر با چرخه
    options_map = {
        "fl_msg":  (["3", "5", "8", "10", "15"], "antiflood_msg_limit"),
        "fl_sec":  (["2", "3", "5", "10"], "antiflood_sec_limit"),
        "fl_warn": (["1", "2", "3", "5"], "antiflood_warn_limit"),
        "fl_pun":  (["mute", "kick", "ban"], "antiflood_punish"),
        "fl_mute": (["1", "3", "5", "10", "30", "60"], "antiflood_mute_min"),
    }

    if action in options_map:
        options, key = options_map[action]
        current = str(get_setting(chat_id, key, options[0]))
        try:
            idx = options.index(current)
            new_val = options[(idx + 1) % len(options)]
        except ValueError:
            new_val = options[0]
        set_setting(chat_id, key, new_val)
        try:
            await query.edit_message_reply_markup(reply_markup=build_flood_menu(chat_id, uid))
        except Exception:
            pass
        await query.answer(f"✅ تنظیم شد: {new_val}")
        return

    await query.answer()


def register_flood_handlers(app):
    app.add_handler(CallbackQueryHandler(flood_cb_handler, pattern=r"^fl_"), group=-50)
    print("OK antiflood handlers loaded")
