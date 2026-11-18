import os
import urllib.parse
from datetime import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import MessageHandler, filters, CallbackQueryHandler
from database import is_bot_admin
from config import OWNER_ID
from modules.i18n import t

NL = chr(10)
LINK_CACHE = {}


def link_main_menu(uid, chat_id):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔗 لینک یکبار مصرف", callback_data="link_once:" + str(uid) + ":" + str(chat_id))],
        [InlineKeyboardButton("♾️ لینک دائمی", callback_data="link_perm:" + str(uid) + ":" + str(chat_id))],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="menu_settings:" + str(uid) + ":" + str(chat_id))],
    ])


def link_result_menu(uid, chat_id, link_url):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📤 اشتراک‌گذاری", url="https://t.me/share/url?url=" + urllib.parse.quote(link_url) + "&text=" + urllib.parse.quote("لینک گروه"))],
        [InlineKeyboardButton("📋 کپی لینک", callback_data="link_copy:" + str(uid) + ":" + str(chat_id))],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="link_menu:" + str(uid) + ":" + str(chat_id))],
    ])


async def handler(update, context):
    query = update.callback_query
    data = query.data
    clicker = query.from_user.id
    parts = data.split(":")
    action = parts[0]
    owner = int(parts[1]) if len(parts) > 1 else clicker
    chat_id = int(parts[2]) if len(parts) > 2 else 0

    if clicker != owner and clicker != OWNER_ID:
        await query.answer("این پنل توسط شما باز نشده!", show_alert=True)
        return

    await query.answer()

    if action == "link_close":
        try:
            await query.message.delete()
        except Exception:
            pass
        return

    if action == "link_menu":
        try:
            await query.edit_message_text(
                "🔗 مدیریت لینک گروه" + NL + NL +
                "لینک یکبار مصرف: بعد از اولین استفاده منقضی می‌شود." + NL +
                "لینک دائمی: همیشه کار می‌کند." + NL,
                reply_markup=link_main_menu(owner, chat_id)
            )
        except Exception as e:
            print("[LINK MENU ERR] " + str(e))
        return

    if action == "link_once":
        try:
            link = await context.bot.create_chat_invite_link(
                chat_id=chat_id,
                member_limit=1,
                expire_date=int((datetime.now().timestamp() + 86400))
            )
            link_url = link.invite_link
            LINK_CACHE[str(chat_id)] = link_url
            text = "🔗 لینک یکبار مصرف شما ساخته شد:" + NL + link_url
            await query.edit_message_text(text, reply_markup=link_result_menu(owner, chat_id, link_url))
        except Exception as e:
            print("[LINK ONCE ERR] " + str(e))
            await query.edit_message_text("❌ خطا در ساخت لینک: " + str(e))
        return

    if action == "link_perm":
        try:
            chat = await context.bot.get_chat(chat_id)
            link_url = chat.invite_link
            if not link_url:
                link = await context.bot.create_chat_invite_link(chat_id=chat_id, name="Permanent")
                link_url = link.invite_link
            LINK_CACHE[str(chat_id)] = link_url
            text = "♾️ لینک دائمی گروه:" + NL + link_url
            await query.edit_message_text(text, reply_markup=link_result_menu(owner, chat_id, link_url))
        except Exception as e:
            print("[LINK PERM ERR] " + str(e))
            await query.edit_message_text("❌ خطا در ساخت لینک: " + str(e))
        return

    if action == "link_copy":
        link_url = LINK_CACHE.get(str(chat_id), "")
        await query.answer("لینک کپی شد: " + link_url[:30] + "...", show_alert=True)
        return


def register(app):
    app.add_handler(CallbackQueryHandler(handler, pattern="^(link_)"), group=5)
