from telegram import Update
from telegram.ext import (
    ApplicationHandlerStop, MessageHandler, CallbackQueryHandler,
    filters, ContextTypes
)
from config import OWNER_ID
from database import is_bot_admin
from modules.subscription import check_active

NL = chr(10)


async def check_group_active_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Middleware - چک کردن اشتراک و نقش کاربر در گروه"""
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user

    if not chat:
        return
    if chat.type not in ("group", "supergroup"):
        return

    # ۱. Owner و Sudo همیشه اجازه دارند
    try:
        if user and (user.id == OWNER_ID or is_bot_admin(user.id)):
            return
    except Exception:
        pass

    # ۲. بررسی اشتراک - هم groups هم subscriptions
    active = False
    import turso_db as sqlite3
    from config import DATABASE_PATH
    from datetime import datetime

    DATE_FORMATS = ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M")

    def is_future_date(date_str):
        if not date_str:
            return True
        for fmt in DATE_FORMATS:
            try:
                return datetime.strptime(date_str, fmt) > datetime.now()
            except Exception:
                continue
        return False

    # چک جدول groups (روش قدیمی)
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        c.execute("SELECT expire_date, activated FROM groups WHERE chat_id=?", (chat.id,))
        row = c.fetchone()
        conn.close()
        if row:
            exp_date, activated = row
            if activated and is_future_date(exp_date):
                active = True
    except Exception as e:
        print("[MIDDLEWARE GRP CHK ERR] " + str(e))

    # ★★★ چک جدول subscriptions (روش جدید) ★★★
    if not active:
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            c = conn.cursor()
            # اگه حداقل یه اشتراک فعال داشت، کافیه
            c.execute("""SELECT expire_date, enabled FROM subscriptions 
                        WHERE chat_id=? AND enabled=1""", (chat.id,))
            subs = c.fetchall()
            conn.close()
            for exp_date, enabled in subs:
                if enabled and is_future_date(exp_date):
                    active = True
                    break
        except Exception as e:
            print("[MIDDLEWARE SUB CHK ERR] " + str(e))

    if not active:
        raise ApplicationHandlerStop

async def check_group_active_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Middleware - چک اشتراک برای callback ها"""
    query = update.callback_query
    if not query:
        return

    user = query.from_user
    chat = query.message.chat if query.message else None
    if not chat:
        return
    if chat.type not in ("group", "supergroup"):
        return

    # ۱. Owner و Sudo همیشه اجازه دارند
    try:
        if user and (user.id == OWNER_ID or is_bot_admin(user.id)):
            return
    except Exception:
        pass

    # ۲. مالک گروه و ادمین‌های تلگرام هم اجازه دارند (برای استفاده از پنل)
    try:
        from database import is_group_owner
        if is_group_owner(chat.id, user.id):
            return
    except Exception:
        pass

    # ۳. ادمین گروه (creator/administrator)
    try:
        member = await chat.get_member(user.id)
        if member.status in ("creator", "administrator"):
            return
    except Exception:
        pass

    # ۴. اگه گروه اشتراک فعال نداشت، بلاک کن
    try:
        active = check_active(chat.id)
    except Exception as e:
        print("[MIDDLEWARE CB ERR] " + str(e))
        active = False

    if not active:
        print("[MIDDLEWARE] blocked callback in chat " + str(chat.id))
        raise ApplicationHandlerStop

async def check_bot_added(update, context):
    """وقتی ربات به گروه اضافه میشه، چک کن اد کننده سودو یا OWNER هست"""
    msg = update.effective_message
    chat = update.effective_chat
    adder = update.effective_user
    if not msg or not chat or not adder:
        return
    if chat.type not in ("group", "supergroup"):
        return
    # آیا خود ربات اد شده؟
    if not msg.new_chat_members:
        return
    bot_id = context.bot.id
    is_bot_added = False
    for m in msg.new_chat_members:
        if m.id == bot_id:
            is_bot_added = True
            break
    if not is_bot_added:
        return
    # چک کن اد کننده سودو یا OWNER هست
    try:
        is_allowed = (adder.id == OWNER_ID) or is_bot_admin(adder.id)
    except Exception:
        is_allowed = False
    if is_allowed:
        try:
            await msg.reply_text(
                "\u2705 ربات با موفقیت به گروه اضافه شد." + NL +
                "\U0001f511 برای فعال‌سازی، اشتراک گروه را از پنل سازنده تنظیم کنید." + NL +
                "\U0001f4de پشتیبانی: @Siavashska"
            )
        except Exception:
            pass
        return
    # اد کننده غیرمجاز
    try:
        await msg.reply_text(
            "\u26a0\ufe0f این ربات فقط توسط سازنده یا سودوهای ربات قابل افزودن است." + NL +
            "\U0001f6ab ربات در حال خروج از گروه..."
        )
    except Exception:
        pass
    try:
        await context.bot.leave_chat(chat.id)
    except Exception as e:
        print("[LEAVE CHAT ERR] " + str(e))
    raise ApplicationHandlerStop


def register(app):
    """ثبت middleware"""
        # هندلر اضافه شدن ربات به گروه
    app.add_handler(
        MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, check_bot_added),
        group=-3
    )
    app.add_handler(
        MessageHandler(filters.ALL, check_group_active_message),
        group=-100
    )
    app.add_handler(
        CallbackQueryHandler(check_group_active_callback),
        group=100
    )
    print("OK module middleware loaded")
