from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler
from database import toggle_lock, get_all_locks

NL = chr(10)

MEDIA_ITEMS = [
    ("text", "📝", "قفل متن"),
    ("voice", "🎤", "قفل ویس"),
    ("music", "🎵", "قفل موزیک"),
    ("video", "🎬", "قفل فیلم"),
    ("selfie", "🤳", "قفل سلفی"),
    ("sticker", "🩹", "قفل استیکر"),
    ("animated_sticker", "🎞️", "قفل استیکر متحرک"),
    ("gif", "🎥", "قفل گیف"),
    ("photo", "📷", "قفل عکس"),
    ("file", "📁", "قفل فایل"),
    ("location", "📍", "قفل لوکیشن"),
    ("contact", "📞", "قفل مخاطب"),
]

PAGE_SIZE = 8


def build_kb(chat_id, page=1, uid=0):
    locks = get_all_locks(chat_id)
    total = len(MEDIA_ITEMS)
    total_pages = (total + PAGE_SIZE - 1) // PAGE_SIZE
    start = (page - 1) * PAGE_SIZE
    page_items = MEDIA_ITEMS[start:start + PAGE_SIZE]
    keyboard = []
    row = []
    for key, emoji, name in page_items:
        status = "✅" if locks.get(key, 0) else "❌"
        row.append(InlineKeyboardButton(emoji + " " + name + " " + status, callback_data="mlock_" + key + ":" + str(uid) + ":" + str(chat_id) + ":" + str(page)))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    nav = []
    if page > 1:
        nav.append(InlineKeyboardButton("⬅️ قبلی", callback_data="media_page_" + str(page - 1) + ":" + str(uid) + ":" + str(chat_id)))
    if page < total_pages:
        nav.append(InlineKeyboardButton("بعدی ➡️", callback_data="media_page_" + str(page + 1) + ":" + str(uid) + ":" + str(chat_id)))
    if nav:
        keyboard.append(nav)
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="menu_settings:" + str(uid) + ":" + str(chat_id))])
    keyboard.append([InlineKeyboardButton("❌ بستن پنل", callback_data="menu_close:" + str(uid))])
    return InlineKeyboardMarkup(keyboard)


async def handler(update, context):
    query = update.callback_query
    data = query.data
    chat_id = query.message.chat_id
    uid = query.from_user.id

    parts = data.split(":")
    action = parts[0]
    total_pages = (len(MEDIA_ITEMS) + PAGE_SIZE - 1) // PAGE_SIZE

    if action == "menu_media":
        await query.answer()
        await query.edit_message_text("📸 قفل‌های رسانه (1/" + str(total_pages) + ")", reply_markup=build_kb(chat_id, 1, uid))
        return

    if action.startswith("media_page_"):
        pg = int(action.replace("media_page_", ""))
        await query.answer()
        await query.edit_message_text("📸 قفل‌های رسانه (" + str(pg) + "/" + str(total_pages) + ")", reply_markup=build_kb(chat_id, pg, uid))
        return

    if action.startswith("mlock_"):
        key = action.replace("mlock_", "")
        toggle_lock(chat_id, key)
        cur_page = int(parts[3]) if len(parts) > 3 else 1
        await query.answer("✅ تغییر کرد")
        await query.edit_message_text("📸 قفل‌های رسانه (" + str(cur_page) + "/" + str(total_pages) + ")", reply_markup=build_kb(chat_id, cur_page, uid))
        return


def register(app):
    app.add_handler(CallbackQueryHandler(handler, pattern="^(menu_media|media_page_|mlock_)"), group=5)
