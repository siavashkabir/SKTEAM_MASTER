"""modules/music_player.py — Sk.Team Music Player commands"""
import asyncio
import logging
import re
import time

from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters

log = logging.getLogger(__name__)

SK_SERVER = "http://127.0.0.1:8080"

_FA = str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789")

def _fa2en(s: str) -> str:
    return s.translate(_FA)

async def _aw(x):
    if asyncio.iscoroutine(x):
        return await x
    return x

async def _is_owner(uid: int) -> bool:
    try:
        from config import OWNER_ID
        return int(uid) == int(OWNER_ID)
    except Exception:
        return False

async def _is_sudo(uid: int) -> bool:
    try:
        from database import is_sudo
        return bool(await _aw(is_sudo(uid)))
    except Exception:
        return False

async def _is_owner_or_sudo(uid: int) -> bool:
    if await _is_owner(uid):
        return True
    return await _is_sudo(uid)

async def _can_play(uid: int, cid: int) -> bool:
    if await _is_owner_or_sudo(uid):
        return True
    try:
        from database import is_music_authorized
        return bool(await _aw(is_music_authorized(cid, uid)))
    except Exception:
        return False

async def _post(path: str, payload: dict) -> dict:
    try:
        import httpx
        async with httpx.AsyncClient(timeout=10) as h:
            r = await h.post(f"{SK_SERVER}{path}", json=payload)
            return r.json()
    except Exception as e:
        return {"ok": False, "error": str(e)}

async def _get(path: str, params=None) -> dict:
    try:
        import httpx
        async with httpx.AsyncClient(timeout=10) as h:
            r = await h.get(f"{SK_SERVER}{path}", params=params or {})
            return r.json()
    except Exception as e:
        return {"ok": False, "error": str(e)}

_PLAY_PATTERNS = [
    re.compile(r"^(?:پخش|بزن|پلی)\s+(.+)$"),
    re.compile(r"^(.+?)\s+را\s+(?:پخش|بزن|پلی)(?:\s+کن)?$"),
]

def _parse_play(text: str):
    for p in _PLAY_PATTERNS:
        m = p.match(text)
        if m:
            return m.group(1).strip()
    return None


async def music_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    if msg is None or not msg.text:
        return
    # DEBUG
    import logging as _lg
    _lg.getLogger("music_dbg").warning(
        "MUSIC_HANDLER FIRED: chat=%s user=%s text=%r",
        update.effective_chat.id if update.effective_chat else None,
        update.effective_user.id if update.effective_user else None,
        msg.text[:80] if msg.text else None,
    )
    chat = update.effective_chat
    if chat is None or chat.type not in ("group", "supergroup"):
        return
    user = update.effective_user
    if user is None:
        return

    uid = user.id
    cid = chat.id
    raw = msg.text.strip()
    text = _fa2en(raw)

    # ─── Panel (owner/sudo only, silent for others) ───
    if raw in ("پنل", "پنل پخش", "پلیر پنل"):
        if not await _is_owner_or_sudo(uid):
            return
        await msg.reply_text(
            "🎛 پنل پخش — نسخه ۱\n"
            "━━━━━━━━━━━━━━\n"
            "🔊 برای تست: «پخش googoosh»\n"
            "⏹ توقف | ⏸ مکث | ▶️ ادامه\n"
            "⏭ بعدی | ⏮ قبلی"
        )
        return

    # ─── Ping ───
    if raw.lower() in ("پینگ", "ping"):
        try:
            m = await context.bot.get_chat_member(cid, uid)
            is_admin = m.status in ("administrator", "creator")
        except Exception:
            is_admin = False
        if await _is_owner_or_sudo(uid) or is_admin:
            t0 = time.time()
            r = await _get("/health")
            ms = int((time.time() - t0) * 1000)
            ok = "✅" if r.get("ok") else "❌"
            await msg.reply_text(
                f"🏓 پونگ! {ms}ms\n"
                f"🎵 سرور: {ok}\n"
                f"📋 صف: {r.get('queue', '?')}"
            )
        return

    # ─── Play ───
    q = _parse_play(raw)
    if q:
        if not await _can_play(uid, cid):
            return
        r = await _post("/command", {
            "action": "play", "chat_id": cid,
            "query": q, "requested_by": uid,
        })
        if r.get("ok"):
            await msg.reply_text(f"🎵 در حال آماده‌سازی: {q}")
        else:
            await msg.reply_text(f"❌ {r.get('error', 'خطا')}")
        return

    # ─── Stop ───
    if raw in ("توقف", "بس کن", "استاپ"):
        if not await _can_play(uid, cid):
            return
        await _post("/command", {"action": "stop", "chat_id": cid})
        await msg.reply_text("⏹ متوقف شد")
        return

    # ─── Pause ───
    if raw in ("مکث", "پاز", "pause", "توقف موقت"):
        if not await _can_play(uid, cid):
            return
        await _post("/command", {"action": "pause", "chat_id": cid})
        await msg.reply_text("⏸ موقتاً متوقف")
        return

    # ─── Resume ───
    if raw in ("ادامه", "resume", "continue"):
        if not await _can_play(uid, cid):
            return
        await _post("/command", {"action": "resume", "chat_id": cid})
        await msg.reply_text("▶️ ادامه")
        return

    # ─── Next ───
    if raw in ("بعدی", "next", "اسکیپ", "skip"):
        if not await _can_play(uid, cid):
            return
        await _post("/command", {"action": "next", "chat_id": cid})
        await msg.reply_text("⏭ بعدی")
        return

    # ─── Previous ───
    if raw in ("قبلی", "prev", "previous"):
        if not await _can_play(uid, cid):
            return
        await _post("/command", {"action": "previous", "chat_id": cid})
        await msg.reply_text("⏮ قبلی")
        return

    # ─── Volume ───
    m = re.match(r"^(?:ولوم|صدا|volume)\s+(\d+)$", text)
    if m:
        if not await _can_play(uid, cid):
            return
        v = max(1, min(200, int(m.group(1))))
        await _post("/command", {"action": "volume", "chat_id": cid, "volume": v})
        await msg.reply_text(f"🔊 صدا روی {v}%")
        return


def register(app):
    app.add_handler(
        MessageHandler(filters.TEXT & (filters.ChatType.GROUP | filters.ChatType.SUPERGROUP) & ~filters.COMMAND, music_handler),
        group=6,
    )
    log.info("music_player registered")
