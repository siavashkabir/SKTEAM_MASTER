"""broadcast.py — ارسال پیام سراسری (هماهنگ بین دو ربات)"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes, ApplicationHandlerStop
from config import OWNER_ID
import asyncio, logging, sqlite3, datetime
from pathlib import Path

log = logging.getLogger("broadcast")
_pending = {}
_pending_lock = asyncio.Lock()


def _is_owner(uid):
    try: return int(uid) == int(OWNER_ID)
    except: return False


def _db():
    from config import DATABASE_PATH
    return sqlite3.connect(DATABASE_PATH, timeout=5)


def _queue_broadcast(text, target, by):
    c = _db()
    c.execute("""INSERT INTO broadcast_queue (text, target, created_at, created_by)
                 VALUES (?, ?, ?, ?)""",
              (text, target, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), by))
    c.commit()
    rid = c.execute("SELECT last_insert_rowid()").fetchone()[0]
    c.close()
    return rid


async def cmd_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message; user = update.effective_user
    if not _is_owner(user.id):
        await msg.reply_text("⛔ فقط سازنده"); raise ApplicationHandlerStop
    kb = [
        [InlineKeyboardButton("📢 همه‌ی گروه‌ها", callback_data="bc_target:groups")],
        [InlineKeyboardButton("👑 همه‌ی مالکین", callback_data="bc_target:owners")],
        [InlineKeyboardButton("⭐ همه‌ی سودوها", callback_data="bc_target:admins")],
        [InlineKeyboardButton("🌍 همه", callback_data="bc_target:all")],
        [InlineKeyboardButton("❌ انصراف", callback_data="bc_cancel")],
    ]
    await msg.reply_text("📢 **ارسال پیام سراسری**\n━━━━━━━━━━━━━━━━━\nمقصد:",
        parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))
    raise ApplicationHandlerStop


async def cb_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; user = q.from_user
    data = q.data or ""
    log.warning(f"[BC-HIT] uid={user.id} data={data!r}")
    if not _is_owner(user.id): await q.answer("⛔", show_alert=True); return
    # ★ از پنل سازنده
    if data.startswith("bc_start:"):
        kb = [
            [InlineKeyboardButton("📢 همه‌ی گروه‌ها", callback_data="bc_target:groups")],
            [InlineKeyboardButton("👑 همه‌ی مالکین", callback_data="bc_target:owners")],
            [InlineKeyboardButton("⭐ همه‌ی سودوها", callback_data="bc_target:admins")],
            [InlineKeyboardButton("🌍 همه", callback_data="bc_target:all")],
            [InlineKeyboardButton("❌ انصراف", callback_data="bc_cancel")],
        ]
        try:
            await q.edit_message_text("📢 **ارسال پیام سراسری**\n━━━━━━━━━━━━━━━━━\nمقصد:",
                parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))
        except Exception as e:
            log.warning(f"bc_start err: {e}")
        return
    if data == "bc_cancel":
        _pending.pop(user.id, None)
        try: await q.message.delete()
        except: pass
        return
    if data.startswith("bc_target:"):
        target = data.split(":", 1)[1]
        _pending[user.id] = {"target": target, "text": None}
        names = {"groups": "همه‌ی گروه‌ها", "owners": "مالکین", "admins": "سودوها", "all": "همه"}
        await q.edit_message_text(
            f"📢 مقصد: {names.get(target, target)}\n\nمتن پیام:",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ انصراف", callback_data="bc_cancel")]]))


async def msg_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message; user = update.effective_user
    _txt = msg.text if msg else None
    log.warning("[BC-MSG] uid=" + str(user.id) + " pending=" + str(user.id in _pending) + " text=" + repr(_txt))
    if not _is_owner(user.id): return
    info = _pending.get(user.id)
    if not info:
        # ★ pending نداریم → return بدون stop (بقیه handler ها اجرا شن)
        return
    if not msg.text:
        return
    info["text"] = msg.text
    log.warning(f"[BC-MSG] saving text from {user.id}")
    await msg.reply_text(
        f"📢 **پیش‌نمایش:**\n━━━━━━━━━━━━━━━━━\n{msg.text}\n━━━━━━━━━━━━━━━━━\n\nتایید؟",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ ارسال", callback_data="bc_send")],
            [InlineKeyboardButton("❌ انصراف", callback_data="bc_cancel")],
        ]))
    raise ApplicationHandlerStop


async def cb_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; user = q.from_user
    if not _is_owner(user.id): await q.answer("⛔", show_alert=True); return
    info = _pending.pop(user.id, None)
    log.warning(f"[BC-SEND] uid={user.id} info={'yes' if info else 'no'}")
    if not info or not info.get("text"):
        await q.answer("❌ متن ذخیره نشده - دوباره شروع کن", show_alert=True)
        return
    rid = _queue_broadcast(info["text"], info["target"], user.id)
    await q.edit_message_text(
        f"✅ در صف قرار گرفت (ID: {rid})\n"
        f"⏳ ربات‌ها در حداکثر ۳۰ ثانیه آینده پیام رو می‌فرستن.")


def register(app):
    # ★ group=-99999 → بالاتر از همه
    app.add_handler(CommandHandler("broadcast", cmd_broadcast), group=-99999)
    app.add_handler(CallbackQueryHandler(cb_broadcast, pattern="^(bc_start:|bc_(target:|cancel))"), group=-99999)
    app.add_handler(CallbackQueryHandler(cb_send, pattern="^bc_send$"), group=-99999)
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, msg_broadcast),
        group=-99999)
    print("[broadcast] registered (group=-99999)")
