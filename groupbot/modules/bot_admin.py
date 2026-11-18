from datetime import datetime
from telegram import Update
from telegram.ext import MessageHandler, filters, ContextTypes
from database import (
    add_bot_admin, remove_bot_admin, is_bot_admin,
    get_all_bot_admins
)
from config import OWNER_ID

NL = chr(10)

TRIGGER_ADD = ["ادمین ربات کن", "افزودن ادمین ربات", "اضافه کردن ادمین ربات", "ادمین کن"]
TRIGGER_REMOVE = ["حذف ادمین ربات", "عزل ادمین ربات", "حذف ادمین"]
TRIGGER_LIST = ["لیست ادمین های ربات", "ادمین های ربات", "لیست ادمین ها"]


def is_owner(user_id):
    return user_id == OWNER_ID


async def reply_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    if not msg or not chat or not user:
        return

    # فقط توی پی وی ربات
    if chat.type != "private":
        return

    text = (msg.text or "").strip()
    if not text:
        return

    print("[BOT ADMIN PV] " + text + " from " + str(user.id))

    # =====================================
    # لیست ادمین های ربات
    # =====================================
    if text in TRIGGER_LIST:
        if not is_owner(user.id) and not is_bot_admin(user.id):
            await msg.reply_text("⛔ شما دسترسی ندارید.")
            return
        admins = get_all_bot_admins()
        if not admins:
            await msg.reply_text("📋 هنوز ادمین رباتی اضافه نشده." + NL + NL + "برای اضافه کردن:" + NL + "1. روی پیام کاربر توی یه گروه ریپلای کن" + NL + "2. پیام رو فوروارد کن به همین پی وی" + NL + "3. بنویس: ادمین ربات کن")
            return
        lines = []
        for i, (uid, first_name, username, added_at) in enumerate(admins, 1):
            uname = ("@" + username) if username else ""
            lines.append(str(i) + ". " + (first_name or "بدون نام") + " " + uname + NL + "   ID: " + str(uid) + NL + "   " + str(added_at))
        text_out = "📋 لیست ادمین های ربات:" + NL + "━━━━━━━━━━━━━━━━━━" + NL + NL + (NL + NL).join(lines)
        await msg.reply_text(text_out)
        return

    # =====================================
    # افزودن ادمین ربات (فقط مالک)
    # =====================================
    if text in TRIGGER_ADD:
        if not is_owner(user.id):
            await msg.reply_text("⛔ فقط مالک ربات میتونه ادمین ربات اضافه کنه.")
            return
        # چک کن ریپلای داره یا فوروارد
        target = None
        if msg.reply_to_message:
            # ریپلای روی پیام شخص
            if msg.reply_to_message.from_user:
                target = msg.reply_to_message.from_user
            # یا فوروارد از یه کاربر
            elif msg.reply_to_message.forward_from:
                target = msg.reply_to_message.forward_from
        # یا فوروارد مستقیم
        elif msg.forward_from:
            target = msg.forward_from

        if not target:
            await msg.reply_text(
                "📌 روش استفاده:" + NL + NL +
                "روش ۱ - ریپلای:" + NL +
                "توی پی وی ربات، روی پیام فوروارد شده کاربر ریپلای کن و بنویس: ادمین ربات کن" + NL + NL +
                "روش ۲ - فوروارد:" + NL +
                "یه پیام از کاربر مورد نظر رو برام فوروارد کن و بنویس: ادمین ربات کن" + NL + NL +
                "روش ۳ - آیدی عددی:" + NL +
                "بنویس: ادمین ربات کن 123456789" + NL + "(به جای 123456789 آیدی عددی کاربر)"
            )
            return
        if target.id == context.bot.id:
            await msg.reply_text("ربات رو نمیشه ادمین کرد!")
            return
        if target.id == OWNER_ID:
            await msg.reply_text("مالک ربات از قبل همه دسترسی ها رو داره.")
            return
        if is_bot_admin(target.id):
            await msg.reply_text("ℹ️ " + (target.first_name or "کاربر") + " از قبل ادمین ربات هست.")
            return
        ok = add_bot_admin(target.id, target.first_name or "", target.username or "", user.id)
        if ok:
            await msg.reply_text(
                "✅ " + (target.first_name or "کاربر") + " به عنوان ادمین ربات اضافه شد." + NL +
                "🆔 آیدی: " + str(target.id) + NL + NL +
                "🔓 دسترسی ها:" + NL +
                "• افزودن ربات به گروه های دیگه" + NL +
                "• تمدید اشتراک گروه ها (فقط توی گروه هایی که خودش مالکه)" + NL +
                "• راه اندازی مجدد ربات (دستور ریستارت)" + NL +
                "• پیکربندی ادمین ها (دستور پیکربندی)" + NL + NL +
                "🔒 بدون دسترسی به:" + NL +
                "• تغییر تنظیمات گروه" + NL +
                "• مدیریت قفل ها" + NL +
                "• تغییرات NSFW و اخطار"
            )
            print("[BOT ADMIN ADD] " + str(target.id) + " by " + str(user.id))
        else:
            await msg.reply_text("❌ خطا در افزودن ادمین ربات")
        return

    # =====================================
    # حذف ادمین ربات (فقط مالک)
    # =====================================
    if text in TRIGGER_REMOVE:
        if not is_owner(user.id):
            await msg.reply_text("⛔ فقط مالک ربات میتونه ادمین ربات رو حذف کنه.")
            return

        target = None
        if msg.reply_to_message and msg.reply_to_message.from_user:
            target = msg.reply_to_message.from_user
        elif msg.reply_to_message and msg.reply_to_message.forward_from:
            target = msg.reply_to_message.forward_from
        elif msg.forward_from:
            target = msg.forward_from

        if not target:
            # شاید با آیدی عددی داده
            parts = text.split()
            if len(parts) >= 2:
                try:
                    target_id = int(parts[-1])
                    if not is_bot_admin(target_id):
                        await msg.reply_text("ℹ️ این کاربر ادمین ربات نیست.")
                        return
                    ok = remove_bot_admin(target_id)
                    if ok:
                        await msg.reply_text("✅ کاربر با آیدی " + str(target_id) + " از ادمین های ربات حذف شد.")
                    else:
                        await msg.reply_text("❌ خطا در حذف.")
                    return
                except Exception:
                    pass
            await msg.reply_text(
                "📌 روش استفاده:" + NL +
                "1. روی پیام کاربر توی پی وی ریپلای کن و بنویس: حذف ادمین ربات" + NL +
                "2. یا بنویس: حذف ادمین ربات 123456789" + NL +
                "(به جای 123456789 آیدی عددی کاربر)"
            )
            return

        if not is_bot_admin(target.id):
            await msg.reply_text("ℹ️ " + (target.first_name or "کاربر") + " ادمین ربات نیست.")
            return
        ok = remove_bot_admin(target.id)
        if ok:
            await msg.reply_text("✅ " + (target.first_name or "کاربر") + " از ادمین های ربات حذف شد.")
            print("[BOT ADMIN REMOVE] " + str(target.id) + " by " + str(user.id))
        else:
            await msg.reply_text("❌ خطا در حذف ادمین ربات")
        return


def register(app):
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_handler, block=False), group=25)
