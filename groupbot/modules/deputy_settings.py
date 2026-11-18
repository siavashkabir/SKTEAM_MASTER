from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler, ContextTypes
from database import (
    DEPUTY_PERMS, get_all_deputy_perms, toggle_deputy_perm,
    init_deputy_perms, is_group_owner, is_bot_admin
)
from config import OWNER_ID

NL = chr(10)


def build_menu(uid, chat_id):
    perms = get_all_deputy_perms(chat_id)
    keyboard = []
    keyboard.append([InlineKeyboardButton("فعال / غیرفعال کردن دسترسی ها", callback_data="depset_noop:" + str(uid) + ":" + str(chat_id))])
    for key, label in DEPUTY_PERMS:
        enabled = perms.get(key, True)
        mark = "[X]" if enabled else "[ ]"
        keyboard.append([InlineKeyboardButton(mark + " " + label, callback_data="depset_toggle_" + key + ":" + str(uid) + ":" + str(chat_id))])
    keyboard.append([
        InlineKeyboardButton("فعال کردن همه", callback_data="depset_all_on:" + str(uid) + ":" + str(chat_id)),
        InlineKeyboardButton("غیرفعال کردن همه", callback_data="depset_all_off:" + str(uid) + ":" + str(chat_id)),
    ])
    keyboard.append([InlineKeyboardButton("بازگشت", callback_data="menu_settings:" + str(uid))])
    keyboard.append([InlineKeyboardButton("بستن پنل", callback_data="menu_close:" + str(uid))])
    return InlineKeyboardMarkup(keyboard)


async def cb_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    clicker = query.from_user.id

    parts = data.split(":")
    action = parts[0]
    owner = int(parts[1]) if len(parts) > 1 else clicker
    chat_id = int(parts[2]) if len(parts) > 2 else query.message.chat_id

    if clicker != owner:
        await query.answer("این منو برای شما نیست", show_alert=True)
        return

    await query.answer()

    if action == "depset_noop":
        return

    if action == "depset_menu":
        init_deputy_perms(chat_id)
        try:
            await query.edit_message_text(
                "تنظیمات دسترسی معاون:" + NL + NL +
                "روی هر مورد بزن تا روشن/خاموش بشه." + NL +
                "معاون فقط به بخش هایی که [X] هستن دسترسی داره.",
                reply_markup=build_menu(owner, chat_id)
            )
        except Exception:
            pass
        return

    if action == "depset_all_on":
        for key, label in DEPUTY_PERMS:
            if not get_all_deputy_perms(chat_id).get(key, True):
                toggle_deputy_perm(chat_id, key)
        try:
            await query.edit_message_reply_markup(reply_markup=build_menu(owner, chat_id))
        except Exception:
            pass
        return

    if action == "depset_all_off":
        for key, label in DEPUTY_PERMS:
            if get_all_deputy_perms(chat_id).get(key, True):
                toggle_deputy_perm(chat_id, key)
        try:
            await query.edit_message_reply_markup(reply_markup=build_menu(owner, chat_id))
        except Exception:
            pass
        return

    if action.startswith("depset_toggle_"):
        key = action.replace("depset_toggle_", "")
        toggle_deputy_perm(chat_id, key)
        try:
            await query.edit_message_reply_markup(reply_markup=build_menu(owner, chat_id))
        except Exception:
            pass
        return


def register(app):
    app.add_handler(CallbackQueryHandler(cb_handler, pattern="^depset_"), group=72)
