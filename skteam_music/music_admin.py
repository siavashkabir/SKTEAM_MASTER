
# -*- coding: utf-8 -*-
# music_admin.py - ترفیع موزیک، مالک، ضبط
import sqlite3, time, logging
from pathlib import Path
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import MessageHandler, CallbackQueryHandler, filters, ApplicationHandlerStop, ContextTypes

log = logging.getLogger("SktTeam")
NL = chr(10)
GB_DB = Path.home() / "groupbot" / "data" / "groupbot.db"
SK_DB = Path.home() / "skteam_music" / "data" / "settings.db"

TRIG_MUSIC_PROMOTE = ["ترفیع موزیک", "+موزیک"]
TRIG_MUSIC_DEMOTE  = ["حذف موزیک", "-موزیک"]
TRIG_RECORD_START  = ["شروع ضبط"]
TRIG_RECORD_STOP   = ["توقف ضبط"]
TRIG_ADD_OWNER     = ["افزودن مالک", "+مالک"]
TRIG_DEL_OWNER     = ["حذف مالک", "-مالک"]
TRIG_LIST_OWNER    = ["مالکین", "لیست مالکین"]

PENDING = {}

def _conn():
    return sqlite3.connect(str(SK_DB), timeout=5)

def ensure_tables():
    try:
        c = _conn()
        c.execute("CREATE TABLE IF NOT EXISTS music_authorized (chat_id INTEGER, user_id INTEGER, until_ts INTEGER DEFAULT 0, added_at INTEGER, PRIMARY KEY (chat_id, user_id))")
        c.execute("CREATE TABLE IF NOT EXISTS sk_group_owners (chat_id INTEGER, user_id INTEGER, added_at INTEGER, first_name TEXT, username TEXT, PRIMARY KEY (chat_id, user_id))")
        try:
            c.execute("ALTER TABLE sk_group_owners ADD COLUMN first_name TEXT")
        except Exception: pass
        try:
            c.execute("ALTER TABLE sk_group_owners ADD COLUMN username TEXT")
        except Exception: pass
        c.commit()
        c.close()
        log.info("[MA] tables ready")
    except Exception as e:
        log.warning("[MA] ensure_tables err: " + str(e))

def _bot_owner():
    try:
        from bot import OWNER_ID
        return OWNER_ID
    except Exception:
        return 7955185125

def is_sk_owner(chat_id, user_id):
    try:
        c = sqlite3.connect(str(GB_DB), timeout=5)
        r = c.execute("SELECT 1 FROM group_owners WHERE chat_id=? AND user_id=?", (chat_id, user_id)).fetchone()
        c.close()
        if r: return True
    except Exception: pass
    try:
        c = _conn()
        r = c.execute("SELECT 1 FROM sk_group_owners WHERE chat_id=? AND user_id=?", (chat_id, user_id)).fetchone()
        c.close()
        if r: return True
    except Exception: pass
    return False

def add_sk_owner(chat_id, user_id, first_name="", username=""):
    c = _conn()
    c.execute("INSERT OR REPLACE INTO sk_group_owners (chat_id, user_id, added_at, first_name, username) VALUES (?, ?, ?, ?, ?)", (chat_id, user_id, int(time.time()), first_name or "", username or ""))
    c.commit(); c.close()

def del_sk_owner(chat_id, user_id):
    c = _conn()
    c.execute("DELETE FROM sk_group_owners WHERE chat_id=? AND user_id=?", (chat_id, user_id))
    c.commit(); c.close()

def list_sk_owners(chat_id):
    try:
        c = _conn()
        rows = c.execute("SELECT user_id, first_name, username FROM sk_group_owners WHERE chat_id=?", (chat_id,)).fetchall()
        c.close()
        return rows
    except Exception:
        return []

def add_music_auth(chat_id, user_id, until_ts=0):
    c = _conn()
    c.execute("INSERT OR REPLACE INTO music_authorized (chat_id, user_id, until_ts, added_at) VALUES (?, ?, ?, ?)", (chat_id, user_id, until_ts, int(time.time())))
    c.commit(); c.close()

def del_music_auth(chat_id, user_id):
    c = _conn()
    c.execute("DELETE FROM music_authorized WHERE chat_id=? AND user_id=?", (chat_id, user_id))
    c.commit(); c.close()

def is_music_auth(chat_id, user_id):
    if user_id == _bot_owner(): return True
    if is_sk_owner(chat_id, user_id): return True
    try:
        c = _conn()
        r = c.execute("SELECT until_ts FROM music_authorized WHERE chat_id=? AND user_id=?", (chat_id, user_id)).fetchone()
        c.close()
        if not r: return False
        until = int(r[0] or 0)
        if until == 0: return True
        return until > int(time.time())
    except Exception:
        return False

def _kb_duration():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("دائمی ♾", callback_data="ma_perm")],
        [InlineKeyboardButton("موقت ⏱", callback_data="ma_temp")],
        [InlineKeyboardButton("❌ انصراف", callback_data="ma_cancel")],
    ])

def _kb_days():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("۱ روز", callback_data="ma_d_1")],
        [InlineKeyboardButton("۲ روز", callback_data="ma_d_2")],
        [InlineKeyboardButton("۳ روز", callback_data="ma_d_3")],
        [InlineKeyboardButton("۷ روز", callback_data="ma_d_7")],
        [InlineKeyboardButton("۳۰ روز", callback_data="ma_d_30")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="ma_back")],
    ])

def _reply_target(msg):
    if not msg.reply_to_message: return None
    u = msg.reply_to_message.from_user
    if not u or u.is_bot: return None
    return {"user_id": u.id, "first_name": u.first_name or "", "username": u.username or ""}

async def ma_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    if not msg or not chat or not user: return
    if chat.type not in ("group", "supergroup"): return
    text = (msg.text or "").strip()
    if not text: return
    is_admin = (user.id == _bot_owner()) or is_sk_owner(chat.id, user.id)
    print("[MA-DBG] user=" + str(user.id) + " chat=" + str(chat.id) + " text=" + repr(text) + " is_admin=" + str(is_admin))

    for trig in TRIG_ADD_OWNER:
        if text == trig:
            if not is_admin:
                await msg.reply_text("⛔ فقط مالک گروه یا سازنده")
                raise ApplicationHandlerStop
            tgt = _reply_target(msg)
            if not tgt:
                await msg.reply_text("🎯 روی پیام کاربر ریپلای کن")
                raise ApplicationHandlerStop
            _fn = tgt.get("first_name") or ""
            _un = tgt.get("username") or ""
            add_sk_owner(chat.id, tgt["user_id"], _fn, _un)
            _disp = ("@" + _un) if _un else _fn
            await msg.reply_text("✅ " + (_disp or "کاربر") + " به مالکین اضافه شد")
            raise ApplicationHandlerStop

    for trig in TRIG_DEL_OWNER:
        if text == trig:
            if not is_admin:
                await msg.reply_text("⛔ فقط مالک گروه یا سازنده")
                raise ApplicationHandlerStop
            tgt = _reply_target(msg)
            if not tgt:
                await msg.reply_text("🎯 روی پیام کاربر ریپلای کن")
                raise ApplicationHandlerStop
            del_sk_owner(chat.id, tgt["user_id"])
            await msg.reply_text("✅ از مالکین حذف شد")
            raise ApplicationHandlerStop

    for trig in TRIG_LIST_OWNER:
        if text == trig:
            owners = list_sk_owners(chat.id)
            if not owners:
                await msg.reply_text("👑 هیچ مالک محلی ثبت نشده")
            else:
                s = "👑 مالکین:" + NL
                for o in owners:
                    _uid = o[0]
                    _fn = o[1] if len(o) > 1 and o[1] else ""
                    _un = o[2] if len(o) > 2 and o[2] else ""
                    if _un:
                        s += "• " + _fn + " (@" + _un + ")" + NL
                    elif _fn:
                        s += "• " + _fn + " [ID: " + str(_uid) + "]" + NL
                    else:
                        s += "• ID: " + str(_uid) + NL
                await msg.reply_text(s)
            raise ApplicationHandlerStop

    for trig in TRIG_MUSIC_PROMOTE:
        if text == trig:
            if not is_admin:
                await msg.reply_text("⛔ فقط مالک گروه یا سازنده")
                raise ApplicationHandlerStop
            tgt = _reply_target(msg)
            if not tgt:
                await msg.reply_text("🎯 روی پیام کاربر ریپلای کن")
                raise ApplicationHandlerStop
            PENDING[user.id] = {"chat_id": chat.id, "target": tgt}
            await msg.reply_text("🎵 ترفیع موزیک برای " + (tgt["first_name"] or "کاربر") + NL + NL + "نوع:", reply_markup=_kb_duration())
            raise ApplicationHandlerStop

    for trig in TRIG_RECORD_START:
        if text == trig:
            if not is_admin:
                raise ApplicationHandlerStop
            try:
                from bot import _sub_is_active
                cid = chat.id
                if not _sub_is_active(cid, "vcall"):
                    raise ApplicationHandlerStop
            except Exception:
                pass
            try:
                import requests
                requests.post("http://127.0.0.1:8080/record_start", json={"chat_id": chat.id}, timeout=5)
            except Exception as e:
                log.warning("[MA] rec start err: " + str(e))
            raise ApplicationHandlerStop

    for trig in TRIG_RECORD_STOP:
        if text == trig:
            if not is_admin:
                raise ApplicationHandlerStop
            try:
                import requests
                requests.post("http://127.0.0.1:8080/record_stop", json={"chat_id": chat.id}, timeout=5)
            except Exception as e:
                log.warning("[MA] rec stop err: " + str(e))
            raise ApplicationHandlerStop

async def ma_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    if not q: return
    data = q.data or ""
    user = q.from_user
    if not user: return
    info = PENDING.get(user.id)
    if not info:
        await q.answer("منقضی شده", show_alert=True); return
    if data == "ma_cancel":
        PENDING.pop(user.id, None)
        try: await q.message.delete()
        except Exception: pass
        return
    if data == "ma_perm":
        add_music_auth(info["chat_id"], info["target"]["user_id"], 0)
        nm = info["target"]["first_name"] or "کاربر"
        PENDING.pop(user.id, None)
        try: await q.message.edit_text("✅ " + nm + " دائمی ادمین موزیک شد")
        except Exception: pass
        return
    if data == "ma_temp":
        try: await q.message.edit_text("⏱ چند روز؟", reply_markup=_kb_days())
        except Exception: pass
        return
    if data.startswith("ma_d_"):
        try: days = int(data.split("_")[-1])
        except Exception: days = 1
        until = int(time.time()) + days * 86400
        add_music_auth(info["chat_id"], info["target"]["user_id"], until)
        nm = info["target"]["first_name"] or "کاربر"
        PENDING.pop(user.id, None)
        try: await q.message.edit_text("✅ " + nm + " برای " + str(days) + " روز ادمین موزیک شد")
        except Exception: pass
        return
    if data == "ma_back":
        try: await q.message.edit_text("نوع:", reply_markup=_kb_duration())
        except Exception: pass
        return
    await q.answer()

def register(app):
    ensure_tables()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ma_handler), group=2)
    app.add_handler(CallbackQueryHandler(ma_callback, pattern="^ma_"), group=2)
    log.info("[MA] music_admin registered")
