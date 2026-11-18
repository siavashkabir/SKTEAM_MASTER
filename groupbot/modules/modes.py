from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler
from modules.i18n import t
from database import get_all_locks, toggle_lock

NL = chr(10)

MODES = [
    ("antispam", "🚫", "ضد اسپم"),
    ("antilink", "🔗", "ضد لینک"),
    ("antiflood", "🌊", "ضد فلود"),
    ("badwords", "🤬", "فیلتر فحش"),
    ("autodelete", "🗑️", "حذف خودکار"),
    ("antichannel", "📢", "ضد کانال"),
    ("forcesub", "📌", "اجبار عضویت"),
    ("silent", "🤫", "حالت سکوت"),
    ("welcome", "👋", "خوش‌آمدگویی"),
    ("kicha", "💩", "کیچا"),
]


def build_kb(chat_id, uid=0):
    locks = get_all_locks(chat_id)
    keyboard = []
    row = []
    for key, emoji, name in MODES:
        status = "✅" if locks.get(key, 0) else "❌"
        row.append(InlineKeyboardButton(emoji + " " + name + " " + status, callback_data="mode_" + key + ":" + str(uid) + ":" + str(chat_id)))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    # دکمه اجبارها
    keyboard.append([InlineKeyboardButton("🔥 اجبارها", callback_data="forces_menu:" + str(uid) + ":" + str(chat_id))])
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

    if action == "menu_modes":
        await query.answer()
        cv = int(parts[2]) if len(parts) > 2 else chat_id
        await query.edit_message_text("🔄 حالت‌های گروه" + chr(10) + chr(10) + "برای تنظیم هر مورد، روی دکمه‌اش بزنید:", reply_markup=build_kb(cv, uid))
        return

    if action.startswith("mode_"):
        key = action.replace("mode_", "")
        cv = int(parts[2]) if len(parts) > 2 else chat_id
        toggle_lock(cv, key)
        await query.answer("✅ تغییر کرد")
        await query.edit_message_text("🔄 حالت‌های گروه", reply_markup=build_kb(cv, uid))
        return


def register(app):
    app.add_handler(CallbackQueryHandler(handler, pattern="^(menu_modes|mode_)"), group=5)
