"""sudo_cmd.py — مدیریت سودوها (فقط سازنده)"""
from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, filters, ContextTypes, ApplicationHandlerStop
from database import is_bot_admin, add_bot_admin, remove_bot_admin, get_all_bot_admins
from config import OWNER_ID


def _is_owner(uid):
    try:
        return int(uid) == int(OWNER_ID)
    except:
        return False


def _reply_target(msg):
    if not msg.reply_to_message:
        return None
    u = msg.reply_to_message.from_user
    if not u or u.is_bot:
        return None
    return {
        "user_id": u.id,
        "first_name": u.first_name or "",
        "username": u.username or "",
    }


async def cmd_add_sudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """افزودن سودو با ریپلای"""
    msg = update.effective_message
    user = update.effective_user
    if not _is_owner(user.id):
        await msg.reply_text("⛔ فقط سازنده")
        raise ApplicationHandlerStop
    tgt = _reply_target(msg)
    if not tgt:
        await msg.reply_text("🎯 روی پیام کاربر ریپلای کن")
        raise ApplicationHandlerStop
    add_bot_admin(tgt["user_id"], tgt["first_name"], tgt["username"], user.id)
    disp = ("@" + tgt["username"]) if tgt["username"] else tgt["first_name"]
    await msg.reply_text(f"✅ {disp} سودو شد")
    raise ApplicationHandlerStop


async def cmd_del_sudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    user = update.effective_user
    if not _is_owner(user.id):
        await msg.reply_text("⛔ فقط سازنده")
        raise ApplicationHandlerStop
    tgt = _reply_target(msg)
    if not tgt:
        await msg.reply_text("🎯 روی پیام کاربر ریپلای کن")
        raise ApplicationHandlerStop
    remove_bot_admin(tgt["user_id"])
    disp = ("@" + tgt["username"]) if tgt["username"] else tgt["first_name"]
    await msg.reply_text(f"✅ {disp} از سودو حذف شد")
    raise ApplicationHandlerStop


async def cmd_list_sudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    user = update.effective_user
    if not _is_owner(user.id):
        await msg.reply_text("⛔ فقط سازنده")
        raise ApplicationHandlerStop
    rows = get_all_bot_admins()
    if not rows:
        await msg.reply_text("👑 هنوز سودویی ثبت نشده")
        raise ApplicationHandlerStop
    text = "👑 لیست سودوها:\n━━━━━━━━━━━━━━━━━━\n"
    for r in rows:
        uid = r[0]
        fn = r[1] if len(r) > 1 and r[1] else "—"
        un = r[2] if len(r) > 2 and r[2] else ""
        if un:
            text += f"• {fn} (@{un}) [ID: {uid}]\n"
        else:
            text += f"• {fn} [ID: {uid}]\n"
    text += "━━━━━━━━━━━━━━━━━━\n"
    text += f"📊 تعداد: {len(rows)}"
    await msg.reply_text(text)
    raise ApplicationHandlerStop


async def msg_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """هندل دستورات فارسی متنی"""
    msg = update.effective_message
    if not msg or not msg.text:
        return
    user = update.effective_user
    print("[sudo_msg] uid=" + str(user.id) + " text=" + repr(msg.text))
    if not _is_owner(user.id):
        print("[sudo_msg] NOT owner")
        return
    t = msg.text.strip()
    print("[sudo_msg] stripped=" + repr(t))

    ADD_KEYS = ("افزودن سودو", "افزودن صدا", "+سودو", "+صدا", "add sudo")
    DEL_KEYS = ("حذف سودو", "حذف صدا", "-سودو", "-صدا", "del sudo")
    LIST_KEYS = ("لیست سودو", "لیست صدا", "سودوها", "صداها", "list sudo")

    if t in ADD_KEYS:
        await cmd_add_sudo(update, context)
    elif t in DEL_KEYS:
        await cmd_del_sudo(update, context)
    elif t in LIST_KEYS:
        await cmd_list_sudo(update, context)
    else:
        print("[sudo_msg] NO MATCH")


def register(app):
    app.add_handler(CommandHandler("addsudo", cmd_add_sudo), group=-999)
    app.add_handler(CommandHandler("delsudo", cmd_del_sudo), group=-999)
    app.add_handler(CommandHandler("listsudo", cmd_list_sudo), group=-999)
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, msg_handler),
        group=-999,
    )
    print("[sudo_cmd] registered (TEXT, group=-999)")