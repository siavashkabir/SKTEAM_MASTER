from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import MessageHandler, filters, ContextTypes, CallbackQueryHandler
from database import (
    add_vip, remove_vip, is_vip, get_all_vips, get_member,
    is_bot_admin, is_deputy
)
from config import OWNER_ID

NL = chr(10)

VIP_TIME_OPTIONS = [
    ("1h", "1 ساعت", 1),
    ("6h", "6 ساعت", 6),
    ("12h", "12 ساعت", 12),
    ("24h", "24 ساعت", 24),
    ("48h", "48 ساعت", 48),
    ("72h", "72 ساعت", 72),
    ("4d", "4 روز", 96),
    ("5d", "5 روز", 120),
    ("7d", "7 روز", 168),
    ("30d", "30 روز", 720),
    ("permanent", "دائمی", None),
]


def user_display(user):
    """نمایش اسم کاربر با منشن"""
    name = user.first_name or "کاربر"
    if user.username:
        return name + " (@" + user.username + ")"
    return name


def user_display_from_db(first_name, username, user_id):
    name = first_name or "کاربر"
    if username:
        return name + " (@" + username + ")"
    return name


async def is_creator(chat, user_id):
    try:
        m = await chat.get_member(user_id)
        return m.status == "creator"
    except Exception:
        return False


async def can_manage_vip(chat, user_id):
    if await is_creator(chat, user_id):
        return True
    return False


def time_menu(uid, chat_id, target_id, target_name):
    keyboard = []
    row = []
    for key, label, hours in VIP_TIME_OPTIONS:
        row.append(InlineKeyboardButton(label, callback_data="vip_set_" + key + ":" + str(uid) + ":" + str(chat_id) + ":" + str(target_id)))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton("لغو", callback_data="vip_cancel:" + str(uid) + ":" + str(chat_id))])
    return InlineKeyboardMarkup(keyboard)


async def vip_reply_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    if not msg or not chat or not user:
        return
    if chat.type not in ("group", "supergroup"):
        return

    text = (msg.text or "").strip()
    if not text:
        return

    # تنظیم ویژه (دائمی)
    if text == "تنظیم ویژه":
        if not await can_manage_vip(chat, user.id):
            await msg.reply_text("⛔ فقط مالک گروه می تونه عضو ویژه تعیین کنه.")
            return
        if not msg.reply_to_message or not msg.reply_to_message.from_user:
            await msg.reply_text("روی پیام کاربر ریپلای کن و بنویس: تنظیم ویژه")
            return
        target = msg.reply_to_message.from_user
        if target.id == context.bot.id or target.id == user.id:
            return
        ok = add_vip(chat.id, target.id, target.first_name or "", target.username or "", user.id, None)
        if ok:
            await msg.reply_text(
                "کاربر " + user_display(target) + " به صورت دائم به لیست ویژه اضافه شد."
            )
            print("[VIP ADD] " + str(target.id) + " in " + str(chat.id) + " permanent")
        else:
            await msg.reply_text("❌ خطا در ثبت عضو ویژه")
        return

    # تنظیم ویژه زمان دار
    if text.startswith("تنظیم ویژه "):
        if not await can_manage_vip(chat, user.id):
            await msg.reply_text("⛔ فقط مالک گروه می تونه عضو ویژه تعیین کنه.")
            return
        if not msg.reply_to_message or not msg.reply_to_message.from_user:
            await msg.reply_text("روی پیام کاربر ریپلای کن و بنویس: تنظیم ویژه 24")
            return
        target = msg.reply_to_message.from_user
        if target.id == context.bot.id or target.id == user.id:
            return

        parts = text.split()
        if len(parts) < 3:
            await msg.reply_text("مثال: تنظیم ویژه 24")
            return

        try:
            num = int(parts[2])
            if num <= 0:
                raise ValueError
        except Exception:
            await msg.reply_text("❌ عدد نامعتبر. مثال: تنظیم ویژه 24")
            return

        is_day = "روز" in text
        if is_day:
            hours = num * 24
            label = str(num) + " روز"
        else:
            hours = num
            label = str(num) + " ساعت"

        expire_dt = datetime.now() + timedelta(hours=hours)
        expire_str = expire_dt.strftime("%Y-%m-%d %H:%M")

        ok = add_vip(chat.id, target.id, target.first_name or "", target.username or "", user.id, expire_str)
        if ok:
            await msg.reply_text(
                "کاربر " + user_display(target) + " به مدت " + label + " به لیست ویژه اضافه شد."
            )
            print("[VIP ADD] " + str(target.id) + " in " + str(chat.id) + " for " + label)
        else:
            await msg.reply_text("❌ خطا در ثبت عضو ویژه")
        return

    # حذف ویژه
    if text in ("حذف ویژه", "لغو ویژه"):
        if not await can_manage_vip(chat, user.id):
            await msg.reply_text("⛔ فقط مالک گروه می تونه عضو ویژه حذف کنه.")
            return
        if not msg.reply_to_message or not msg.reply_to_message.from_user:
            await msg.reply_text("روی پیام کاربر ریپلای کن و بنویس: حذف ویژه")
            return
        target = msg.reply_to_message.from_user
        if not is_vip(chat.id, target.id):
            await msg.reply_text("ℹ️ کاربر " + user_display(target) + " عضو ویژه نیست.")
            return
        ok = remove_vip(chat.id, target.id)
        if ok:
            await msg.reply_text("کاربر " + user_display(target) + " از لیست ویژه حذف شد.")
            print("[VIP REMOVE] " + str(target.id) + " from " + str(chat.id))
        else:
            await msg.reply_text("❌ خطا در حذف")
        return

    # لیست ویژه ها
    if text in ("لیست ویژه ها", "اعضای ویژه"):
        vips = get_all_vips(chat.id)
        if not vips:
            await msg.reply_text("📋 هنوز عضو ویژه ای وجود نداره.")
            return
        lines = []
        for i, (uid, first_name, username, added_by, added_at, expire_at) in enumerate(vips, 1):
            display = user_display_from_db(first_name, username, uid)
            exp_label = "دائمی" if not expire_at else expire_at
            lines.append(str(i) + ". " + display + NL + "   ⏰ " + exp_label)
        text_out = "📋 لیست اعضای ویژه:" + NL + "━━━━━━━━━━━━━━━━━━" + NL + NL + (NL + NL).join(lines)
        await msg.reply_text(text_out)
        return


async def vip_cb_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    clicker = query.from_user.id

    parts = data.split(":")
    action = parts[0]
    owner = int(parts[1]) if len(parts) > 1 else clicker

    if clicker != owner:
        await query.answer("این منو برای شما نیست", show_alert=True)
        return

    await query.answer()

    if action == "vip_cancel":
        try:
            await query.message.delete()
        except Exception:
            pass
        return

    if action.startswith("vip_set_"):
        if len(parts) < 4:
            return
        key = action.replace("vip_set_", "")
        chat_id = int(parts[2])
        target_id = int(parts[3])

        try:
            chat = await context.bot.get_chat(chat_id)
            m = await chat.get_member(clicker)
            if m.status != "creator":
                await query.answer("فقط مالک گروه", show_alert=True)
                return
        except Exception:
            await query.answer("خطا", show_alert=True)
            return

        hours = None
        label = "دائمی"
        for k, lbl, h in VIP_TIME_OPTIONS:
            if k == key:
                hours = h
                label = lbl
                break

        try:
            target = await context.bot.get_chat(target_id)
            t_name = target.first_name or "کاربر"
            t_username = target.username or ""
        except Exception:
            t_name = "کاربر"
            t_username = ""

        if hours is None:
            expire_str = None
        else:
            expire_str = (datetime.now() + timedelta(hours=hours)).strftime("%Y-%m-%d %H:%M")

        ok = add_vip(chat_id, target_id, t_name, t_username, clicker, expire_str)
        if ok:
            display = user_display_from_db(t_name, t_username, target_id)
            if label == "دائمی":
                msg_text = "کاربر " + display + " به صورت دائم به لیست ویژه اضافه شد."
            else:
                msg_text = "کاربر " + display + " به مدت " + label + " به لیست ویژه اضافه شد."
            try:
                await query.edit_message_text(msg_text)
            except Exception:
                pass
        else:
            try:
                await query.edit_message_text("❌ خطا در ثبت")
            except Exception:
                pass
        return


def register(app):
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, vip_reply_handler, block=False), group=50)
    app.add_handler(CallbackQueryHandler(vip_cb_handler, pattern="^vip_"), group=51)
