"""helper_cmd.py — مدیریت هلپرها (فقط سازنده)"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes, ApplicationHandlerStop
OWNER_ID = 7955185125
import sqlite3, datetime, logging

log = logging.getLogger("helper_cmd")
_pending = {}


def _is_owner(uid):
    try: return int(uid) == int(OWNER_ID)
    except: return False


def _db():
    from pathlib import Path
    db = Path.home() / "groupbot" / "data" / "groupbot.db"
    return sqlite3.connect(str(db), timeout=5)


async def cmd_helpers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message; user = update.effective_user
    log.warning(f"[H-CMD] uid={user.id} is_owner={_is_owner(user.id)}")
    if not _is_owner(user.id):
        await msg.reply_text("⛔ فقط سازنده"); raise ApplicationHandlerStop
    c = _db()
    rows = c.execute("SELECT id, name, enabled, groups_count FROM helpers").fetchall()
    c.close()
    t = "🚀 **مدیریت هلپرها**\n━━━━━━━━━━━━━━━━━\n"
    if not rows:
        t += "_هنوز هلپری نصب نشده_\n"
    else:
        for r in rows:
            st = "✅" if r[2] else "❌"
            t += f"{st} #{r[0]} {r[1]} ({r[3]} گروه)\n"
    kb = [
        [InlineKeyboardButton("➕ افزودن هلپر", callback_data="h_add")],
        [InlineKeyboardButton("🔄 توزیع خودکار", callback_data="h_auto_assign")],
        [InlineKeyboardButton("🔙 بستن", callback_data="menu_close")],
    ]
    await msg.reply_text(t, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb))
    raise ApplicationHandlerStop


async def cb_helpers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; user = q.from_user
    if not _is_owner(user.id):
        await q.answer("⛔", show_alert=True); return
    data = q.data or ""
    
    if data == "h_add":
        _pending[user.id] = "waiting_name"
        await q.edit_message_text(
            "➕ **افزودن هلپر**\n━━━━━━━━━━━━━━━━━\n"
            "بفرست در قالب JSON:\n"
            "`{\"name\": \"Helper1\", \"session\": \"...\", \"api_id\": 123, \"api_hash\": \"...\"}`",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ انصراف", callback_data="h_cancel")]
            ])
        )
        return
    
    if data == "h_auto_assign":
        c = _db()
        helpers = c.execute("SELECT id FROM helpers WHERE enabled=1").fetchall()
        groups = c.execute("SELECT chat_id FROM groups").fetchall()
        if not helpers:
            c.close()
            await q.answer("❌ هلپری نیست", show_alert=True); return
        # پاک کردن تنظیمات قبلی
        c.execute("DELETE FROM helper_groups")
        # توزیع round-robin
        hid_list = [h[0] for h in helpers]
        counts = {h: 0 for h in hid_list}
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for i, (gid,) in enumerate(groups):
            hid = hid_list[i % len(hid_list)]
            c.execute("INSERT INTO helper_groups (helper_id, chat_id, assigned_at) VALUES (?, ?, ?)",
                      (hid, gid, now))
            counts[hid] += 1
        # آپدیت تعداد
        for hid, cnt in counts.items():
            c.execute("UPDATE helpers SET groups_count=? WHERE id=?", (cnt, hid))
        c.commit()
        c.close()
        await q.answer(f"✅ توزیع شد بین {len(hid_list)} هلپر", show_alert=True)
        return
    
    if data == "h_cancel":
        _pending.pop(user.id, None)
        try: await q.message.delete()
        except: pass
        return


async def msg_helpers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message; user = update.effective_user
    if user.id not in _pending: return
    if not _is_owner(user.id): return
    if _pending[user.id] != "waiting_name": return
    text = (msg.text or "").strip()
    try:
        import json
        data = json.loads(text)
        name = data.get("name", "Helper")
        session = data.get("session", "")
        api_id = int(data.get("api_id", 0))
        api_hash = data.get("api_hash", "")
        if not session or not api_id or not api_hash:
            raise ValueError("فیلدهای ضروری ناقص")
        c = _db()
        c.execute("""INSERT INTO helpers (name, session_string, api_id, api_hash, enabled, created_at, added_by)
                     VALUES (?, ?, ?, ?, 1, ?, ?)""",
                  (name, session, api_id, api_hash,
                   datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user.id))
        c.commit()
        c.close()
        _pending.pop(user.id, None)
        await msg.reply_text(f"✅ هلپر {name} اضافه شد")
    except Exception as e:
        await msg.reply_text(f"❌ خطا: {str(e)[:200]}")
    raise ApplicationHandlerStop


def register(app):
    app.add_handler(CommandHandler(["helpers", "helper"], cmd_helpers), group=-100000)
    app.add_handler(CallbackQueryHandler(cb_helpers, pattern="^h_"), group=-100000)
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE, msg_helpers),
        group=-100000)
    print("[helper_cmd] registered")


def build_helpers_menu(back_cb="adm_panel"):
    """Returns (text, InlineKeyboardMarkup) for helper menu — برای استفاده در edit_message."""
    c = _db()
    rows = c.execute("SELECT id, name, enabled, groups_count FROM helpers").fetchall()
    c.close()
    t = "🚀 **مدیریت هلپرها**\n━━━━━━━━━━━━━━━━━\n"
    if not rows:
        t += "_هنوز هلپری نصب نشده_\n"
    else:
        for r in rows:
            st = "✅" if r[2] else "❌"
            t += f"{st} #{r[0]} {r[1]} ({r[3]} گروه)\n"
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ افزودن هلپر", callback_data="h_add")],
        [InlineKeyboardButton("🔄 توزیع خودکار", callback_data="h_auto_assign")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data=back_cb)],
    ])
    return t, kb
