from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler, ApplicationHandlerStop
from config import OWNER_ID

NL = chr(10)

# قیمت‌ها (تومان)
PRICES = {
    "manager": [("۱ ماهه", "149,000"), ("۳ ماهه", "349,000"), ("۶ ماهه", "599,000"), ("۱ ساله", "999,000")],
    "music":   [("۱ ماهه", "149,000"), ("۳ ماهه", "349,000"), ("۶ ماهه", "599,000"), ("۱ ساله", "999,000")],
    "nsfw":    [("۱ ماهه", "119,000"), ("۳ ماهه", "279,000"), ("۶ ماهه", "479,000"), ("۱ ساله", "799,000")],
    "vcall":   [("۱ ماهه", "89,000"),  ("۳ ماهه", "199,000"), ("۶ ماهه", "349,000"), ("۱ ساله", "599,000")],
}

NAMES = {
    "nsfw": "🔞 اشتراک NSFW",
    "music": "🎵 اشتراک موزیک",
    "vcall": "🎙️ اشتراک ضبط ویس‌کال",
    "manager": "🤖 اشتراک مدیریت گروه",
}

SUPPORT = "@Siavashska"
CARD_NUMBER = "0000-0000-0000-0000"
CARD_HOLDER = "سیاوش"




# ============ PV Auto-Delete System ============
PV_MESSAGES = {}   # {chat_id: [message_ids]}
PV_JOBS = {}       # {chat_id: job}


async def _delete_pv_messages(context):
    chat_id = context.job.data
    msg_ids = PV_MESSAGES.get(chat_id, [])
    for mid in msg_ids:
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=mid)
        except Exception:
            pass
    PV_MESSAGES[chat_id] = []
    PV_JOBS.pop(chat_id, None)


def _schedule_delete(context, chat_id):
    old = PV_JOBS.get(chat_id)
    if old:
        try:
            old.schedule_removal()
        except Exception:
            pass
    try:
        job = context.job_queue.run_once(_delete_pv_messages, 60, data=chat_id)
        PV_JOBS[chat_id] = job
    except Exception as e:
        print("[PV JOB ERR] " + str(e))


def _track_message(chat_id, msg_id):
    if chat_id not in PV_MESSAGES:
        PV_MESSAGES[chat_id] = []
    PV_MESSAGES[chat_id].append(msg_id)


def main_menu_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🛒 مشاهده اشتراک‌ها و قیمت‌ها", callback_data="pv_shop")],
        [InlineKeyboardButton("📖 راهنمای ربات", callback_data="pv_guide")],
        [InlineKeyboardButton("☎️ پشتیبانی", url="https://t.me/" + SUPPORT.replace("@", ""))],
    ])


def shop_menu_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(NAMES["manager"], callback_data="pv_cat_manager")],
        [InlineKeyboardButton(NAMES["nsfw"], callback_data="pv_cat_nsfw")],
        [InlineKeyboardButton(NAMES["music"], callback_data="pv_cat_music")],
        [InlineKeyboardButton(NAMES["vcall"], callback_data="pv_cat_vcall")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="pv_home")],
    ])


def category_kb(cat):
    rows = []
    for label, price in PRICES.get(cat, []):
        rows.append([InlineKeyboardButton(label + " - " + price + " تومان", callback_data="pv_buy_" + cat + "_" + label)])
    rows.append([InlineKeyboardButton("🔙 بازگشت", callback_data="pv_shop")])
    return InlineKeyboardMarkup(rows)


MAIN_TEXT = (
    "🤖 به ربات مدیریت گروه Sk.team خوش آمدید!" + NL +
    "━━━━━━━━━━━━━━━━━━━━" + NL + NL +
    "✨ این ربات با امکانات کامل، مدیریت گروه شما را آسان می‌کند." + NL + NL +
    "💼 امکانات ربات:" + NL +
    "• 🔒 قفل‌های امنیتی پیشرفته" + NL +
    "• 👋 خوش‌آمدگویی خودکار" + NL +
    "• 🔞 فیلتر محتوای بزرگسال (NSFW)" + NL +
    "• 🎵 پخش موزیک در ویس‌کال" + NL +
    "• 🎙️ ضبط خودکار ویس‌کال" + NL +
    "• 👥 مدیریت ادمین‌ها و معاونین" + NL + NL +
    "👇 برای مشاهده اشتراک‌ها و قیمت‌ها، روی دکمه زیر بزنید:"
)


async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    if not msg or not chat or not user:
        return
    if chat.type != "private":
        return
    
    # چک کردن نقش کاربر
    is_sudo = False
    is_group_owner_flag = False
    is_bot_admin_flag = False
    owner_chat_id = 0
    try:
        from database import is_bot_admin, is_group_owner
        from config import OWNER_ID, DATABASE_PATH
        import sqlite3
        if user.id == OWNER_ID:
            is_sudo = True
        elif is_bot_admin(user.id):
            is_bot_admin_flag = True
        # چک کن آیا کاربر مالک یکی از گروه‌هاست
        conn = sqlite3.connect(DATABASE_PATH)
        cur = conn.cursor()
        cur.execute("SELECT chat_id FROM groups")
        all_groups = [r[0] for r in cur.fetchall()]
        conn.close()
        for gid in all_groups:
            try:
                if is_group_owner(gid, user.id):
                    is_group_owner_flag = True
                    owner_chat_id = gid
                    break
            except Exception:
                continue
    except Exception as e:
        print("[PV ROLE CHECK ERR] " + str(e))
    
    # اگه مالک گروه بود، پنل مالک گروه بفرست
    if is_group_owner_flag:
        try:
            from modules.start import sudo_panel_menu, group_owner_panel_menu
            print("[PV] importing group_owner_panel_menu OK")
            print("[PV] importing group_owner_panel_menu OK")
            sent = await msg.reply_text(
                "👑 پنل مالک گروه" + NL + NL + "برای مدیریت گروه، از دکمه‌های زیر استفاده کنید:",
                reply_markup=group_owner_panel_menu(user.id, owner_chat_id)
            )
            _track_message(chat.id, sent.message_id)
            _schedule_delete(context, chat.id)
            return
        except Exception as e:
            import traceback
            print("[PV OWNER PANEL ERR] " + str(e))
            traceback.print_exc()
            sent = await msg.reply_text(
                "⚠️ خطا در باز کردن پنل مالک گروه." + NL + "خطا: " + str(e),
                reply_markup=main_menu_kb()
            )
            return
    
    # اگه سازنده یا ادمین ربات بود، پنل سازنده بفرست
    if is_sudo or is_bot_admin_flag:
        try:
            from modules.start import sudo_panel_menu
            sent = await msg.reply_text(
                "🛡️ پنل مدیریت:" + NL + NL + "برای مدیریت ربات، از دکمه‌های زیر استفاده کنید:",
                reply_markup=sudo_panel_menu(user.id, 0)
            )
            _track_message(chat.id, sent.message_id)
            _schedule_delete(context, chat.id)
            return
        except Exception as e:
            import traceback
            print("[PV SUDO PANEL ERR] " + str(e))
            traceback.print_exc()
            return
    
    # در غیر این صورت، منوی فروشگاه
    sent = await msg.reply_text(MAIN_TEXT, reply_markup=main_menu_kb())
    _track_message(chat.id, sent.message_id)
    _schedule_delete(context, chat.id)
    return


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    user = query.from_user
    if not data.startswith("pv_"):
        return
    await query.answer()
    _schedule_delete(context, query.message.chat_id)
    # ادامه بده و در آخر stop کن

    if data == "pv_home":
        await query.edit_message_text(MAIN_TEXT, reply_markup=main_menu_kb())
        return

    if data == "pv_shop":
        text = (
            "🛒 فروشگاه اشتراک‌ها" + NL +
            "━━━━━━━━━━━━━━━━━━━━" + NL + NL +
            "یکی از اشتراک‌های زیر را انتخاب کنید:" + NL + NL +
            "ℹ️ همه اشتراک‌ها به صورت ۱ ماهه، ۳ ماهه، ۶ ماهه و ۱ ساله موجود هستند."
        )
        await query.edit_message_text(text, reply_markup=shop_menu_kb())
        return

    if data.startswith("pv_cat_"):
        cat = data.replace("pv_cat_", "")
        name = NAMES.get(cat, "اشتراک")
        text = (
            name + NL +
            "━━━━━━━━━━━━━━━━━━━━" + NL + NL +
            "💰 لیست قیمت‌ها:" + NL + NL
        )
        for label, price in PRICES.get(cat, []):
            text += "• " + label + " → " + price + " تومان" + NL
        text += NL + "👇 برای خرید، یکی از گزینه‌های زیر را انتخاب کنید:"
        await query.edit_message_text(text, reply_markup=category_kb(cat))
        return

    if data.startswith("pv_buy_"):
        parts = data.replace("pv_buy_", "").split("_")
        cat = parts[0]
        plan = "_".join(parts[1:])
        name = NAMES.get(cat, "اشتراک")
        # پیدا کردن قیمت
        price = "?"
        for lbl, pr in PRICES.get(cat, []):
            if lbl == plan:
                price = pr
                break
        # پیام به کاربر
        text = (
            "✅ فاکتور شما صادر شد!" + NL +
            "━━━━━━━━━━━━━━━━━━━━" + NL + NL +
            "📦 اشتراک: " + name + NL +
            "⏱️ مدت: " + plan + NL +
            "💰 مبلغ: " + price + " تومان" + NL + NL +
            "💳 شماره کارت:" + NL +
            "`" + CARD_NUMBER + "`" + NL +
            "👤 به نام: " + CARD_HOLDER + NL + NL +
            "📌 لطفاً مبلغ را واریز کنید و رسید را به پشتیبانی ارسال کنید." + NL + NL +
            "☎️ پشتیبانی: " + SUPPORT
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("📩 ارسال رسید به پشتیبانی", url="https://t.me/" + SUPPORT.replace("@", ""))],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="pv_cat_" + cat)],
            [InlineKeyboardButton("🏠 منوی اصلی", callback_data="pv_home")],
        ])
        await query.edit_message_text(text, reply_markup=kb, parse_mode="Markdown")

        # ارسال فاکتور به پیوی سازنده
        username = "@" + user.username if user.username else "(ندارد)"
        full_name = user.full_name or "کاربر"
        invoice_to_owner = (
            "🔔 فاکتور جدید دریافت شد!" + NL +
            "━━━━━━━━━━━━━━━━━━━━" + NL + NL +
            "👤 کاربر: " + full_name + NL +
            "🔗 یوزرنیم: " + username + NL +
            "📱 آیدی عددی: `" + str(user.id) + "`" + NL + NL +
            "📦 اشتراک درخواستی: " + name + NL +
            "⏱️ مدت: " + plan + NL +
            "💰 مبلغ: " + price + " تومان" + NL + NL +
            "📌 منتظر ارسال رسید از طرف کاربر باشید." + NL +
            "💬 برای پاسخ، همین حالا با کاربر در ارتباط باشید."
        )
        try:
            await context.bot.send_message(chat_id=OWNER_ID, text=invoice_to_owner, parse_mode="Markdown")
        except Exception as e:
            print("[INVOICE TO OWNER ERR] " + str(e))
        return

    if data == "pv_guide":
        text = (
            "📖 راهنمای ربات Sk.team" + NL +
            "━━━━━━━━━━━━━━━━━━━━" + NL + NL +
            "🤖 ربات Sk.team با امکانات کامل، مدیریت گروه شما را آسان می‌کند." + NL + NL +
            "💼 امکانات ربات:" + NL +
            "• 🔒 قفل‌های امنیتی پیشرفته (لینک، تلگرام، هشتگ، وب و...)" + NL +
            "• 📸 قفل رسانه‌ها (متن، ویس، موزیک، فیلم، استیکر و...)" + NL +
            "• 👋 خوش‌آمدگویی خودکار" + NL +
            "• 🔞 فیلتر محتوای بزرگسال (NSFW)" + NL +
            "• 🎵 پخش موزیک در ویس‌کال" + NL +
            "• 🎙️ ضبط خودکار ویس‌کال" + NL +
            "• 👥 مدیریت ادمین‌ها و معاونین" + NL +
            "• 🛒 فروشگاه اشتراک" + NL + NL +
            "🛒 برای خرید اشتراک، از منوی اصلی گزینه فروشگاه را انتخاب کنید." + NL +
            "👑 برای دسترسی به پنل مدیریت، ربات را در گروه صدا بزنید." + NL + NL +
            "👤 پشتیبانی: " + SUPPORT
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 بازگشت", callback_data="pv_home")],
        ])
        await query.edit_message_text(text, reply_markup=kb)
        return




async def pv_owner_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """هندل دکمه‌های پنل مالک گروه در پیوی"""
    query = update.callback_query
    data = query.data
    user = query.from_user
    if not data:
        return
    # چک کن که توی پیوی هستیم
    chat = query.message.chat
    if chat.type != "private":
        return
    
    parts = data.split(":")
    action = parts[0]
    uid = int(parts[1]) if len(parts) > 1 else user.id
    group_chat_id = int(parts[2]) if len(parts) > 2 else 0
    
    # فقط اگه کاربر خودش دکمه رو زده
    if user.id != uid:
        await query.answer("این پنل توسط شما باز نشده!", show_alert=True)
        return
    
    await query.answer()
    
    # بازگشت
    if action == "op_back":
        try:
            from modules.start import sudo_panel_menu, group_owner_panel_menu
            from config import OWNER_ID
            from database import is_bot_admin, is_group_owner, DATABASE_PATH
            import sqlite3
            is_sudo = (user.id == OWNER_ID)
            if not is_sudo:
                try:
                    is_sudo = is_bot_admin(user.id)
                except Exception:
                    pass
            if is_sudo:
                await query.edit_message_text(
                    "👑 منوی اصلی - بخش مورد نظر:",
                    reply_markup=sudo_panel_menu(user.id, group_chat_id or 0)
                )
            else:
                conn = sqlite3.connect(DATABASE_PATH)
                cur = conn.cursor()
                cur.execute("SELECT chat_id FROM groups")
                all_groups = [r[0] for r in cur.fetchall()]
                conn.close()
                target_group = group_chat_id
                if not target_group:
                    for gid in all_groups:
                        try:
                            if is_group_owner(gid, user.id):
                                target_group = gid
                                break
                        except Exception:
                            continue
                await query.edit_message_text(
                    "👑 منوی اصلی - بخش مورد نظر:",
                    reply_markup=group_owner_panel_menu(user.id, target_group)
                )
            _schedule_delete(context, chat.id)
        except Exception as e:
            print("[PV OP_BACK ERR] " + str(e))
        return

    if action == "op_ownerguide":
        text = (
            "📖 راهنمای مالک گروه" + NL +
            "━━━━━━━━━━━━━━━━" + NL + NL +
            "👑 شما به عنوان مالک گروه، به تمام امکانات ربات دسترسی دارید." + NL + NL +
            "💳 اشتراک‌های من: مشاهده وضعیت اشتراک‌های فعال" + NL +
            "👥 مدیریت گروه: مدیریت اعضا، ادمین‌ها، معاونین" + NL +
            "⚙️ تنظیمات گروه: قفل‌ها، خوش‌آمدگویی، NSFW، اخطار، پاکسازی" + NL + NL +
            "📌 برای مدیریت، از دکمه‌های پنل استفاده کنید." + NL + NL +
            "👤 پشتیبانی: @Siavashska"
        )
        try:
            from modules.start import group_owner_panel_menu
            await query.edit_message_text(text, reply_markup=group_owner_panel_menu(user.id, group_chat_id))
            _schedule_delete(context, chat.id)
        except Exception as e:
            print("[PV GUIDE ERR] " + str(e))
        return
    
    # مدیریت گروه
    if action == "owner_section_menu":
        try:
            from modules.start import owner_section_menu
            await query.edit_message_text(
                "🔧 بخش سازنده\n\nگزینه مورد نظر را انتخاب کنید:",
                reply_markup=owner_section_menu(user.id, group_chat_id or 0)
            )
            _schedule_delete(context, chat.id)
        except Exception as e:
            print("[PV SECTION ERR] " + str(e))
        return

    if action == "sudo_panel_back":
        try:
            from modules.start import sudo_panel_menu
            await query.edit_message_text(
                "👑 منوی اصلی - بخش مورد نظر:",
                reply_markup=sudo_panel_menu(user.id, group_chat_id or 0)
            )
            _schedule_delete(context, chat.id)
        except Exception as e:
            print("[PV SUDO BACK ERR] " + str(e))
        return

    if action == "op_manage":
        try:
            from modules.start import owner_manage_menu
            await query.edit_message_text(
                "👥 مدیریت گروه" + NL + NL + "یکی از گزینه‌های زیر را انتخاب کنید:",
                reply_markup=owner_manage_menu(user.id, group_chat_id)
            )
            _schedule_delete(context, chat.id)
        except Exception as e:
            print("[PV MANAGE ERR] " + str(e))
        return
    
    # تنظیمات گروه
    if action == "op_settings":
        try:
            from modules.start import owner_settings_menu
            await query.edit_message_text(
                "⚙️ تنظیمات گروه" + NL + NL + "یکی از گزینه‌های زیر را انتخاب کنید:",
                reply_markup=owner_settings_menu(user.id, group_chat_id)
            )
            _schedule_delete(context, chat.id)
        except Exception as e:
            print("[PV SETTINGS ERR] " + str(e))
        return
    
    # برای جلوگیری از پردازش دوباره توسط start.py
    from telegram.ext import ApplicationHandlerStop
    raise ApplicationHandlerStop




async def order_from_status_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """سفارش از داخل اشتراک‌های من"""
    query = update.callback_query
    data = query.data
    if not data.startswith("ord_"):
        return
    await query.answer()
    
    parts = data.split(":")
    action = parts[0]
    uid = int(parts[1]) if len(parts) > 1 else query.from_user.id
    chat_id = int(parts[2]) if len(parts) > 2 else 0
    
    if action.startswith("ord_cat_"):
        cat = action.replace("ord_cat_", "")
        name = NAMES.get(cat, "اشتراک")
        from database import is_sub_active, get_sub_days_remaining
        is_active = is_sub_active(chat_id, cat)
        current_days = get_sub_days_remaining(chat_id, cat) if is_active else 0
        title = "🔄 تمدید " + name if is_active else "🛒 سفارش " + name
        text = (
            title + NL +
            "━━━━━━━━━━━━━━━━━━━━" + NL + NL
        )
        if is_active:
            text += "📌 اشتراک شما " + str(current_days) + " روز دیگه منقضی می‌شود." + NL
            text += "✅ با تمدید، روزهای جدید به تاریخ فعلی اضافه می‌شود." + NL + NL
        text += "💰 لیست قیمت‌ها:" + NL + NL
        DURATION_DAYS = {"۱ ماهه": 30, "۳ ماهه": 90, "۶ ماهه": 180, "۱ ساله": 365}
        for label, price in PRICES.get(cat, []):
            add_days = DURATION_DAYS.get(label, 30)
            extra = ""
            if is_active:
                total = current_days + add_days
                extra = " (تاریخ جدید: " + str(total) + " روز)"
            text += "• " + label + " → " + price + " تومان" + extra + NL
        text += NL + "👇 برای ادامه، یکی از گزینه‌های زیر را انتخاب کنید:"
        rows = []
        for label, price in PRICES.get(cat, []):
            rows.append([InlineKeyboardButton(label + " - " + price + " تومان", callback_data="ord_buy_" + cat + "_" + label + ":" + str(uid) + ":" + str(chat_id))])
        rows.append([InlineKeyboardButton("🔙 بازگشت", callback_data="ord_back:" + str(uid) + ":" + str(chat_id))])
        rows.append([InlineKeyboardButton("🏠 منوی اصلی", callback_data="pv_home")])
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(rows))
        return
    
    if action.startswith("ord_buy_"):
        rest = action.replace("ord_buy_", "")
        parts2 = rest.split("_")
        cat = parts2[0]
        plan = "_".join(parts2[1:])
        name = NAMES.get(cat, "اشتراک")
        price = "?"
        for lbl, pr in PRICES.get(cat, []):
            if lbl == plan:
                price = pr
                break
        text = (
            "✅ فاکتور شما صادر شد!" + NL +
            "━━━━━━━━━━━━━━━━━━━━" + NL + NL +
            "📦 اشتراک: " + name + NL +
            "⏱️ مدت: " + plan + NL +
            "💰 مبلغ: " + price + " تومان" + NL + NL +
            "💳 شماره کارت:" + NL +
            "`" + CARD_NUMBER + "`" + NL +
            "👤 به نام: " + CARD_HOLDER + NL + NL +
            "📌 لطفاً مبلغ را واریز کنید و رسید را به پشتیبانی ارسال کنید." + NL + NL +
            "☎️ پشتیبانی: " + SUPPORT
        )
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("📩 ارسال رسید به پشتیبانی", url="https://t.me/" + SUPPORT.replace("@", ""))],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="ord_back:" + str(uid) + ":" + str(chat_id))],
            [InlineKeyboardButton("🏠 منوی اصلی", callback_data="pv_home")],
        ])
        await query.edit_message_text(text, reply_markup=kb, parse_mode="Markdown")
        
        # ارسال فاکتور به مالک
        user = query.from_user
        username = "@" + user.username if user.username else "(ندارد)"
        invoice_to_owner = (
            "🔔 فاکتور جدید (از منوی اشتراک‌های من)!" + NL +
            "━━━━━━━━━━━━━━━━━━━━" + NL + NL +
            "👤 کاربر: " + (user.full_name or "کاربر") + NL +
            "🔗 یوزرنیم: " + username + NL +
            "📱 آیدی: `" + str(user.id) + "`" + NL +
            "🏠 آیدی گروه: `" + str(chat_id) + "`" + NL + NL +
            "📦 " + name + NL + "⏱️ " + plan + NL + "💰 " + price + " تومان"
        )
        try:
            await context.bot.send_message(chat_id=OWNER_ID, text=invoice_to_owner, parse_mode="Markdown")
        except Exception as e:
            print("[ORDER INVOICE ERR] " + str(e))
        return
    
    if action == "ord_back":
        # برگرد به اشتراک‌های من
        try:
            from modules.subs_menu import sub_status_menu
            t, kb = sub_status_menu(uid, chat_id)
            await query.edit_message_text(t, reply_markup=kb)
        except Exception as e:
            print("[ORD BACK ERR] " + str(e))
        return


def register(app):
    app.add_handler(CommandHandler("start", start_cmd), group=-10)
    app.add_handler(CallbackQueryHandler(callback_handler, pattern="^pv_"), group=-10)
    app.add_handler(CallbackQueryHandler(order_from_status_handler, pattern="^ord_"), group=-11)
# [DISABLED BY AI TO FIX CONFLICT] app.add_handler(CallbackQueryHandler(pv_owner_callbacks, pattern="^(op_back|op_manage|op_settings|op_ownerguide):"), group=-12)


def refresh_prices():
    """بارگذاری قیمت‌ها از دیتابیس روی PRICES"""
    global PRICES
    try:
        from database import get_setting
    except Exception:
        return
    for cat in list(PRICES.keys()):
        new_plans = []
        for idx, item in enumerate(PRICES[cat]):
            try:
                label, old_price = item
            except Exception:
                continue
            saved = get_setting(0, "price_" + cat + "_" + str(idx))
            new_plans.append((label, saved if saved else old_price))
        PRICES[cat] = new_plans
