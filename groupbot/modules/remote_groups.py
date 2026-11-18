from telegram import InlineKeyboardButton, InlineKeyboardMarkup

NL = chr(10)


def remote_groups_menu(uid, chat_id=0):
    from database import get_all_bot_chats
    chats = get_all_bot_chats()
    btns = []
    for cid, title in chats[:30]:
        t = (title or "بدون نام")[:30]
        btns.append([InlineKeyboardButton("👥 " + t, callback_data="rmt_g:" + str(uid) + ":" + str(cid))])
    btns.append([InlineKeyboardButton("🔙 بازگشت", callback_data="owner_section_back:" + str(uid) + ":" + str(chat_id))])
    btns.append([InlineKeyboardButton("❌ بستن", callback_data="menu_close:" + str(uid))])
    return InlineKeyboardMarkup(btns)


def remote_group_menu(uid, target_chat_id):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔗 دریافت لینک دعوت", callback_data="rmt_link:" + str(uid) + ":" + str(target_chat_id))],
        [InlineKeyboardButton("📊 آمار گروه", callback_data="rmt_stat:" + str(uid) + ":" + str(target_chat_id))],
        [InlineKeyboardButton("📢 ارسال پیام به گروه", callback_data="rmt_msg:" + str(uid) + ":" + str(target_chat_id))],
        [InlineKeyboardButton("📌 ارسال و پین پیام", callback_data="rmt_pin:" + str(uid) + ":" + str(target_chat_id))],
        [InlineKeyboardButton("👥 لیست ادمین‌ها", callback_data="rmt_mem:" + str(uid) + ":" + str(target_chat_id))],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="rmt_groups:" + str(uid) + ":" + str(target_chat_id))],
    ])
