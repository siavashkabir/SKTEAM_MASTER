from telegram import Update, ChatPermissions, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ChatMemberHandler, MessageHandler, CallbackQueryHandler, filters
from database import (
    get_force_joins, is_force_enabled, is_user_verified, set_user_verified,
    get_payment_settings, is_group_owner, is_bot_admin
)
from config import OWNER_ID

NL = chr(10)
PENDING_RECEIPTS = {}


async def on_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = update.chat_member
    if not result:
        return
    chat = result.chat
    user = result.new_chat_member.user
    new_status = result.new_chat_member.status
    old_status = result.old_chat_member.status
    if new_status not in ("member", "restricted"):
        return
    if old_status in ("member", "administrator", "creator"):
        return
    if user.is_bot:
        return
    try:
        if user.id == OWNER_ID or is_bot_admin(user.id) or is_group_owner(chat.id, user.id):
            return
    except Exception:
        pass
    joins = get_force_joins(chat.id)
    pay = get_payment_settings(chat.id)
    force_join_on = len(joins) > 0
    force_pay_on = bool(pay and pay[0])
    if not force_join_on and not force_pay_on:
        return
    if is_user_verified(chat.id, user.id):
        return
    try:
        await context.bot.restrict_chat_member(chat.id, user.id, ChatPermissions(can_send_messages=False))
    except Exception as e:
        print("[FORCE MUTE ERR] " + str(e))
    text = "🔒 سلام " + (user.first_name or "دوست") + " عزیز!" + NL + NL
    text += "برای ارسال پیام در گروه " + (chat.title or "") + "، باید شرایط زیر رو انجام بدی:" + NL + NL
    kb = []
    if force_join_on:
        text += "📢 عضویت در کانال/گروه‌های زیر:" + NL
        for j in joins:
            fid, ftype, tid, tlink, tname = j
            icon = "📢" if ftype == "channel" else "👥"
            text += "• " + icon + " " + (tname or tlink) + NL
            link = tlink if tlink.startswith("http") else ("https://t.me/" + tlink.replace("@", ""))
            kb.append([InlineKeyboardButton(icon + " " + (tname or tlink), url=link)])
        text += NL
    if force_pay_on:
        amount = pay[1] or "?"
        card = pay[3] or "?"
        holder = pay[4] or "?"
        text += "💰 پرداخت مبلغ " + amount + " تومان" + NL
        text += "💳 شماره کارت: `" + card + "`" + NL
        text += "👤 به نام: " + holder + NL + NL
        text += "بعد از پرداخت، رسید رو همین‌جا بفرست." + NL + NL
    if force_join_on:
        kb.append([InlineKeyboardButton("✅ عضو شدم، بررسی کن", callback_data="force_verify:" + str(user.id) + ":" + str(chat.id))])
    if force_pay_on:
        kb.append([InlineKeyboardButton("📤 ارسال رسید", callback_data="force_receipt:" + str(user.id) + ":" + str(chat.id))])
    try:
        await context.bot.send_message(chat_id=user.id, text=text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
    except Exception as e:
        print("[FORCE MSG ERR] " + str(e))


async def verify_join_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    user = query.from_user
    parts = data.split(":")
    action = parts[0]
    target_id = int(parts[1]) if len(parts) > 1 else user.id
    chat_id = int(parts[2]) if len(parts) > 2 else 0
    if user.id != target_id:
        await query.answer("این دکمه برای شما نیست!", show_alert=True)
        return
    await query.answer()
    if action == "force_verify":
        joins = get_force_joins(chat_id)
        if not joins:
            await query.answer("✅ تأیید شد")
            return
        missing = []
        for j in joins:
            fid, ftype, tid, tlink, tname = j
            try:
                m = await context.bot.get_chat_member(tid, user.id)
                if m.status in ("left", "kicked"):
                    missing.append(tname or tlink)
            except Exception as e:
                print("[FORCE CHK ERR] " + str(e))
                missing.append(tname or tlink)
        if missing:
            text = "❌ هنوز در موارد زیر عضو نشدی:" + NL + NL
            for m in missing:
                text += "• " + m + NL
            try:
                await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("✅ بررسی مجدد", callback_data="force_verify:" + str(user.id) + ":" + str(chat_id))]
                ]))
            except Exception:
                pass
            return
        pay = get_payment_settings(chat_id)
        if pay and pay[0]:
            set_user_verified(chat_id, user.id, method="join")
            try:
                await query.edit_message_text("✅ عضویت تأیید شد." + NL + NL + "💰 حالا لطفاً مبلغ " + (pay[1] or "?") + " تومان رو پرداخت کن و رسید رو بفرست.")
            except Exception:
                pass
            return
        set_user_verified(chat_id, user.id, method="join")
        try:
            await context.bot.restrict_chat_member(chat_id, user.id, ChatPermissions(
                can_send_messages=True, can_send_audios=True, can_send_documents=True,
                can_send_photos=True, can_send_videos=True, can_send_video_notes=True,
                can_send_voice_notes=True, can_send_polls=True, can_send_other_messages=True,
                can_add_web_page_previews=True, can_invite_users=True
            ))
            await query.edit_message_text("✅ عضویت تأیید شد. حالا می‌تونی پیام بدی.")
        except Exception as e:
            print("[FORCE UNMUTE ERR] " + str(e))
        return
    if action == "force_receipt":
        PENDING_RECEIPTS[user.id] = chat_id
        try:
            await query.edit_message_text("📤 لطفاً عکس رسید پرداخت رو همین‌جا بفرست.")
        except Exception:
            pass
        return


async def receipt_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    if not msg or not chat or not user:
        return
    if chat.type != "private":
        return
    if not msg.photo:
        return
    if user.id not in PENDING_RECEIPTS:
        return
    group_chat_id = PENDING_RECEIPTS.get(user.id)
    PENDING_RECEIPTS.pop(user.id, None)
    file_id = msg.photo[-1].file_id
    try:
        set_user_verified(group_chat_id, user.id, method="payment_pending", receipt_file_id=file_id)
    except Exception as e:
        print("[RECEIPT SAVE ERR] " + str(e))
    await msg.reply_text("✅ رسید دریافت شد." + NL + "در انتظار تأیید مالک گروه باشید.")
    try:
        pay = get_payment_settings(group_chat_id)
        amount = pay[1] if pay else "?"
        import turso_db as sqlite3
        from config import DATABASE_PATH
        conn = sqlite3.connect(DATABASE_PATH)
        cur = conn.cursor()
        cur.execute("SELECT user_id FROM group_owners WHERE chat_id=? LIMIT 1", (group_chat_id,))
        row = cur.fetchone()
        conn.close()
        if row:
            owner_id = row[0]
            text = ("🔔 رسید پرداخت جدید!" + NL + "━━━━━━━━━━━━━━━━" + NL +
                    "👤 کاربر: " + (user.first_name or "?") + NL +
                    "📱 آیدی: " + str(user.id) + NL +
                    "💰 مبلغ: " + str(amount) + " تومان" + NL + NL +
                    "برای تأیید، روی دکمه زیر بزن:")
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ تأیید", callback_data="force_approve:" + str(user.id) + ":" + str(group_chat_id))],
                [InlineKeyboardButton("❌ رد", callback_data="force_reject:" + str(user.id) + ":" + str(group_chat_id))],
            ])
            await context.bot.send_photo(chat_id=owner_id, photo=file_id, caption=text, reply_markup=kb)
    except Exception as e:
        print("[RECEIPT NOTIF ERR] " + str(e))


async def approve_reject_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    parts = data.split(":")
    action = parts[0]
    target_id = int(parts[1]) if len(parts) > 1 else 0
    group_chat_id = int(parts[2]) if len(parts) > 2 else 0
    await query.answer()
    if action == "force_approve":
        try:
            set_user_verified(group_chat_id, target_id, method="payment_approved")
            await context.bot.restrict_chat_member(group_chat_id, target_id, ChatPermissions(
                can_send_messages=True, can_send_audios=True, can_send_documents=True,
                can_send_photos=True, can_send_videos=True, can_send_video_notes=True,
                can_send_voice_notes=True, can_send_polls=True, can_send_other_messages=True,
                can_add_web_page_previews=True, can_invite_users=True
            ))
            await query.edit_message_caption(caption="✅ پرداخت تأیید شد. کاربر آزاد شد.")
            try:
                await context.bot.send_message(chat_id=target_id, text="✅ پرداخت شما تأیید شد. حالا می‌تونی پیام بدی.")
            except Exception:
                pass
        except Exception as e:
            print("[APPROVE ERR] " + str(e))
            await query.answer("خطا: " + str(e)[:100], show_alert=True)
        return
    if action == "force_reject":
        try:
            await query.edit_message_caption(caption="❌ پرداخت رد شد.")
            try:
                await context.bot.send_message(chat_id=target_id, text="❌ متأسفانه رسید شما تأیید نشد. با پشتیبانی تماس بگیرید.")
            except Exception:
                pass
        except Exception as e:
            print("[REJECT ERR] " + str(e))
        return


def register(app):
    app.add_handler(ChatMemberHandler(on_new_member, ChatMemberHandler.CHAT_MEMBER), group=2)
    app.add_handler(CallbackQueryHandler(verify_join_callback, pattern="^(force_verify|force_receipt):"), group=2)
    app.add_handler(CallbackQueryHandler(approve_reject_handler, pattern="^(force_approve|force_reject):"), group=2)
    app.add_handler(MessageHandler(filters.PHOTO & filters.ChatType.PRIVATE, receipt_handler), group=3)
