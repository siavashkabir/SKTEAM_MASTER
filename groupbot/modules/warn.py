from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler
from database import get_setting, set_setting

NL = chr(10)


def warn_menu(uid, chat_id):
    limit = get_setting(chat_id, "warn_limit", "3")
    action_name = get_setting(chat_id, "warn_action", "mute")
    labels = {"mute": "سکوت", "kick": "اخراج", "ban": "بن"}
    keyboard = [
        [InlineKeyboardButton("⚠️ تعداد اخطار تا اقدام: " + str(limit), callback_data="warn_noop")],
        [InlineKeyboardButton("3", callback_data="warnset_limit_3:" + str(uid) + ":" + str(chat_id)),
         InlineKeyboardButton("4", callback_data="warnset_limit_4:" + str(uid) + ":" + str(chat_id)),
         InlineKeyboardButton("5", callback_data="warnset_limit_5:" + str(uid) + ":" + str(chat_id)),
         InlineKeyboardButton("10", callback_data="warnset_limit_10:" + str(uid) + ":" + str(chat_id))],
        [InlineKeyboardButton("⚡ اقدام در صورت رسیدن به حد:", callback_data="warn_noop")],
        [InlineKeyboardButton("🤐 سکوت" + (" ✅" if action_name == "mute" else ""), callback_data="warnset_action_mute:" + str(uid) + ":" + str(chat_id))],
        [InlineKeyboardButton("👢 اخراج" + (" ✅" if action_name == "kick" else ""), callback_data="warnset_action_kick:" + str(uid) + ":" + str(chat_id))],
        [InlineKeyboardButton("🚫 بن" + (" ✅" if action_name == "ban" else ""), callback_data="warnset_action_ban:" + str(uid) + ":" + str(chat_id))],
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

    if action == "warnset_menu":
        await query.answer()
        await query.edit_message_text("⚠️ سیستم اخطار" + NL + NL + "می‌توانی تعیین کنی بعد از چند اخطار، چه اقدامی برای کاربر انجام شود.", reply_markup=warn_menu(uid, chat_id))
        return

    if action.startswith("warnset_limit_"):
        limit = action.replace("warnset_limit_", "")
        set_setting(chat_id, "warn_limit", limit)
        await query.answer("✅ حد اخطار: " + limit)
        await query.edit_message_text("⚠️ سیستم اخطار", reply_markup=warn_menu(uid, chat_id))
        return

    if action.startswith("warnset_action_"):
        act = action.replace("warnset_action_", "")
        set_setting(chat_id, "warn_action", act)
        await query.answer("✅ اقدام: " + act)
        await query.edit_message_text("⚠️ سیستم اخطار", reply_markup=warn_menu(uid, chat_id))
        return

    if action == "warn_noop":
        await query.answer()
        return

    await query.answer()


def register(app):
    app.add_handler(CallbackQueryHandler(handler, pattern="^(warnset_|warn_noop)"), group=5)
