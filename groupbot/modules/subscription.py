from datetime import datetime, timedelta
from telegram.ext import CommandHandler
from database import get_group, update_group, is_bot_admin
import sqlite3
from config import DATABASE_PATH, OWNER_ID

DATE_FMT = '%Y-%m-%d %H:%M:%S'


def is_privileged(user_id):
    """مالک ربات یا ادمین ربات"""
    if user_id == OWNER_ID:
        return True
    return is_bot_admin(user_id)


def get_expire(chat_id):
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    c.execute("SELECT expire_date FROM groups WHERE chat_id = ?", (chat_id,))
    row = c.fetchone()
    conn.close()
    if row and row[0]:
        return row[0]
    return None


def check_active(chat_id):
    """چک می کنه گروه اشتراک فعال داره یا نه"""
    expire = get_expire(chat_id)
    if not expire:
        return False
    try:
        exp = datetime.strptime(expire, DATE_FMT)
        return exp > datetime.now()
    except Exception:
        return False


async def myid_cmd(update, context):
    await update.message.reply_text("ID: " + str(update.effective_user.id))


async def activate_cmd(update, context):
    user_id = update.effective_user.id
    if not is_privileged(user_id):
        return await update.message.reply_text("⛔ فقط مالک ربات یا ادمین های ربات میتونن اشتراک فعال کنن.")
    if len(context.args) < 1:
        return await update.message.reply_text("مثال: /activate 30")
    try:
        days = int(context.args[0])
    except Exception:
        return await update.message.reply_text("عدد نامعتبر")
    chat_id = update.effective_chat.id
    # ===== محاسبه از تاریخ انقضای فعلی =====
    _base = datetime.now()
    try:
        import sqlite3 as _sq_acc2
        from config import DATABASE_PATH as _DBP_acc2
        _cn_acc2 = _sq_acc2.connect(_DBP_acc2)
        _cr_acc2 = _cn_acc2.cursor()
        _cr_acc2.execute("SELECT expire_date FROM groups WHERE chat_id=?", (chat_id,))
        _rw_acc2 = _cr_acc2.fetchone()
        _cn_acc2.close()
        _cur_acc2 = _rw_acc2[0] if _rw_acc2 and _rw_acc2[0] else None
        if _cur_acc2:
            for _fmt_acc2 in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
                try:
                    _cdt_acc2 = datetime.strptime(_cur_acc2, _fmt_acc2)
                    if _cdt_acc2 > _base:
                        _base = _cdt_acc2
                    break
                except Exception:
                    continue
    except Exception as _e_acc2:
        print("[SUB ACC ERR] " + str(_e_acc2))
    expire = (_base + timedelta(days=days)).strftime(DATE_FMT)
    update_group(chat_id, expire_date=expire, activated=1)
    await update.message.reply_text(
        "✅ گروه فعال شد" + chr(10) +
        "تعداد روز: " + str(days) + chr(10) +
        "انقضا: " + expire
    )


async def deactivate_cmd(update, context):
    if not is_privileged(update.effective_user.id):
        return await update.message.reply_text("⛔ فقط مالک ربات یا ادمین های ربات")
    chat_id = update.effective_chat.id
    update_group(chat_id, expire_date=None, activated=0)
    await update.message.reply_text("❌ گروه غیرفعال شد")


async def status_cmd(update, context):
    chat_id = update.effective_chat.id
    expire = get_expire(chat_id)
    if not expire:
        return await update.message.reply_text("این گروه فعال نیست. با پشتیبانی تماس بگیرید.")
    try:
        exp = datetime.strptime(expire, DATE_FMT)
        if exp > datetime.now():
            remain = exp - datetime.now()
            days = remain.days
            hours = remain.seconds // 3600
            await update.message.reply_text(
                "✅ اشتراک فعال" + chr(10) +
                "انقضا: " + expire + chr(10) +
                "باقی مانده: " + str(days) + " روز و " + str(hours) + " ساعت"
            )
        else:
            await update.message.reply_text("❌ اشتراک منقضی شده" + chr(10) + "تاریخ: " + expire)
    except Exception:
        await update.message.reply_text("تاریخ: " + expire)


def register(app):
    app.add_handler(CommandHandler("myid", myid_cmd))
    app.add_handler(CommandHandler("activate", activate_cmd))
    app.add_handler(CommandHandler("deactivate", deactivate_cmd))
    app.add_handler(CommandHandler("subscription", status_cmd))
