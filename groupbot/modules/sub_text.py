"""
ماژول دستورات نوشتاری اشتراک
فقط برای OWNER و SUDO
فرمت: اشتراک [نوع] [مدت]
مثال:
  اشتراک موزیک 30 روز
  اشتراک مدیریت گروه 60
  اشتراک nsfw 90 روز
  اشتراک ویسکال 180
"""
import re
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import (
    ContextTypes, MessageHandler, filters, ApplicationHandlerStop
)

NL = chr(10)

SUB_PATTERN = re.compile(
    r'^اشتراک\s+(.+?)\s+(\d+)\s*(?:روز|روزه)?\s*$',
    re.UNICODE
)

SUB_MAP = {
    'موزیک': 'music',
    'مزیک': 'music',
    'مدیریت گروه': 'manager',
    'مدیریت': 'manager',
    'گروه': 'manager',
    'nsfw': 'nsfw',
    'ویسکال': 'vcall',
    'ویس کال': 'vcall',
    'ویس‌کال': 'vcall',
    'ویس': 'vcall',
}

SUB_LABEL = {
    'music': '🎵 موزیک',
    'manager': '👤 مدیریت گروه',
    'nsfw': '🔞 NSFW',
    'vcall': '📞 ویس‌کال',
}


async def sub_text_handler(update, context):
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    if not msg or not chat or not user or not msg.text:
        return
    if chat.type not in ("group", "supergroup"):
        return
    if user.is_bot:
        return

    text = msg.text.strip()
    match = SUB_PATTERN.match(text)
    if not match:
        return

    # چک دسترسی (OWNER یا SUDO)
    try:
        from config import OWNER_ID
        from database import is_bot_owner_or_sudo
        if user.id != OWNER_ID and not is_bot_owner_or_sudo(user.id):
            return
    except Exception:
        return

    type_str = match.group(1).strip().lower()
    days = int(match.group(2))

    sub_type = None
    for k, v in SUB_MAP.items():
        if k.lower() == type_str:
            sub_type = v
            break

    if sub_type is None:
        await msg.reply_text(
            "❌ نوع اشتراک نامعتبر." + NL +
            "گزینه‌ها: موزیک، مدیریت گروه، NSFW، ویس‌کال"
        )
        raise ApplicationHandlerStop

    # محاسبه از انقضای فعلی (اگه فعاله)
    target_chat = chat.id
    _base = datetime.now()
    try:
        from database import get_expire, get_subscription
        _cur = None
        if sub_type == "manager":
            _cur = get_expire(target_chat)
        else:
            _s = get_subscription(target_chat, sub_type)
            if _s and _s[0]:
                _cur = _s[0]
        if _cur:
            for _fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
                try:
                    _c = datetime.strptime(_cur, _fmt)
                    if _c > _base:
                        _base = _c
                    break
                except Exception:
                    continue
    except Exception:
        pass

    _new = (_base + timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")

    try:
        if sub_type == "manager":
            from database import update_group
            update_group(target_chat, expire_date=_new, activated=1)
        else:
            from database import set_subscription
            set_subscription(target_chat, sub_type, _new, enabled=1)

        reply = ("✅ اشتراک فعال شد" + NL + "━━━━━━━━━━━━━━" + NL +
                 "👥 گروه: " + (chat.title or "بدون نام") + NL +
                 "💳 اشتراک: " + SUB_LABEL.get(sub_type, sub_type) + NL +
                 "📅 مدت: " + str(days) + " روز" + NL +
                 "📅 انقضا: " + _new)
        await msg.reply_text(reply)
    except Exception as e:
        await msg.reply_text("❌ خطا: " + str(e)[:200])

    raise ApplicationHandlerStop


def register(app):
    app.add_handler(
        MessageHandler(filters.TEXT & filters.ChatType.GROUPS, sub_text_handler),
        group=2
    )
    print("OK module sub_text loaded")
