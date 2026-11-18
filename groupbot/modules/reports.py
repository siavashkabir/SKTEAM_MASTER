"""گزارش مخفی پیام‌ها"""
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions
from telegram.ext import ContextTypes, MessageHandler, CallbackQueryHandler, filters, ApplicationHandlerStop
from config import OWNER_ID
from database import (
    is_group_owner, add_report, get_pending_reports,
    count_pending_reports, update_report_status, count_user_reports_today,
    get_report_settings
)

_REPORT_COOLDOWN = {}


def _is_report_trigger(text):
    if not text:
        return False
    return text.strip().lower() in ("report", "گزارش", "/report", "/گزارش")


async def _auto_del(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    try:
        await context.bot.delete_message(chat_id=job.chat_id, message_id=job.data)
    except Exception:
        pass


async def handle_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    if not msg or not chat or not user:
        return
    if chat.type not in ("group", "supergroup"):
        return
    if not msg.text or not _is_report_trigger(msg.text):
        return
    
    if not msg.reply_to_message:
        try:
            w = await msg.reply_text("⚠️ برای گزارش، روی پیام مورد نظر ریپلای کنید و بنویسید report")
            context.job_queue.run_once(_auto_del, 5, chat_id=chat.id, data=w.message_id,
                                        name=f"rw_{w.message_id}")
        except Exception:
            pass
        raise ApplicationHandlerStop
    
    try:
        await msg.delete()
    except Exception:
        pass
    
    key = (user.id, chat.id)
    now = time.time()
    last = _REPORT_COOLDOWN.get(key, 0)
    
    try:
        _dl, _cd = get_report_settings(chat.id)
    except Exception:
        _dl, _cd = 3, 300
    
    if now - last < _cd:
        try:
            w = await context.bot.send_message(
                chat_id=user.id,
                text=f"⏳ لطفاً {int(_cd - (now - last))} ثانیه دیگر صبر کنید."
            )
            context.job_queue.run_once(_auto_del, 5, chat_id=user.id, data=w.message_id,
                                        name=f"rcd_{w.message_id}")
        except Exception:
            pass
        raise ApplicationHandlerStop
    
    today_count = count_user_reports_today(user.id, chat.id)
    if today_count >= _dl:
        try:
            w = await context.bot.send_message(
                chat_id=user.id,
                text=f"⛔ سهمیه گزارش روزانه شما ({_dl} مورد) تمام شده است."
            )
            context.job_queue.run_once(_auto_del, 8, chat_id=user.id, data=w.message_id,
                                        name=f"rlim_{w.message_id}")
        except Exception:
            pass
        raise ApplicationHandlerStop
    
    rmsg = msg.reply_to_message
    ruser = rmsg.from_user
    rtext = rmsg.text or rmsg.caption or "[بدون متن]"
    
    if ruser and ruser.id == user.id:
        try:
            w = await context.bot.send_message(chat_id=user.id, text="⚠️ نمی‌توانید پیام خودتان را گزارش کنید.")
            context.job_queue.run_once(_auto_del, 5, chat_id=user.id, data=w.message_id,
                                        name=f"rself_{w.message_id}")
        except Exception:
            pass
        raise ApplicationHandlerStop
    
    rid = add_report(chat.id, chat.title or str(chat.id),
                     user.id, user.full_name or "-", user.username or "-",
                     ruser.id if ruser else 0,
                     ruser.full_name if ruser else "-",
                     ruser.username if ruser else "-",
                     rmsg.message_id, rtext[:500])
    
    _REPORT_COOLDOWN[key] = now
    if not rid:
        raise ApplicationHandlerStop
    
    try:
        conn = sqlite3.connect('data/groupbot.db')
        c = conn.cursor()
        c.execute("SELECT user_id FROM group_owners WHERE chat_id=?", (chat.id,))
        owners = [r[0] for r in c.fetchall()]
        conn.close()
    except Exception:
        owners = []
    
    pending = count_pending_reports(chat.id)
    for oid in owners:
        try:
            kb = InlineKeyboardMarkup([[
                InlineKeyboardButton(f"📬 مشاهده گزارش‌ها ({pending})",
                                     callback_data=f"rep_view:{chat.id}:0")
            ]])
            await context.bot.send_message(
                chat_id=oid,
                text=f"🔔 گزارش جدید در گروه «{chat.title}»\n\n📊 تعداد: {pending}",
                reply_markup=kb,
                disable_notification=True
            )
        except Exception as e:
            print(f"[NOTIFY ERR] {e}")
    
    print(f"[REPORT] id={rid} group={chat.id} by={user.id}")
    raise ApplicationHandlerStop


async def _build_view(gid, offset):
    reports = get_pending_reports(gid, limit=100)
    if not reports:
        return None, None
    if offset >= len(reports):
        offset = len(reports) - 1
    if offset < 0:
        offset = 0
    r = reports[offset]
    (rid, _, gtitle, rep_id, rep_name, rep_user, ru_id, ru_name, ru_user, rmsg_id, rtext, created) = r
    total = len(reports)
    text = (
        f"🚨 گزارش #{rid}  ({offset+1} از {total})\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🏠 گروه: {gtitle}\n"
        f"📅 تاریخ: {created}\n\n"
        f"👮 گزارش‌دهنده:\n"
        f"   نام: {rep_name}\n"
        f"   یوزرنیم: @{rep_user}\n"
        f"   آیدی: {rep_id}\n\n"
        f"👤 فرستنده پیام:\n"
        f"   نام: {ru_name}\n"
        f"   یوزرنیم: @{ru_user}\n"
        f"   آیدی: {ru_id}\n\n"
        f"📝 متن پیام:\n{rtext}"
    )
    nav = []
    if offset > 0:
        nav.append(InlineKeyboardButton("⬅️ قبلی", callback_data=f"rep_view:{gid}:{offset-1}"))
    if offset < total - 1:
        nav.append(InlineKeyboardButton("➡️ بعدی", callback_data=f"rep_view:{gid}:{offset+1}"))
    rows = [
        [InlineKeyboardButton("🗑 حذف پیام", callback_data=f"rep_del:{gid}:{rid}:{rmsg_id}:{offset}"),
         InlineKeyboardButton("🚫 سکوت 1ساعت", callback_data=f"rep_mute:{gid}:{rid}:{ru_id}:{offset}")],
        [InlineKeyboardButton("🔨 بن", callback_data=f"rep_ban:{gid}:{rid}:{ru_id}:{offset}")],
        [InlineKeyboardButton("✅ رسیدگی", callback_data=f"rep_done:{gid}:{rid}:{offset}"),
         InlineKeyboardButton("❌ نادیده", callback_data=f"rep_ign:{gid}:{rid}:{offset}")],
    ]
    if nav:
        rows.append(nav)
    rows.append([InlineKeyboardButton("🔙 بستن", callback_data=f"rep_close:{gid}:0")])
    return text, InlineKeyboardMarkup(rows)


async def handle_report_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    data = query.data
    parts = data.split(":")
    action = parts[0]
    await query.answer()
    
    if action == "rep_close":
        try:
            await query.edit_message_text("📪 بسته شد.")
        except Exception:
            pass
        return
    
    if action == "rep_view":
        gid = int(parts[1])
        offset = int(parts[2])
        if not is_group_owner(gid, user.id) and user.id != OWNER_ID:
            await query.answer("⛔ فقط مالک گروه.", show_alert=True)
            return
        text, kb = await _build_view(gid, offset)
        if not text:
            try:
                await query.edit_message_text("✅ گزارش رسیدگی‌نشده‌ای نیست.")
            except Exception:
                pass
            return
        try:
            await query.edit_message_text(text, reply_markup=kb)
        except Exception:
            pass
        return
    
    if len(parts) < 4:
        return
    gid = int(parts[1])
    rid = int(parts[2])
    if not is_group_owner(gid, user.id) and user.id != OWNER_ID:
        await query.answer("⛔ فقط مالک گروه.", show_alert=True)
        return
    
    offset = 0
    
    if action == "rep_del":
        msg_id = int(parts[3])
        offset = int(parts[4]) if len(parts) > 4 else 0
        try:
            await context.bot.delete_message(chat_id=gid, message_id=msg_id)
            await query.answer("✅ حذف شد.", show_alert=True)
        except Exception as e:
            await query.answer(f"⚠️ {str(e)[:50]}", show_alert=True)
    elif action == "rep_mute":
        uid = int(parts[3])
        offset = int(parts[4]) if len(parts) > 4 else 0
        import datetime as _dt
        try:
            await context.bot.restrict_chat_member(
                chat_id=gid, user_id=uid,
                permissions=ChatPermissions(can_send_messages=False),
                until_date=_dt.datetime.now() + _dt.timedelta(hours=1)
            )
            await query.answer("✅ 1ساعت سکوت شد.", show_alert=True)
        except Exception as e:
            await query.answer(f"⚠️ {str(e)[:50]}", show_alert=True)
    elif action == "rep_ban":
        uid = int(parts[3])
        offset = int(parts[4]) if len(parts) > 4 else 0
        try:
            await context.bot.ban_chat_member(chat_id=gid, user_id=uid)
            await query.answer("✅ بن شد.", show_alert=True)
        except Exception as e:
            await query.answer(f"⚠️ {str(e)[:50]}", show_alert=True)
    elif action == "rep_done":
        offset = int(parts[3]) if len(parts) > 3 else 0
        await query.answer("✅ رسیدگی شد.")
    elif action == "rep_ign":
        offset = int(parts[3]) if len(parts) > 3 else 0
        await query.answer("❌ نادیده گرفته شد.")
    
    update_report_status(rid, 'resolved' if action != "rep_ign" else 'ignored')
    text, kb = await _build_view(gid, offset)
    if text:
        try:
            await query.edit_message_text(text, reply_markup=kb)
        except Exception:
            pass
    else:
        try:
            await query.edit_message_text("✅ همه گزارش‌ها رسیدگی شدند.")
        except Exception:
            pass


def register(app):
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_report, block=False),
        group=-45
    )
    app.add_handler(
        CallbackQueryHandler(handle_report_callback, pattern=r"^rep_"),
        group=-44
    )
    print("OK module reports loaded")
