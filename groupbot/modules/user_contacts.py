"""User Contacts - بانک اطلاعاتی کاربران"""
import os
import csv
import json
import turso_db as sqlite3
import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes, CommandHandler, MessageHandler, CallbackQueryHandler,
    filters, ApplicationHandlerStop
)
from config import OWNER_ID, DATABASE_PATH
from database import (
    upsert_user_contact, get_user_contact, get_contacts_stats,
    get_all_user_contacts, delete_user_contact, increment_user_groups_count,
    is_bot_admin, is_group_owner, get_setting, log_group_event
)


# ============= ثبت کاربر =============

async def track_user_pv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """وقتی کاربر توی پیوی /start می‌زنه"""
    user = update.effective_user
    if not user:
        return
    upsert_user_contact(
        user.id, user.first_name, getattr(user, "last_name", None),
        user.username, user.language_code, getattr(user, "is_premium", False),
        has_started=True, source="pv_start"
    )


async def track_user_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """هر پیام توی گروه - آپدیت last_seen و groups_count"""
    user = update.effective_user
    chat = update.effective_chat
    if not user or not chat or chat.type not in ("group", "supergroup"):
        return
    if user.is_bot:
        return
    upsert_user_contact(
        user.id, user.first_name, getattr(user, "last_name", None),
        user.username, user.language_code, getattr(user, "is_premium", False),
        source="group"
    )


async def track_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """کاربر جدید وارد گروه شد"""
    msg = update.effective_message
    chat = update.effective_chat
    if not msg or not chat or not msg.new_chat_members:
        return
    for m in msg.new_chat_members:
        if m.is_bot:
            continue
        upsert_user_contact(
            m.id, m.first_name, getattr(m, "last_name", None),
            m.username, m.language_code, getattr(m, "is_premium", False),
            source="group_join"
        )
        increment_user_groups_count(m.id)


async def track_left_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """کاربر از گروه خارج شد - ثبت توی group_events"""
    msg = update.effective_message
    chat = update.effective_chat
    if not msg or not chat:
        return
    left = msg.left_chat_member
    if not left or left.is_bot:
        return
    try:
        from database import log_group_event
        log_group_event(chat.id, "leave", left.id, None)
    except Exception as e:
        print("[TRACK LEAVE ERR]", str(e))


# ============= دستور /userinfo =============

def _fmt_time(t):
    if not t:
        return "نامعلوم"
    return t


async def userinfo_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/userinfo - نمایش اطلاعات کاربر"""
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    if not msg or not user:
        return

    # چک دسترسی: فقط Owner و Sudo (اگه توگل سودو فعاله)
    is_owner = user.id == OWNER_ID
    is_sudo = False
    try:
        is_sudo = is_bot_admin(user.id)
    except Exception:
        pass
    sudo_allowed = get_setting(0, "sys_sudo_userinfo", "0") == "1"

    if not is_owner and not (is_sudo and sudo_allowed):
        return  # فقط Owner و (Sudo اگه فعاله)

    # پیدا کردن target
    target = None
    if msg.reply_to_message and msg.reply_to_message.from_user:
        target = msg.reply_to_message.from_user
    elif context.args:
        arg = context.args[0]
        if arg.startswith("@") or not arg.lstrip("-").isdigit():
            uname = arg.lstrip("@").lower()
            try:
                conn = sqlite3.connect(DATABASE_PATH)
                c = conn.cursor()
                c.execute("SELECT user_id, first_name, last_name, username FROM user_contacts WHERE LOWER(username)=?", (uname,))
                r = c.fetchone()
                conn.close()
                if r:
                    target = {"id": r[0], "first_name": r[1], "last_name": r[2], "username": r[3]}
            except Exception:
                pass
        else:
            try:
                tid = int(arg)
                target = {"id": tid, "first_name": "", "last_name": "", "username": ""}
            except Exception:
                pass

    if not target:
        await msg.reply_text("❌ کاربر رو پیدا نکردم.\nروی پیام کاربر ریپلای کن یا `/userinfo @username` یا `/userinfo 123456789` بزن.", parse_mode="Markdown")
        return

    # اطلاعات از دیتابیس
    contact = get_user_contact(target["id"] if isinstance(target, dict) else target.id)

    text = "👤 *اطلاعات کاربر*\n"
    text += "━━━━━━━━━━━━━━━━━━━━\n\n"

    if contact:
        uid, fn, ln, un, started, fs, ls, gc, prem = contact
        text += f"📛 نام: `{fn} {ln or ''}`\n"
        text += f"🔤 یوزرنیم: {'@' + un if un else 'ندارد'}\n"
        text += f"🆔 آیدی: `{uid}`\n"
        text += f"📅 اولین بار: `{_fmt_time(fs)}`\n"
        text += f"🕒 آخرین فعالیت: `{_fmt_time(ls)}`\n"
        text += f"👥 تعداد گروه‌ها: `{gc}`\n"
        text += f"💎 پرمیوم: {'✅' if prem else '❌'}\n"
        text += f"🚀 ربات رو /start کرده: {'✅' if started else '❌'}\n"
    else:
        text += f"🆔 آیدی: `{target["id"] if isinstance(target, dict) else target.id}`\n"
        text += f"📛 نام: `{target.get("first_name", "-") if isinstance(target, dict) else getattr(target, "first_name", "-")}`\n"
        text += f"🔤 یوزرنیم: {("@" + target["username"]) if (isinstance(target, dict) and target.get("username")) else "ندارد"}\n"
        text += "\n⚠️ کاربر توی بانک اطلاعاتی نیست."

    # اطلاعات در همین گروه
    if chat and chat.type in ("group", "supergroup"):
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            c = conn.cursor()
            c.execute("SELECT join_date, message_count FROM members WHERE chat_id=? AND user_id=?", (chat.id, target["id"] if isinstance(target, dict) else target.id))
            r = c.fetchone()
            conn.close()
            if r:
                text += f"\n📍 *در این گروه:*\n"
                text += f"📅 تاریخ ورود: `{r[0]}`\n"
                text += f"💬 تعداد پیام: `{r[1]}`\n"
        except Exception:
            pass

    try:
        await msg.reply_text(text, parse_mode="Markdown")
    except Exception:
        pass

    raise ApplicationHandlerStop


# ============= Export =============

def _export_dir():
    d = os.path.expanduser("~/groupbot/exports")
    os.makedirs(d, exist_ok=True)
    return d


def export_csv(started_only=False):
    rows = get_all_user_contacts(started_only=started_only)
    path = os.path.join(_export_dir(), f"users_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["user_id", "first_name", "last_name", "username", "has_started_bot",
                    "first_seen", "last_seen", "groups_count"])
        w.writerows(rows)
    return path, len(rows)


def export_json(started_only=False):
    rows = get_all_user_contacts(started_only=started_only)
    path = os.path.join(_export_dir(), f"users_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    data = []
    for r in rows:
        data.append({
            "user_id": r[0], "first_name": r[1], "last_name": r[2],
            "username": r[3], "has_started_bot": bool(r[4]),
            "first_seen": r[5], "last_seen": r[6], "groups_count": r[7]
        })
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return path, len(data)


def export_sqlite(started_only=False):
    rows = get_all_user_contacts(started_only=started_only)
    path = os.path.join(_export_dir(), f"users_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.execute("""CREATE TABLE user_contacts (
        user_id INTEGER PRIMARY KEY, first_name TEXT, last_name TEXT, username TEXT,
        has_started_bot INTEGER, first_seen TEXT, last_seen TEXT, groups_count INTEGER)""")
    for r in rows:
        c.execute("INSERT INTO user_contacts VALUES (?, ?, ?, ?, ?, ?, ?, ?)", r)
    conn.commit()
    conn.close()
    return path, len(rows)


# ============= پنل بانک کاربران =============

def build_contacts_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 آمار کلی", callback_data="uc_stats")],
        [InlineKeyboardButton("📥 Export CSV", callback_data="uc_exp_csv")],
        [InlineKeyboardButton("📥 Export JSON", callback_data="uc_exp_json")],
        [InlineKeyboardButton("📥 Export SQLite", callback_data="uc_exp_db")],
        [InlineKeyboardButton("📥 فقط کاربرانی که /start کردن (CSV)", callback_data="uc_exp_csv_started")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="sys_menu")],
    ])


async def contacts_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    data = query.data

    if user.id != OWNER_ID:
        await query.answer("⛔ فقط سازنده!", show_alert=True)
        return

    if data == "uc_menu":
        try:
            await query.edit_message_text(
                "👥 *بانک اطلاعاتی کاربران*\n\nخروجی‌ها به پیوی ارسال می‌شه:",
                reply_markup=build_contacts_menu(),
                parse_mode="Markdown"
            )
        except Exception:
            pass
        await query.answer()
        return

    if data == "uc_stats":
        s = get_contacts_stats()
        text = (f"📊 *آمار بانک کاربران*\n\n"
                f"👥 کل: `{s['total']}`\n"
                f"🚀 ربات رو /start کردن: `{s['started']}`\n"
                f"👤 توی گروه‌ها: `{s['in_groups']}`\n"
                f"💎 پرمیوم: `{s['premium']}`")
        kb = [[InlineKeyboardButton("🔙 بازگشت", callback_data="uc_menu")]]
        try:
            await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
        except Exception:
            pass
        await query.answer()
        return

    if data.startswith("uc_exp_"):
        await query.answer("📥 در حال ساخت فایل...")
        started = data == "uc_exp_csv_started"
        try:
            if data in ("uc_exp_csv", "uc_exp_csv_started"):
                path, cnt = export_csv(started_only=started)
                caption = f"📥 CSV - {cnt} کاربر"
            elif data == "uc_exp_json":
                path, cnt = export_json()
                caption = f"📥 JSON - {cnt} کاربر"
            elif data == "uc_exp_db":
                path, cnt = export_sqlite()
                caption = f"📥 SQLite - {cnt} کاربر"
            else:
                return

            with open(path, "rb") as f:
                await context.bot.send_document(
                    chat_id=OWNER_ID, document=f,
                    filename=os.path.basename(path), caption=caption
                )
            try:
                await query.edit_message_text(
                    f"✅ {caption}\n\n📤 فایل به پیوی ارسال شد.",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔙 بازگشت", callback_data="uc_menu")]
                    ])
                )
            except Exception:
                pass
        except Exception as e:
            print("[UC EXP ERR]", str(e))
            await query.answer(f"❌ خطا: {e}", show_alert=True)
        return

    await query.answer()


# ============= register =============

def register(app):
    # ثبت کاربر توی پیوی
    app.add_handler(CommandHandler("start", track_user_pv), group=-30)
    # ثبت کاربر توی گروه
    app.add_handler(MessageHandler(filters.ALL & filters.ChatType.GROUPS, track_user_group), group=30)
    # عضو جدید
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, track_new_member), group=30)
    # خروج از گروه
    app.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, track_left_member), group=30)
    # /userinfo
    app.add_handler(CommandHandler("userinfo", userinfo_cmd), group=-2)
    # پنل بانک کاربران
    app.add_handler(CallbackQueryHandler(contacts_cb, pattern=r"^uc_"), group=-40)
    print("OK module user_contacts loaded")
