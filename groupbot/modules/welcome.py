import asyncio
import random
import re
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler, MessageHandler, filters
from database import get_setting, set_setting, get_all_locks, toggle_lock

NL = chr(10)

LONG_TEXT = "👋 تنظیمات خوش‌آمدگویی" + NL + NL + "در این بخش می‌تونی متن، رسانه و زمان حذف خودکار پیام خوش‌آمدگویی رو تنظیم کنی." + NL + NL + "📌 روش دوم: یه عکس/گیف/ویدیو توی گروه بفرست، روش ریپلای کن و بنویس «تنظیم رسانه خوش‌آمدگویی»"

RANDOM_WELCOMES = [
    "🌟 خوش آمدی {name} عزیز!",
    "🎉 سلام {name}! خوشحالیم که پیوستی.",
    "💫 {name} جان، قدمت روی چشم!",
    "🌸 به به، {name} عزیز!",
    "🔥 {name}، به خانواده ما خوش آمدی!",
    "🎊 سلام {name}! چه خبر؟",
    "💝 {name} جان، خوش آمدی!",
    "🌺 {name} عزیز، ورودت رو تبریک!",
    "✨ خوش آمدی {name}!",
    "🎈 سلام {name} جان!",
    "🌹 {name} عزیز، امیدوارم اینجا راحت باشی.",
    "🎁 سلام {name}! خوش آمدی.",
    "💎 {name} جان، خوش آمدی!",
    "🌈 سلام {name}! چه خوب که اومدی.",
    "☀️ {name} عزیز، خوش آمدی!",
]

PENDING_WELCOME_EDIT = {}
PENDING_WELCOME_MEDIA = {}

TRIGGERS = [
    "تنظیم رسانه خوش آمد گویی",
    "تنظیم رسانه خوشامدگویی",
    "تنظیم خوشامدگویی",
    "تنظیم خوش آمد گویی",
]


def normalize_text(s):
    """حذف فاصله‌ها و کاراکترهای مخفی برای مقایسه"""
    return re.sub(r"[\s\u200c\u200f\u200e\u202a-\u202e]+", "", s.strip())


NORMALIZED_TRIGGERS = [normalize_text(t) for t in TRIGGERS]


def welcome_menu(uid, chat_id):
    locks = get_all_locks(chat_id)
    status = "✅" if locks.get("welcome", 0) else "❌"
    rand_status = "✅" if get_setting(chat_id, "welcome_random", "1") == "1" else "❌"
    keyboard = [
        [InlineKeyboardButton("👋 خوش‌آمدگویی " + status, callback_data="welcome_toggle:" + str(uid) + ":" + str(chat_id))],
        [InlineKeyboardButton("🎲 خوش‌آمدگویی تصادفی " + rand_status, callback_data="welcome_random_toggle:" + str(uid) + ":" + str(chat_id))],
        [InlineKeyboardButton("👁️ مشاهده خوش‌آمدگویی", callback_data="welcome_shortcut:" + str(uid) + ":" + str(chat_id))],
        [InlineKeyboardButton("✏️ ویرایش متن", callback_data="welcome_edittext:" + str(uid) + ":" + str(chat_id))],
        [InlineKeyboardButton("📷 بدون رسانه", callback_data="welcome_media_name:" + str(uid) + ":" + str(chat_id)),
         InlineKeyboardButton("🖼️ عکس", callback_data="welcome_media_photo:" + str(uid) + ":" + str(chat_id))],
        [InlineKeyboardButton("🎥 ویدیو", callback_data="welcome_media_video:" + str(uid) + ":" + str(chat_id)),
         InlineKeyboardButton("🎞️ گیف", callback_data="welcome_media_gif:" + str(uid) + ":" + str(chat_id))],
        [InlineKeyboardButton("🗑️ حذف رسانه فعلی", callback_data="welcome_mediaclear:" + str(uid) + ":" + str(chat_id))],
        [InlineKeyboardButton("⏰ حذف خودکار:", callback_data="welcome_noop")],
        [InlineKeyboardButton("10s", callback_data="welcome_del_10:" + str(uid) + ":" + str(chat_id)),
         InlineKeyboardButton("30s", callback_data="welcome_del_30:" + str(uid) + ":" + str(chat_id)),
         InlineKeyboardButton("1m", callback_data="welcome_del_60:" + str(uid) + ":" + str(chat_id))],
        [InlineKeyboardButton("5m", callback_data="welcome_del_300:" + str(uid) + ":" + str(chat_id)),
         InlineKeyboardButton("10m", callback_data="welcome_del_600:" + str(uid) + ":" + str(chat_id)),
         InlineKeyboardButton("30m", callback_data="welcome_del_1800:" + str(uid) + ":" + str(chat_id))],
        [InlineKeyboardButton("🚫 بدون حذف", callback_data="welcome_cancel:" + str(uid) + ":" + str(chat_id))],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="menu_settings:" + str(uid) + ":" + str(chat_id))],
    ]
    return InlineKeyboardMarkup(keyboard)


async def handler(update, context):
    query = update.callback_query
    data = query.data
    chat_id = query.message.chat_id
    uid = query.from_user.id
    parts = data.split(":")
    action = parts[0]

    if action == "welcome_menu":
        await query.answer()
        await query.edit_message_text(LONG_TEXT, reply_markup=welcome_menu(uid, chat_id))
        return

    if action == "welcome_toggle":
        toggle_lock(chat_id, "welcome")
        await query.answer("✅ تغییر کرد")
        await query.edit_message_text(LONG_TEXT, reply_markup=welcome_menu(uid, chat_id))
        return

    if action == "welcome_random_toggle":
        cur = get_setting(chat_id, "welcome_random", "1")
        set_setting(chat_id, "welcome_random", "0" if cur == "1" else "1")
        await query.answer("✅ تغییر کرد")
        await query.edit_message_text(LONG_TEXT, reply_markup=welcome_menu(uid, chat_id))
        return

    if action == "welcome_shortcut":
        await query.answer()
        rand_on = get_setting(chat_id, "welcome_random", "1") == "1"
        cur = get_setting(chat_id, "welcome_text", "")
        if rand_on:
            preview_text = random.choice(RANDOM_WELCOMES).replace("{name}", "کاربر نمونه")
        elif cur:
            preview_text = cur.replace("{name}", "کاربر نمونه")
        else:
            preview_text = "خوش آمدی کاربر نمونه!"
        media_type = get_setting(chat_id, "welcome_media_type", "none")
        media_id = get_setting(chat_id, "welcome_media_id", "")
        try:
            if media_type == "photo" and media_id:
                await context.bot.send_photo(chat_id=chat_id, photo=media_id, caption=preview_text, parse_mode="Markdown")
            elif media_type == "gif" and media_id:
                await context.bot.send_animation(chat_id=chat_id, animation=media_id, caption=preview_text, parse_mode="Markdown")
            elif media_type == "video" and media_id:
                await context.bot.send_video(chat_id=chat_id, video=media_id, caption=preview_text, parse_mode="Markdown")
            else:
                await context.bot.send_message(chat_id=chat_id, text="👋 پیش‌نمایش خوش‌آمدگویی:" + NL + NL + preview_text)
        except Exception as e:
            print("[WELCOME PREVIEW ERR] " + str(e))
            try:
                await context.bot.send_message(chat_id=chat_id, text="👋 پیش‌نمایش:" + NL + NL + preview_text)
            except Exception:
                pass
        try:
            await query.edit_message_text(LONG_TEXT, reply_markup=welcome_menu(uid, chat_id))
        except Exception:
            pass
        return

    if action == "welcome_edittext":
        PENDING_WELCOME_EDIT[chat_id] = uid
        await query.answer()
        await query.edit_message_text(
            "✏️ ویرایش متن خوش‌آمدگویی" + NL + NL +
            "لطفاً متن جدید را همین حالا در گروه بفرستید." + NL +
            "برای انصراف، روی دکمه بازگشت بزنید.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 انصراف", callback_data="welcome_canceledit:" + str(uid) + ":" + str(chat_id))],
            ])
        )
        return

    if action == "welcome_canceledit":
        PENDING_WELCOME_EDIT.pop(chat_id, None)
        await query.answer("لغو شد")
        await query.edit_message_text(LONG_TEXT, reply_markup=welcome_menu(uid, chat_id))
        return

    if action.startswith("welcome_media_"):
        mtype = action.replace("welcome_media_", "")
        if mtype == "name":
            set_setting(chat_id, "welcome_media_type", "none")
            set_setting(chat_id, "welcome_media_id", "")
            await query.answer("✅ بدون رسانه")
            await query.edit_message_text(LONG_TEXT, reply_markup=welcome_menu(uid, chat_id))
            return
        PENDING_WELCOME_MEDIA[chat_id] = {"user_id": uid, "type": mtype}
        labels = {"photo": "عکس", "video": "ویدیو", "gif": "گیف"}
        label = labels.get(mtype, mtype)
        await query.answer()
        await query.edit_message_text(
            "📤 ارسال " + label + " خوش‌آمدگویی" + NL + NL +
            "لطفاً " + label + " مورد نظر را همین حالا در گروه بفرستید." + NL + NL +
            "📌 روش دوم: روی یه " + label + " ریپلای بزنید و بنویسید «تنظیم رسانه خوش‌آمدگویی»",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 انصراف", callback_data="welcome_cancelmedia:" + str(uid) + ":" + str(chat_id))],
            ])
        )
        return

    if action == "welcome_cancelmedia":
        PENDING_WELCOME_MEDIA.pop(chat_id, None)
        await query.answer("لغو شد")
        await query.edit_message_text(LONG_TEXT, reply_markup=welcome_menu(uid, chat_id))
        return

    if action == "welcome_mediaclear":
        set_setting(chat_id, "welcome_media_type", "none")
        set_setting(chat_id, "welcome_media_id", "")
        await query.answer("✅ رسانه حذف شد")
        await query.edit_message_text(LONG_TEXT, reply_markup=welcome_menu(uid, chat_id))
        return

    if action.startswith("welcome_del_"):
        seconds = int(action.replace("welcome_del_", ""))
        set_setting(chat_id, "welcome_autodelete", str(seconds))
        await query.answer("✅ زمان حذف: " + str(seconds) + " ثانیه")
        await query.edit_message_text(LONG_TEXT, reply_markup=welcome_menu(uid, chat_id))
        return

    if action == "welcome_cancel":
        set_setting(chat_id, "welcome_autodelete", "0")
        await query.answer("✅ حذف خودکار غیرفعال شد")
        await query.edit_message_text(LONG_TEXT, reply_markup=welcome_menu(uid, chat_id))
        return

    if action == "welcome_noop":
        await query.answer()
        return

    await query.answer()


async def catch_welcome_text(update, context):
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    if not msg or not chat or not user:
        return
    if chat.id not in PENDING_WELCOME_EDIT:
        return
    if PENDING_WELCOME_EDIT.get(chat.id) != user.id:
        return
    if not msg.text:
        return
    set_setting(chat.id, "welcome_text", msg.text)
    PENDING_WELCOME_EDIT.pop(chat.id, None)
    confirm = await msg.reply_text("✅ متن خوش‌آمدگویی جدید ذخیره شد.")
    try:
        await msg.reply_text(LONG_TEXT, reply_markup=welcome_menu(user.id, chat.id))
    except Exception as e:
        print("[WELCOME MENU RESEND ERR] " + str(e))
    await asyncio.sleep(10)
    try:
        await confirm.delete()
    except Exception:
        pass


async def catch_welcome_media(update, context):
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    if not msg or not chat or not user:
        return
    if chat.id not in PENDING_WELCOME_MEDIA:
        return
    pending = PENDING_WELCOME_MEDIA.get(chat.id)
    if not pending or pending.get("user_id") != user.id:
        return
    mtype = pending.get("type")
    file_id = None
    if mtype == "photo" and msg.photo:
        file_id = msg.photo[-1].file_id
    elif mtype == "video" and msg.video:
        file_id = msg.video.file_id
    elif mtype == "gif" and msg.animation:
        file_id = msg.animation.file_id
    elif mtype == "gif" and msg.document and msg.document.mime_type == "image/gif":
        file_id = msg.document.file_id
    if not file_id:
        return
    set_setting(chat.id, "welcome_media_type", mtype)
    set_setting(chat.id, "welcome_media_id", file_id)
    PENDING_WELCOME_MEDIA.pop(chat.id, None)
    confirm = await msg.reply_text("✅ رسانه خوش‌آمدگویی ذخیره شد.")
    try:
        await msg.reply_text(LONG_TEXT, reply_markup=welcome_menu(user.id, chat.id))
    except Exception as e:
        print("[WELCOME MEDIA MENU ERR] " + str(e))
    await asyncio.sleep(10)
    try:
        await confirm.delete()
    except Exception:
        pass


async def set_media_by_reply(update, context):
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    if not msg or not chat or not user:
        return
    if chat.type not in ("group", "supergroup"):
        return
    if not msg.text:
        return
    cleaned = normalize_text(msg.text)
    if cleaned not in NORMALIZED_TRIGGERS:
        return
    try:
        from database import is_group_owner, is_bot_admin
        from config import OWNER_ID
        if not (is_group_owner(chat.id, user.id) or is_bot_admin(user.id) or user.id == OWNER_ID):
            return
    except Exception:
        return
    if not msg.reply_to_message:
        await msg.reply_text("❌ لطفاً روی یه عکس، گیف یا ویدیو ریپلای بزنید.")
        return
    target = msg.reply_to_message
    mtype = None
    file_id = None
    if target.photo:
        mtype = "photo"
        file_id = target.photo[-1].file_id
    elif target.animation:
        mtype = "gif"
        file_id = target.animation.file_id
    elif target.video:
        mtype = "video"
        file_id = target.video.file_id
    elif target.document and target.document.mime_type == "image/gif":
        mtype = "gif"
        file_id = target.document.file_id
    if not file_id:
        await msg.reply_text("❌ فقط عکس، گیف و ویدیو پشتیبانی می‌شود.")
        return
    set_setting(chat.id, "welcome_media_type", mtype)
    set_setting(chat.id, "welcome_media_id", file_id)
    labels = {"photo": "عکس", "gif": "گیف", "video": "ویدیو"}
    confirm = await msg.reply_text("✅ " + labels.get(mtype, mtype) + " خوش‌آمدگویی تنظیم شد.")
    await asyncio.sleep(10)
    try:
        await confirm.delete()
    except Exception:
        pass


def get_welcome_text(chat_id, name="دوست"):
    rand_on = get_setting(chat_id, "welcome_random", "1") == "1"
    if rand_on:
        msg = random.choice(RANDOM_WELCOMES)
        return msg.replace("{name}", name)
    return get_setting(chat_id, "welcome_text", "خوش آمدی {name}!").replace("{name}", name)


def register(app):
    app.add_handler(CallbackQueryHandler(handler, pattern="^(welcome_)"), group=5)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, set_media_by_reply), group=-6)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, catch_welcome_text), group=-5)
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO | filters.ANIMATION | filters.Document.ALL, catch_welcome_media), group=-5)
