from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler
from database import get_all_notifs, set_notif

NL = chr(10)

NOTIF_ITEMS = [
    ("ban", "🔨 بن / اخراج"),
    ("mute", "🔇 سکوت / آنسکوت"),
    ("warn", "⚠️ اخطار کاربر"),
    ("delete", "🗑️ حذف پیام"),
    ("bot_leave", "🤖 خروج ربات از گروه"),
]

ALWAYS_ON = ["expiry", "owner_leave"]

MENU_TEXT = (
    "🔔 تنظیمات اعلان‌ها" + NL +
    "━━━━━━━━━━━━━━━━" + NL + NL +
    "اینجا می‌تونید تعیین کنید که کدوم اعلان‌ها به پیوی شما ارسال بشه." + NL + NL +
    "روی هر مورد بزنید تا فعال یا غیرفعال بشه:" + NL + NL +
    "ℹ️ اعلان «انقضای اشتراک» همیشه فعال است و قابل تنظیم نیست."
)


def notif_menu(uid, chat_id):
    notifs = get_all_notifs(chat_id)
    keyboard = []
    row = []
    for key, label in NOTIF_ITEMS:
        status = "✅" if notifs.get(key, True) else "❌"
        row.append(InlineKeyboardButton(status + " " + label, callback_data="notif_" + key + ":" + str(uid) + ":" + str(chat_id)))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="op_back:" + str(uid) + ":" + str(chat_id))])
    keyboard.append([InlineKeyboardButton("❌ بستن پنل", callback_data="menu_close:" + str(uid))])
    return InlineKeyboardMarkup(keyboard)


async def handler(update, context):
    query = update.callback_query
    data = query.data
    user = query.from_user
    parts = data.split(":")
    action = parts[0]
    if action == "notif_menu":
        uid = int(parts[1]) if len(parts) > 1 else user.id
        chat_id = int(parts[2]) if len(parts) > 2 else 0
        if user.id != uid:
            await query.answer("این پنل توسط شما باز نشده!", show_alert=True)
            return
        await query.answer()
        await query.edit_message_text(MENU_TEXT, reply_markup=notif_menu(uid, chat_id))
        return
    if action.startswith("notif_"):
        key = action.replace("notif_", "")
        uid = int(parts[1]) if len(parts) > 1 else user.id
        chat_id = int(parts[2]) if len(parts) > 2 else 0
        if user.id != uid:
            await query.answer("این پنل توسط شما باز نشده!", show_alert=True)
            return
        valid_keys = [k for k, _ in NOTIF_ITEMS]
        if key not in valid_keys:
            await query.answer("این اعلان قابل تنظیم نیست!", show_alert=True)
            return
        notifs = get_all_notifs(chat_id)
        current = notifs.get(key, True)
        set_notif(chat_id, key, 0 if current else 1)
        await query.answer("✅ تغییر کرد")
        await query.edit_message_text(MENU_TEXT, reply_markup=notif_menu(uid, chat_id))
        return


def register(app):
    app.add_handler(CallbackQueryHandler(handler, pattern="^(notif_menu|notif_)"), group=5)


async def send_notification(context, chat_id, notif_type, text, force=False):
    """
    ارسال اعلان به مالک گروه.
    - context: از handler
    - chat_id: آیدی گروه
    - notif_type: نوع اعلان (ban, mute, warn, delete, bot_leave, expiry)
    - text: متن پیام
    - force: اگه True باشه، تنظیمات رو چک نمی‌کنه (برای انقضا و خروج مالک)
    """
    from database import is_group_owner, get_notif
    from config import DATABASE_PATH
    import turso_db as sqlite3
    try:
        # اگه force نبود، چک کن تنظیمات کاربر
        if not force:
            if not get_notif(chat_id, notif_type):
                return
        # پیدا کردن مالک گروه
        owner_id = None
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cur = conn.cursor()
            cur.execute("SELECT user_id FROM group_owners WHERE chat_id=? LIMIT 1", (chat_id,))
            row = cur.fetchone()
            if row:
                owner_id = row[0]
            conn.close()
        except Exception:
            pass
        if not owner_id:
            # اگه توی جدول نبود، از دیتابیس groups یا group_owner
            try:
                from database import get_group_owner
                owner_id = get_group_owner(chat_id)
            except Exception:
                pass
        if not owner_id:
            return
        try:
            await context.bot.send_message(chat_id=owner_id, text=text)
        except Exception as e:
            # اگه مالک بلاک کرده، لاگ کن
            print("[NOTIF SEND ERR] chat=" + str(chat_id) + " owner=" + str(owner_id) + " " + str(e))
    except Exception as e:
        print("[NOTIF ERR] " + str(e))
