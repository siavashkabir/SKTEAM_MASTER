"""
Global Cooldown - جلوگیری از تکرار دستورات
هر کاربر توی هر گروه، فقط هر N ثانیه می‌تونه یه دستور تکراری بفرسته
مقدار N از پنل سازنده قابل تنظیمه (پیش‌فرض: 5)
"""
import time
from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters, ApplicationHandlerStop
from config import OWNER_ID

# ⚡ Cooldown table
_COOLDOWN = {}
DEFAULT_COOLDOWN = 30

# دستوراتی که نباید cooldown داشته باشن (خیلی سریع باید اجرا بشن)
EXEMPT_COMMANDS = {
    "start", "help", "menu", "panel",
    "reset", "restart", "stop", "پنل", "panel"
}


def _get_cooldown_seconds():
    """گرفتن مقدار cooldown از دیتابیس"""
    try:
        from database import get_setting
        val = get_setting(0, "sys_cooldown_seconds", str(DEFAULT_COOLDOWN))
        sec = int(val)
        if sec < 0:
            return 0
        if sec > 120:
            return 120
        return sec
    except Exception:
        return DEFAULT_COOLDOWN


def _normalize_trigger(text):
    """استخراج trigger از متن پیام"""
    if not text:
        return None
    t = text.strip().lower()
    # اگه دستور بود
    if t.startswith("/"):
        # حذف @username از آخر دستور
        cmd = t.split()[0].split("@")[0]
        return cmd
    # اگه کلمه کلیدی تکی بود (مثل «پنل»، «ربات»، «اسپم‌ترکر» و...)
    if len(t.split()) <= 2:
        return t
    return None


def _is_on_cooldown(user_id, chat_id, trigger, is_owner=False):
    """چک می‌کنه کاربر توی cooldown هست یا نه"""
    if is_owner:
        return False  # Owner محدودیت نداره

    # دستورات معاف
    if trigger and trigger.lstrip("/") in EXEMPT_COMMANDS:
        return False

    cooldown_sec = _get_cooldown_seconds()

    # اگه cooldown صفر باشه، هیچ محدودیتی اعمال نمی‌شه
    if cooldown_sec == 0:
        return False

    key = (user_id, chat_id, trigger)
    now = time.time()
    last = _COOLDOWN.get(key, 0)

    if now - last < cooldown_sec:
        return True

    _COOLDOWN[key] = now

    # پاکسازی قدیمی‌ها
    if len(_COOLDOWN) > 2000:
        cutoff = now - 3600
        for k in list(_COOLDOWN.keys()):
            if _COOLDOWN[k] < cutoff:
                del _COOLDOWN[k]

    return False


async def cooldown_middleware(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # [FIXED] کلمه پنل از cooldown معاف است
    try:
        if msg.text and msg.text.strip() in ("پنل", "panel", "PANEL"):
            return
    except Exception:
        pass
    """چک cooldown برای همه پیام‌ها"""
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    if not msg or not chat or not user:
        return
    if user.is_bot:
        return
    if chat.type not in ("group", "supergroup"):
        return

    text = msg.text or msg.caption or ""
    trigger = _normalize_trigger(text)
    if not trigger:
        return

    is_owner = user.id == OWNER_ID

    if _is_on_cooldown(user.id, chat.id, trigger, is_owner):
        # کاربر تکراری فرستاده - پیامش رو پاک کن (اگه بتونیم) و بلاک کن
        try:
            await msg.delete()
        except Exception:
            pass
        print(f"[COOLDOWN] Blocked duplicate: user={user.id} chat={chat.id} trigger={trigger!r}")
        raise ApplicationHandlerStop


def register(app):
    # توی گروه -300 که قبل از همه چیز اجرا بشه
    app.add_handler(
        MessageHandler(filters.ALL & filters.ChatType.GROUPS, cooldown_middleware),
        group=-300
    )
    print(f"OK module global_cooldown loaded (cooldown={_get_cooldown_seconds()}s)")
