from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler
from database import (
    get_force_joins, add_force_join, remove_force_join,
    get_payment_settings, set_payment_setting, is_force_enabled
)

NL = chr(10)

# وضعیت انتظار برای ورودی: {chat_id: {"type": "channel/group/amount/card/gateway", "uid": id}}
PENDING_FORCE = {}
PENDING_GATEWAY = {}  # {chat_id: {"name": ..., "api_key": ..., "merchant_id": ...}}


def forces_menu_kb(uid, chat_id):
    joins = get_force_joins(chat_id)
    channels = [j for j in joins if j[1] == "channel"]
    groups = [j for j in joins if j[1] == "group"]
    pay = get_payment_settings(chat_id)
    pay_status = "✅" if (pay and pay[0]) else "❌"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 اجبار به عضویت (" + str(len(channels)) + " کانال، " + str(len(groups)) + " گروه)", callback_data="forces_join_menu:" + str(uid) + ":" + str(chat_id))],
        [InlineKeyboardButton("💰 اجبار به پرداخت " + pay_status, callback_data="forces_pay_menu:" + str(uid) + ":" + str(chat_id))],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="menu_settings:" + str(uid) + ":" + str(chat_id))],
    ])


def forces_join_kb(uid, chat_id):
    joins = get_force_joins(chat_id)
    channels = [j for j in joins if j[1] == "channel"]
    groups = [j for j in joins if j[1] == "group"]
    status = "✅" if len(joins) > 0 else "❌"
    kb = [
        [InlineKeyboardButton("وضعیت: " + status + " (" + str(len(joins)) + " مورد)", callback_data="forces_noop")],
        [InlineKeyboardButton("➕ افزودن کانال", callback_data="forces_add_channel:" + str(uid) + ":" + str(chat_id))],
        [InlineKeyboardButton("➕ افزودن گروه", callback_data="forces_add_group:" + str(uid) + ":" + str(chat_id))],
        [InlineKeyboardButton("📋 لیست و مدیریت", callback_data="forces_list:" + str(uid) + ":" + str(chat_id))],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="forces_menu:" + str(uid) + ":" + str(chat_id))],
    ]
    return InlineKeyboardMarkup(kb)


def forces_pay_kb(uid, chat_id):
    pay = get_payment_settings(chat_id)
    if not pay:
        status = "❌"
        amount = "تنظیم نشده"
        method = "—"
        card = "—"
        gateway = "—"
    else:
        status = "✅" if pay[0] else "❌"
        amount = (pay[1] or "تنظیم نشده") + " تومان" if pay[1] else "تنظیم نشده"
        method = pay[2] or "—"
        card = pay[3] or "—"
        gateway = pay[5] or "—"
    kb = [
        [InlineKeyboardButton("وضعیت: " + status, callback_data="forces_pay_toggle:" + str(uid) + ":" + str(chat_id))],
        [InlineKeyboardButton("💵 مبلغ: " + amount, callback_data="forces_set_amount:" + str(uid) + ":" + str(chat_id))],
        [InlineKeyboardButton("💳 شماره کارت: " + card, callback_data="forces_set_card:" + str(uid) + ":" + str(chat_id))],
        [InlineKeyboardButton("🏦 درگاه بانکی: " + gateway, callback_data="forces_set_gateway:" + str(uid) + ":" + str(chat_id))],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="forces_menu:" + str(uid) + ":" + str(chat_id))],
    ]
    return InlineKeyboardMarkup(kb)




def gateway_edit_kb(uid, chat_id):
    """منوی ویرایش درگاه بانکی"""
    data = PENDING_GATEWAY.get(chat_id, {})
    name = data.get("name", "تنظیم نشده")
    api_key = data.get("api_key", "تنظیم نشده")
    merchant = data.get("merchant_id", "تنظیم نشده")
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🏦 نام درگاه: " + name, callback_data="forces_gw_name:" + str(uid) + ":" + str(chat_id))],
        [InlineKeyboardButton("🔑 API Key: " + api_key, callback_data="forces_gw_api:" + str(uid) + ":" + str(chat_id))],
        [InlineKeyboardButton("🆔 Merchant ID: " + merchant, callback_data="forces_gw_mer:" + str(uid) + ":" + str(chat_id))],
        [InlineKeyboardButton("✅ تایید و ذخیره", callback_data="forces_gw_save:" + str(uid) + ":" + str(chat_id))],
        [InlineKeyboardButton("🔙 انصراف", callback_data="forces_pay_menu:" + str(uid) + ":" + str(chat_id))],
    ])


async def handler(update, context):
    query = update.callback_query
    data = query.data
    user = query.from_user
    parts = data.split(":")
    action = parts[0]
    uid = int(parts[1]) if len(parts) > 1 else user.id
    chat_id = int(parts[2]) if len(parts) > 2 else 0
    if user.id != uid:
        await query.answer("این پنل توسط شما باز نشده!", show_alert=True)
        return

    # ========== منوی اصلی اجبارها ==========
    if action == "forces_menu":
        await query.answer()
        text = (
            "🔥 اجبارها" + NL + "━━━━━━━━━━━━━━━━" + NL + NL +
            "در این بخش می‌تونید برای ورود اعضای جدید به گروه، شرایط تعیین کنید:" + NL + NL +
            "📢 اجبار به عضویت: کاربر باید اول در کانال/گروه‌های شما عضو بشه." + NL +
            "💰 اجبار به پرداخت: کاربر باید مبلغ مشخصی پرداخت کنه." + NL
        )
        await query.edit_message_text(text, reply_markup=forces_menu_kb(uid, chat_id))
        return

    if action == "forces_noop":
        await query.answer()
        return

    # ========== اجبار به عضویت ==========
    if action == "forces_join_menu":
        await query.answer()
        joins = get_force_joins(chat_id)
        channels = [j for j in joins if j[1] == "channel"]
        groups = [j for j in joins if j[1] == "group"]
        text = (
            "📢 اجبار به عضویت" + NL + "━━━━━━━━━━━━━━━━" + NL + NL +
            "📌 کانال‌های اجباری: " + str(len(channels)) + NL +
            "📌 گروه‌های اجباری: " + str(len(groups)) + NL + NL +
            "برای افزودن، از دکمه‌های زیر استفاده کنید:" + NL +
            "• افزودن کانال: ربات باید ادمین کانال باشه" + NL +
            "• افزودن گروه: ربات باید ادمین گروه باشه" + NL + NL +
            "📌 لینک کانال و گروه باید عمومی (با @) یا لینک دعوت باشه."
        )
        await query.edit_message_text(text, reply_markup=forces_join_kb(uid, chat_id))
        return

    if action == "forces_add_channel":
        PENDING_FORCE[chat_id] = {"type": "channel", "uid": uid}
        await query.answer()
        await query.edit_message_text(
            "➕ افزودن کانال اجباری" + NL + NL +
            "لطفاً یوزرنیم یا لینک کانال رو بفرست." + NL +
            "مثال: `@my_channel` یا `https://t.me/my_channel`" + NL + NL +
            "⚠️ ربات باید ادمین اون کانال باشه.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 انصراف", callback_data="forces_join_menu:" + str(uid) + ":" + str(chat_id))],
            ]),
            parse_mode="Markdown"
        )
        return

    if action == "forces_add_group":
        PENDING_FORCE[chat_id] = {"type": "group", "uid": uid}
        await query.answer()
        await query.edit_message_text(
            "➕ افزودن گروه اجباری" + NL + NL +
            "لطفاً یوزرنیم یا لینک گروه رو بفرست." + NL +
            "مثال: `@my_group` یا `https://t.me/my_group`" + NL + NL +
            "⚠️ ربات باید ادمین اون گروه باشه.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 انصراف", callback_data="forces_join_menu:" + str(uid) + ":" + str(chat_id))],
            ]),
            parse_mode="Markdown"
        )
        return

    if action == "forces_list":
        await query.answer()
        joins = get_force_joins(chat_id)
        if not joins:
            await query.edit_message_text(
                "📋 لیست خالیه.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 بازگشت", callback_data="forces_join_menu:" + str(uid) + ":" + str(chat_id))],
                ])
            )
            return
        kb = []
        for j in joins:
            fid, ftype, tid, tlink, tname = j
            icon = "📢" if ftype == "channel" else "👥"
            kb.append([InlineKeyboardButton(icon + " " + (tname or tlink) + " ❌ حذف", callback_data="forces_del_" + str(fid) + ":" + str(uid) + ":" + str(chat_id))])
        kb.append([InlineKeyboardButton("🔙 بازگشت", callback_data="forces_join_menu:" + str(uid) + ":" + str(chat_id))])
        await query.edit_message_text("📋 لیست اجبارها (برای حذف کلیک کنید):", reply_markup=InlineKeyboardMarkup(kb))
        return

    if action.startswith("forces_del_"):
        fid = int(action.replace("forces_del_", ""))
        try:
            remove_force_join(fid)
            await query.answer("✅ حذف شد")
        except Exception as e:
            await query.answer("خطا: " + str(e)[:100])
        joins = get_force_joins(chat_id)
        kb = []
        for j in joins:
            fid2, ftype, tid, tlink, tname = j
            icon = "📢" if ftype == "channel" else "👥"
            kb.append([InlineKeyboardButton(icon + " " + (tname or tlink) + " ❌ حذف", callback_data="forces_del_" + str(fid2) + ":" + str(uid) + ":" + str(chat_id))])
        kb.append([InlineKeyboardButton("🔙 بازگشت", callback_data="forces_join_menu:" + str(uid) + ":" + str(chat_id))])
        await query.edit_message_text("📋 لیست اجبارها:", reply_markup=InlineKeyboardMarkup(kb))
        return

    # ========== اجبار به پرداخت ==========
    if action == "forces_pay_menu":
        await query.answer()
        pay = get_payment_settings(chat_id)
        text = (
            "💰 اجبار به پرداخت" + NL + "━━━━━━━━━━━━━━━━" + NL + NL
        )
        if pay:
            text += "وضعیت: " + ("✅ فعال" if pay[0] else "❌ غیرفعال") + NL
            text += "مبلغ: " + ((pay[1] or "تنظیم نشده") + " تومان" if pay[1] else "تنظیم نشده") + NL
            text += "روش پرداخت: " + (pay[2] or "—") + NL + NL
        text += "روش‌های پرداخت موجود:" + NL
        text += "• 💳 شماره کارت (کاربر رسید می‌فرسته)" + NL
        text += "• 🏦 درگاه بانکی (API خودتون رو وارد کنید)" + NL
        await query.edit_message_text(text, reply_markup=forces_pay_kb(uid, chat_id))
        return

    if action == "forces_pay_toggle":
        pay = get_payment_settings(chat_id)
        cur = pay[0] if pay else 0
        new_val = 0 if cur else 1
        set_payment_setting(chat_id, "enabled", new_val)
        await query.answer("✅ تغییر کرد")
        await query.edit_message_text("💰 اجبار به پرداخت", reply_markup=forces_pay_kb(uid, chat_id))
        return

    if action == "forces_set_amount":
        PENDING_FORCE[chat_id] = {"type": "amount", "uid": uid}
        await query.answer()
        await query.edit_message_text(
            "💵 مبلغ رو به تومان بنویس (فقط عدد):" + NL + "مثال: `50000`",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 انصراف", callback_data="forces_pay_menu:" + str(uid) + ":" + str(chat_id))],
            ]),
            parse_mode="Markdown"
        )
        return

    if action == "forces_set_card":
        PENDING_FORCE[chat_id] = {"type": "card", "uid": uid}
        await query.answer()
        await query.edit_message_text(
            "💳 شماره کارت رو به این شکل بفرست:" + NL + "`شماره کارت - نام صاحب کارت`" + NL + NL +
            "مثال: `6037-9977-1234-5678 - علی رضایی`",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 انصراف", callback_data="forces_pay_menu:" + str(uid) + ":" + str(chat_id))],
            ]),
            parse_mode="Markdown"
        )
        return

    if action == "forces_set_gateway":
        await query.answer()
        # بارگذاری اطلاعات فعلی از دیتابیس
        pay = get_payment_settings(chat_id)
        if pay:
            PENDING_GATEWAY[chat_id] = {
                "name": pay[5] or "تنظیم نشده",
                "api_key": pay[6] or "تنظیم نشده",
                "merchant_id": pay[7] or "تنظیم نشده"
            }
        else:
            PENDING_GATEWAY[chat_id] = {
                "name": "تنظیم نشده",
                "api_key": "تنظیم نشده",
                "merchant_id": "تنظیم نشده"
            }
        text = (
            "🏦 تنظیم درگاه بانکی" + NL + "━━━━━━━━━━━━━━━━" + NL + NL +
            "لطفاً هر فیلد رو جدا تنظیم کن و در آخر روی «✅ تایید و ذخیره» بزن." + NL + NL +
            "⚠️ مسئولیت استفاده از درگاه، پای خودتونه."
        )
        await query.edit_message_text(text, reply_markup=gateway_edit_kb(uid, chat_id))
        return

    if action == "forces_gw_name":
        PENDING_FORCE[chat_id] = {"type": "gw_name", "uid": uid}
        await query.answer()
        await query.edit_message_text(
            "🏦 نام درگاه رو بنویس:" + NL + "مثال: `zarinpal` یا `idpay`",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 بازگشت", callback_data="forces_set_gateway:" + str(uid) + ":" + str(chat_id))],
            ]),
            parse_mode="Markdown"
        )
        return

    if action == "forces_gw_api":
        PENDING_FORCE[chat_id] = {"type": "gw_api", "uid": uid}
        await query.answer()
        await query.edit_message_text(
            "🔑 API Key رو بنویس:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 بازگشت", callback_data="forces_set_gateway:" + str(uid) + ":" + str(chat_id))],
            ])
        )
        return

    if action == "forces_gw_mer":
        PENDING_FORCE[chat_id] = {"type": "gw_mer", "uid": uid}
        await query.answer()
        await query.edit_message_text(
            "🆔 Merchant ID رو بنویس:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 بازگشت", callback_data="forces_set_gateway:" + str(uid) + ":" + str(chat_id))],
            ])
        )
        return

    if action == "forces_gw_save":
        data = PENDING_GATEWAY.get(chat_id, {})
        if data.get("name") == "تنظیم نشده" or data.get("api_key") == "تنظیم نشده":
            await query.answer("❌ همه فیلدها رو پر کن!", show_alert=True)
            return
        set_payment_setting(chat_id, "gateway_name", data.get("name", ""))
        set_payment_setting(chat_id, "gateway_api_key", data.get("api_key", ""))
        set_payment_setting(chat_id, "gateway_merchant_id", data.get("merchant_id", ""))
        set_payment_setting(chat_id, "payment_method", "gateway")
        PENDING_GATEWAY.pop(chat_id, None)
        await query.answer("✅ درگاه ذخیره شد")
        await query.edit_message_text("💰 منوی پرداخت:", reply_markup=forces_pay_kb(uid, chat_id))
        return


async def force_input_handler(update, context):
    """گرفتن ورودی از مالک برای تنظیم اجبارها"""
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    if not msg or not chat or not user:
        return
    if chat.type != "private":
        return
    if not msg.text:
        return
    # چک کن توی حالت انتظار هستیم
    pending = None
    for cid, info in list(PENDING_FORCE.items()):
        if info.get("uid") == user.id:
            pending = (cid, info)
            break
    if not pending:
        return
    cid, info = pending
    ftype = info.get("type")
    text = msg.text.strip()

    if ftype == "channel" or ftype == "group":
        # استخراج یوزرنیم از متن
        username = text
        if "t.me/" in text:
            username = "@" + text.split("t.me/")[-1].split("/")[0].strip()
        elif not text.startswith("@"):
            await msg.reply_text("❌ لطفاً با @ شروع کن یا لینک t.me بفرست.")
            return
        try:
            chat_obj = await context.bot.get_chat(username)
            target_id = chat_obj.id
            target_name = chat_obj.title or username
            # چک ادمین بودن ربات
            try:
                bot_member = await context.bot.get_chat_member(target_id, context.bot.id)
                if bot_member.status not in ("administrator", "creator"):
                    await msg.reply_text("❌ ربات توی " + target_name + " ادمین نیست. لطفاً اول ربات رو ادمین کن.")
                    return
            except Exception as e:
                await msg.reply_text("❌ نمی‌تونم وضعیت ربات رو چک کنم. مطمئن شو ربات ادمین هست.\nخطا: " + str(e)[:200])
                return
            add_force_join(cid, ftype, target_id, username, target_name)
            PENDING_FORCE.pop(cid, None)
            await msg.reply_text("✅ " + target_name + " به لیست اجبارهای اضافه شد.")
            # ارسال منو
            try:
                await msg.reply_text("📋 برای دیدن لیست:", reply_markup=forces_join_kb(user.id, cid))
            except Exception:
                pass
        except Exception as e:
            await msg.reply_text("❌ خطا: " + str(e)[:200])
        return

    if ftype == "amount":
        try:
            amount = int(text.replace(",", "").strip())
            set_payment_setting(cid, "amount", str(amount))
            PENDING_FORCE.pop(cid, None)
            await msg.reply_text("✅ مبلغ تنظیم شد: " + str(amount) + " تومان")
            await msg.reply_text("💰 منوی پرداخت:", reply_markup=forces_pay_kb(user.id, cid))
        except Exception:
            await msg.reply_text("❌ لطفاً فقط عدد بفرست.")
        return

    if ftype == "card":
        if "-" not in text:
            await msg.reply_text("❌ فرمت درست: `شماره کارت - نام صاحب کارت`", parse_mode="Markdown")
            return
        parts2 = text.split("-", 1)
        card_num = parts2[0].strip()
        holder = parts2[1].strip()
        set_payment_setting(cid, "card_number", card_num)
        set_payment_setting(cid, "card_holder", holder)
        set_payment_setting(cid, "payment_method", "card")
        PENDING_FORCE.pop(cid, None)
        await msg.reply_text("✅ شماره کارت تنظیم شد.")
        await msg.reply_text("💰 منوی پرداخت:", reply_markup=forces_pay_kb(user.id, cid))
        return

    if ftype == "gw_name":
        if cid not in PENDING_GATEWAY:
            PENDING_GATEWAY[cid] = {}
        PENDING_GATEWAY[cid]["name"] = text
        PENDING_FORCE.pop(cid, None)
        await msg.reply_text("✅ نام درگاه: " + text)
        await msg.reply_text("🏦 تنظیم درگاه:", reply_markup=gateway_edit_kb(user.id, cid))
        return

    if ftype == "gw_api":
        if cid not in PENDING_GATEWAY:
            PENDING_GATEWAY[cid] = {}
        PENDING_GATEWAY[cid]["api_key"] = text
        PENDING_FORCE.pop(cid, None)
        await msg.reply_text("✅ API Key ذخیره شد.")
        await msg.reply_text("🏦 تنظیم درگاه:", reply_markup=gateway_edit_kb(user.id, cid))
        return

    if ftype == "gw_mer":
        if cid not in PENDING_GATEWAY:
            PENDING_GATEWAY[cid] = {}
        PENDING_GATEWAY[cid]["merchant_id"] = text
        PENDING_FORCE.pop(cid, None)
        await msg.reply_text("✅ Merchant ID ذخیره شد.")
        await msg.reply_text("🏦 تنظیم درگاه:", reply_markup=gateway_edit_kb(user.id, cid))
        return


def register(app):
    from telegram.ext import MessageHandler, filters
    app.add_handler(CallbackQueryHandler(handler, pattern="^(forces_)"), group=5)
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, force_input_handler), group=4)
