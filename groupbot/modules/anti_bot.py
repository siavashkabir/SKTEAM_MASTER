"""Anti-Bot - جلوگیری از اضافه شدن ربات‌های دیگه به گروه"""
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes, MessageHandler, CallbackQueryHandler,
    filters, ApplicationHandlerStop
)
from config import OWNER_ID
from database import get_chat_raid_setting, set_chat_raid_setting, is_bot_owner_or_sudo


def _is_enabled(chat_id):
    return get_chat_raid_setting(chat_id, "antibbot_enabled", "0") == "1"


def _get_action(chat_id):
    return get_chat_raid_setting(chat_id, "antibbot_action", "kick")


async def check_new_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    if not msg or not chat or chat.type not in ("group", "supergroup"):
        return
    if not msg.new_chat_members:
        return
    if not _is_enabled(chat.id):
        return

    our_bot_id = context.bot.id
    new_bots = [m for m in msg.new_chat_members if m.is_bot and m.id != our_bot_id]
    if not new_bots:
        return

    action = _get_action(chat.id)
    kicked = 0
    for bot_member in new_bots:
        try:
            if action == "ban":
                await context.bot.ban_chat_member(chat.id, bot_member.id)
            else:
                await context.bot.ban_chat_member(chat.id, bot_member.id)
                await context.bot.unban_chat_member(chat.id, bot_member.id)
            kicked += 1
            print(f"[ANTI-BOT] {action}ed bot {bot_member.id} from {chat.id}")
        except Exception as e:
            print(f"[ANTI-BOT ERR] {e}")

    if kicked > 0:
        try:
            names = ", ".join([f"@{b.username}" if b.username else b.first_name for b in new_bots])
            action_txt = "بن" if action == "ban" else "اخراج"
            sent = await context.bot.send_message(
                chat_id=chat.id,
                text=f"🤖 *ربات غیرمجاز {action_txt} شد!*\n\n📛 {names}\n\n⚠️ فقط ربات اصلی این گروه مجاز به موندنه.",
                parse_mode="Markdown"
            )
            async def _del():
                await asyncio.sleep(10)
                try:
                    await context.bot.delete_message(chat_id=chat.id, message_id=sent.message_id)
                except Exception:
                    pass
            asyncio.create_task(_del())
        except Exception as e:
            print(f"[ABOT NOTIFY ERR] {e}")
        try:
            await context.bot.send_message(
                chat_id=OWNER_ID,
                text=f"🤖 *Anti-Bot Alert*\n\n📍 {chat.title or chat.id}\n🆔 `{chat.id}`\n🚫 ربات‌های بلاک: `{kicked}`",
                parse_mode="Markdown"
            )
        except Exception:
            pass


def build_antibot_panel(uid, chat_id):
    enabled = _is_enabled(chat_id)
    action = _get_action(chat_id)
    action_lbl = "🚫 بن دائم" if action == "ban" else "👢 کیک موقت"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"🤖 Anti-Bot: {'✅ فعال' if enabled else '❌ غیرفعال'}", callback_data=f"abot_tog:{uid}:{chat_id}")],
        [InlineKeyboardButton(f"⚙️ اکشن: {action_lbl}", callback_data=f"abot_action:{uid}:{chat_id}")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data=f"menu_settings:{uid}:{chat_id}")],
    ])


async def antibot_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    data = query.data
    parts = data.split(":")
    action = parts[0]
    # دسترسی: Owner، Sudo، مالک گروه
    uid = user.id
    chat_id = 0
    try:
        if len(parts) > 2 and parts[2].lstrip("-").isdigit():
            chat_id = int(parts[2])
    except Exception:
        pass
    allowed = False
    try:
        if user.id == OWNER_ID or is_bot_owner_or_sudo(user.id):
            allowed = True
    except Exception:
        pass
    if not allowed:
        try:
            from database import is_group_owner
            if is_group_owner(chat_id, user.id):
                allowed = True
        except Exception:
            pass
    if not allowed:
        try:
            member = await query.message.chat.get_member(user.id)
            if member.status in ("creator", "administrator"):
                allowed = True
        except Exception:
            pass
    if not allowed:
        await query.answer("⛔ فقط سازنده یا مالک گروه!", show_alert=True)
        return
    if action == "abot_panel":
        try:
            await query.edit_message_text(
                "🤖 *Anti-Bot*\n\nهر ربات دیگه‌ای که به این گروه اضافه بشه، خودکار بلاک می‌شه.\n\nاز دکمه‌ها استفاده کن:",
                reply_markup=build_antibot_panel(uid, chat_id),
                parse_mode="Markdown"
            )
        except Exception as e:
            print("[ABOT PANEL ERR]", str(e))
        await query.answer()
        return
    if action == "abot_tog":
        cur = _is_enabled(chat_id)
        new = "0" if cur else "1"
        set_chat_raid_setting(chat_id, "antibbot_enabled", new)
        try:
            await query.edit_message_reply_markup(reply_markup=build_antibot_panel(uid, chat_id))
        except Exception:
            pass
        await query.answer("✅ فعال" if new == "1" else "❌ غیرفعال")
        return
    if action == "abot_action":
        cur = _get_action(chat_id)
        new = "ban" if cur == "kick" else "kick"
        set_chat_raid_setting(chat_id, "antibbot_action", new)
        try:
            await query.edit_message_reply_markup(reply_markup=build_antibot_panel(uid, chat_id))
        except Exception:
            pass
        await query.answer("✅ تغییر کرد")
        return
    await query.answer()


def register(app):
    app.add_handler(
        MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, check_new_bot),
        group=-185
    )
    app.add_handler(
        CallbackQueryHandler(antibot_cb, pattern=r"^abot_"),
        group=-42
    )
    print("OK module anti_bot loaded")
