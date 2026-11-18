from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler
from database import get_setting, set_setting

NL = chr(10)

SECTIONS = [
    ("text", "📝", "قفل متن"),
    ("gif", "🎞️", "گیف‌ها"),
    ("sticker", "🩹", "استیکرها"),
    ("photo", "🖼️", "عکس‌ها"),
    ("video", "🎥", "ویدیوها"),
    ("voice", "🎤", "ویس‌ها"),
    ("file", "📁", "فایل‌ها"),
]

LONG_TEXT = "🗑️ پاکسازی خودکار" + NL + NL + "در این بخش می‌تونی پاکسازی خودکار پیام‌ها رو تنظیم کنی."


async def do_purge(chat_id, msg_id, count=100, bot=None):
    """پاک کردن count پیام آخر گروه"""
    if not bot:
        print("[PURGE] bot argument لازمه")
        return 0
    
    ids = list(range(msg_id, max(0, msg_id - count), -1))
    deleted = 0
    
    # دسته‌بندی ۱۰۰ تایی
    for i in range(0, len(ids), 100):
        chunk = ids[i:i+100]
        try:
            await bot.delete_messages(chat_id, chunk)
            deleted += len(chunk)
        except Exception as e:
            # اگه نشد، تک‌تک امتحان کن
            print(f"[PURGE] chunk err: {e}")
            for mid in chunk:
                try:
                    await bot.delete_message(chat_id, mid)
                    deleted += 1
                except Exception:
                    pass
    
    print(f"[PURGE] {deleted}/{len(ids)} پیام پاک شد")
    return deleted


def purge_menu(uid, chat_id):
    enabled = get_setting(chat_id, "purge_enabled", "0")
    pt = get_setting(chat_id, "purge_time", "03:00")
    status = "✅" if enabled == "1" else "❌"
    keyboard = [
        [InlineKeyboardButton("🗑️ پاکسازی خودکار " + status, callback_data="purge_toggle:" + str(uid) + ":" + str(chat_id))],
        [InlineKeyboardButton("⏰ ساعت: " + pt, callback_data="purge_noop")],
        [InlineKeyboardButton("📋 بخش‌های فعال:", callback_data="purge_noop")],
    ]
    row = []
    for key, emoji, name in SECTIONS:
        sec_status = "✅" if get_setting(chat_id, "purge_sec_" + key, "1") == "1" else "❌"
        row.append(InlineKeyboardButton(emoji + " " + name + " " + sec_status, callback_data="purge_sec_" + key + ":" + str(uid) + ":" + str(chat_id)))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="menu_settings:" + str(uid) + ":" + str(chat_id))])
    keyboard.append([InlineKeyboardButton("❌ بستن پنل", callback_data="menu_close:" + str(uid))])
    return InlineKeyboardMarkup(keyboard)


async def handler(update, context):
    query = update.callback_query
    data = query.data
    chat_id = query.message.chat_id
    uid = query.from_user.id
    action = data.split(":")[0]

    if action == "purge_menu":
        await query.answer()
        await query.edit_message_text(LONG_TEXT, reply_markup=purge_menu(uid, chat_id))
        return

    if action == "purge_toggle":
        cur = get_setting(chat_id, "purge_enabled", "0")
        set_setting(chat_id, "purge_enabled", "0" if cur == "1" else "1")
        await query.answer("✅ تغییر کرد")
        await query.edit_message_text(LONG_TEXT, reply_markup=purge_menu(uid, chat_id))
        return

    if action.startswith("purge_sec_"):
        key = action.replace("purge_sec_", "")
        cur = get_setting(chat_id, "purge_sec_" + key, "1")
        set_setting(chat_id, "purge_sec_" + key, "0" if cur == "1" else "1")
        await query.answer("✅ تغییر کرد")
        await query.edit_message_text(LONG_TEXT, reply_markup=purge_menu(uid, chat_id))
        return

    if action == "purge_noop":
        await query.answer()
        return

    await query.answer()


def register(app):
    app.add_handler(CallbackQueryHandler(handler, pattern="^(purge_)"), group=5)
