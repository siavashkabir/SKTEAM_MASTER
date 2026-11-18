from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import MessageHandler, filters, ContextTypes, CallbackQueryHandler
from config import OWNER_ID

NL = chr(10)

TRIGGERS = ["راهنما مالک", "راهنمای مالک", "دستورات مالک", "پنل مالک", "help owner", "owner help"]


def is_owner(user_id):
    return user_id == OWNER_ID


def guide_menu(uid):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("1 - ساختار منو", callback_data="guide_menu_structure:" + str(uid))],
        [InlineKeyboardButton("2 - دستورات عمومی", callback_data="guide_general:" + str(uid))],
        [InlineKeyboardButton("3 - بخش مدیریت", callback_data="guide_manage:" + str(uid))],
        [InlineKeyboardButton("4 - بخش تنظیمات", callback_data="guide_settings:" + str(uid))],
        [InlineKeyboardButton("5 - قفل ها", callback_data="guide_locks:" + str(uid))],
        [InlineKeyboardButton("6 - خوش آمدگویی", callback_data="guide_welcome:" + str(uid))],
        [InlineKeyboardButton("7 - NSFW", callback_data="guide_nsfw:" + str(uid))],
        [InlineKeyboardButton("8 - اخطار", callback_data="guide_warn:" + str(uid))],
        [InlineKeyboardButton("9 - پاکسازی", callback_data="guide_purge:" + str(uid))],
        [InlineKeyboardButton("10 - لینک گروه", callback_data="guide_link:" + str(uid))],
        [InlineKeyboardButton("11 - اعضای ویژه (VIP)", callback_data="guide_vip:" + str(uid))],
        [InlineKeyboardButton("12 - معاون گروه", callback_data="guide_deputy:" + str(uid))],
        [InlineKeyboardButton("13 - مالک گروه", callback_data="guide_group_owner:" + str(uid))],
        [InlineKeyboardButton("14 - مدیریت دسترسی", callback_data="guide_access:" + str(uid))],
        [InlineKeyboardButton("15 - ادمین های ربات", callback_data="guide_botadmin:" + str(uid))],
        [InlineKeyboardButton("16 - اشتراک", callback_data="guide_sub:" + str(uid))],
        [InlineKeyboardButton("17 - دستورات ویژه مالک", callback_data="guide_owner:" + str(uid))],
        [InlineKeyboardButton("بستن", callback_data="guide_close:" + str(uid))],
    ])


def back_btn(uid):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("بازگشت به منو", callback_data="guide_menu:" + str(uid))],
    ])


async def reply_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    if not msg or not chat or not user:
        return
    if chat.type != "private":
        return
    if not is_owner(user.id):
        return

    text = (msg.text or "").strip()
    if text not in TRIGGERS:
        return

    print("[OWNER GUIDE] opened by " + str(user.id))

    text_out = (
        "راهنمای کامل ربات اسکای تیم" + NL +
        "━━━━━━━━━━━━━━━━━━" + NL + NL +
        "سلام مالک عزیز!" + NL + NL +
        "یه بخش رو انتخاب کن:" + NL + NL +
        "1. ساختار منو" + NL +
        "2. دستورات عمومی" + NL +
        "3. بخش مدیریت" + NL +
        "4. بخش تنظیمات" + NL +
        "5. قفل ها" + NL +
        "6. خوش آمدگویی" + NL +
        "7. NSFW" + NL +
        "8. اخطار" + NL +
        "9. پاکسازی" + NL +
        "10. لینک گروه" + NL +
        "11. اعضای ویژه (VIP)" + NL +
        "12. معاون گروه" + NL +
        "13. مالک گروه" + NL +
        "14. مدیریت دسترسی" + NL +
        "15. ادمین های ربات" + NL +
        "16. اشتراک" + NL +
        "17. دستورات ویژه مالک"
    )
    await msg.reply_text(text_out, reply_markup=guide_menu(user.id))


async def cb_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    clicker = query.from_user.id

    parts = data.split(":")
    action = parts[0]
    owner = int(parts[1]) if len(parts) > 1 else clicker

    if clicker != owner:
        await query.answer("این راهنما برای شما نیست", show_alert=True)
        return
    if not is_owner(clicker):
        await query.answer("فقط مالک ربات دسترسی داره", show_alert=True)
        return

    await query.answer()

    if action == "guide_close":
        try:
            await query.message.delete()
        except Exception:
            pass
        return

    if action == "guide_menu":
        text_out = "راهنمای کامل ربات" + NL + "━━━━━━━━━━━━━━━━━━" + NL + NL + "یه بخش رو انتخاب کن:"
        try:
            await query.edit_message_text(text_out, reply_markup=guide_menu(owner))
        except Exception:
            pass
        return

    if action == "guide_menu_structure":
        text_out = (
            "1 - ساختار منو" + NL + "━━━━━━━━━━━━━━━━━━" + NL + NL +
            "منوی اصلی:" + NL +
            "┌ مدیریت" + NL +
            "└ تنظیمات" + NL + NL +
            "بخش مدیریت:" + NL +
            "• وضعیت گروه" + NL +
            "• صاحبان گروه / مدیران" + NL +
            "• اعضای ویژه / معاونین" + NL + NL +
            "بخش تنظیمات:" + NL +
            "• قفل های اصلی / قفل های رسانه" + NL +
            "• حالت های گروه" + NL +
            "• خوش آمدگویی / NSFW" + NL +
            "• اخطار / پاکسازی" + NL +
            "• لینک گروه" + NL +
            "• دسترسی معاون (فقط مالک)" + NL + NL +
            "پنل پی وی (فقط مالک گروه):" + NL +
            "• مدیریت / تنظیمات برای هر گروه"
        )
        try:
            await query.edit_message_text(text_out, reply_markup=back_btn(owner))
        except Exception:
            pass
        return

    if action == "guide_general":
        text_out = (
                    "📌 بخش General (دستورات عمومی)" + NL + "━━━━━━━━━━━━━━━━━━" + NL + NL +
                    "👤 عمومی:" + NL +
                    "• «آیدی» → آیدی عددی" + NL +
                    "• «اطلاعات» (ریپلای) → پروفایل" + NL +
                    "• «قوانین» → قوانین گروه" + NL + NL +
                    "🕐 زمان:" + NL +
                    "• «ساعت» → ساعت" + NL +
                    "• «تاریخ» / «تقویم» → تاریخ شمسی" + NL + NL +
                    "🎮 سرگرمی:" + NL +
                    "• «فال» → فال حافظ" + NL +
                    "• «جوک» → جوک" + NL +
                    "• «شعر» → شعر" + NL +
                    "• «معما» → معما" + NL +
                    "• «سکه» → شیر یا خط" + NL +
                    "• «قرعه» → قرعه‌کشی" + NL +
                    "• «حدس» → بازی حدس" + NL +
                    "• «جرئت» / «حقیقت» → بازی" + NL + NL +
                    "📝 بیو:" + NL +
                    "• «بیو» / «بیوگرافی» → منوی بیو" + NL +
                    "• «بیو ربات» → توضیحات ربات" + NL + NL +
                    "📖 راهنما:" + NL +
                    "• «راهنما» / /help → همین"
                )
        try:
            await query.edit_message_text(text_out, reply_markup=back_btn(owner))
        except Exception:
            pass
        return

    if action == "guide_manage":
        text_out = '📌 بخش مدیریت (دستورات مالک/ادمین)\n━━━━━━━━━━━━━━━━━━\n\n🔨 بن:\n• «بن» / ban / اخراج / کیک (ریپلای)\n• /ban (ریپلای)\n\n🔇 سکوت:\n• «سکوت» / mute / خفه شو / ساکت (ریپلای)\n• /mute (ریپلای)\n\n⚠️ اخطار:\n• «اخطار» / warn / هشدار (ریپلای)\n• /warn (ریپلای)\n\n🚫 رهایی:\n• «آنبن» / آزادش کن / رهایی / بخشیدمت\n• «رفع سکوت» / حذف سکوت / باز کن\n• /unban (ریپلای)\n\n🗑 پاک\u200cسازی:\n• «پاکسازی» / purge\n\n👮 ادمین:\n• /promote (ریپلای)\n• /demote (ریپلای)\n\n🖥 سیستم (پنل → مدیریت سیستم → تنظیمات):\n• هشدار قبل از ری\u200cاستارت\n• تاخیر ری\u200cاستارت\n• Global Ban / UserInfo\n• بازه چک اتصال\n• Connection Monitor\n• Auto-Start در Termux\n• پاکسازی خودکار\n• VACUUM هفتگی\n• 🗑 حذف خودکار دستور ← جدید\n• ⏱ تایمر پنل ← جدید'
        try:
            await query.edit_message_text(text_out, reply_markup=back_btn(owner))
        except Exception:
            pass
        return

    if action == "guide_settings":
        text_out = (
            "4 - بخش تنظیمات" + NL + "━━━━━━━━━━━━━━━━━━" + NL + NL +
            "توی گروه: پنل → تنظیمات" + NL + NL +
            "🔹 قفل های اصلی / رسانه" + NL +
            "🔹 حالت های گروه" + NL +
            "🔹 خوش آمدگویی" + NL +
            "🔹 NSFW" + NL +
            "🔹 تنظیمات اخطار" + NL +
            "🔹 پاکسازی گروه" + NL +
            "🔹 لینک گروه" + NL +
            "🔹 دسترسی معاون (فقط مالک)" + NL + NL +
            "📌 توجه:" + NL +
            "بر اساس تنظیمات دسترسی معاون،" + NL +
            "ممکنه بعضی بخش ها برای معاون مخفی باشه."
        )
        try:
            await query.edit_message_text(text_out, reply_markup=back_btn(owner))
        except Exception:
            pass
        return

    if action == "guide_locks":
        text_out = (
            "5 - قفل ها" + NL + "━━━━━━━━━━━━━━━━━━" + NL + NL +
            "پنل → تنظیمات → قفل های اصلی" + NL + NL +
            "صفحه 1: لینک، تلگرام، تگ، هشتگ،" + NL +
            "وب، نظرسنجی، ایموجی، اسپویلر" + NL + NL +
            "صفحه 2: فوروارد، ری اکشن، پست،" + NL +
            "پست تکراری، غیرفارسی، انگلیسی،" + NL +
            "مبهم، توهین" + NL + NL +
            "صفحه 3: درون خطی" + NL + NL +
            "قفل های رسانه:" + NL +
            "رسانه، متن، ویس، موزیک، فیلم، سلفی،" + NL +
            "استیکر، استیکر متحرک، گیف، عکس، فایل،" + NL +
            "موقعیت، مخاطب"
        )
        try:
            await query.edit_message_text(text_out, reply_markup=back_btn(owner))
        except Exception:
            pass
        return

    if action == "guide_welcome":
        text_out = (
            "6 - خوش آمدگویی" + NL + "━━━━━━━━━━━━━━━━━━" + NL + NL +
            "پنل → تنظیمات → خوش آمدگویی" + NL + NL +
            "🔹 روشن/خاموش" + NL +
            "🔹 ویرایش متن:" + NL +
            "   روی دکمه بزن، بعد توی همون گروه" + NL +
            "   متن رو بفرست (پیام خودکار حذف می شه)" + NL +
            "   متغیرها: {mention} و {group_name}" + NL + NL +
            "🔹 نوع رسانه: عکس / گیف / ویدیو" + NL +
            "   روی نوع بزن، بعد توی گروه رسانه رو بفرست" + NL + NL +
            "🔹 حذف رسانه فعلی" + NL +
            "🔹 زمان حذف خودکار: 0، 10ث، 30ث، 1د، 5د، 10د، 30د"
        )
        try:
            await query.edit_message_text(text_out, reply_markup=back_btn(owner))
        except Exception:
            pass
        return

    if action == "guide_nsfw":
        text_out = (
            "7 - NSFW" + NL + "━━━━━━━━━━━━━━━━━━" + NL + NL +
            "پنل → تنظیمات → NSFW" + NL + NL +
            "🔹 روشن/خاموش" + NL +
            "🔹 حساسیت:" + NL +
            "   • کم (0.85) - فقط واضح ها" + NL +
            "   • متوسط (0.7) - عادی" + NL +
            "   • زیاد (0.5) - سختگیرانه" + NL + NL +
            "هر بار NSFW → 1 اخطار" + NL +
            "بعد از رسیدن به حد → سکوت/اخراج/بن"
        )
        try:
            await query.edit_message_text(text_out, reply_markup=back_btn(owner))
        except Exception:
            pass
        return

    if action == "guide_warn":
        text_out = (
            "8 - اخطار" + NL + "━━━━━━━━━━━━━━━━━━" + NL + NL +
            "پنل → تنظیمات → تنظیمات اخطار" + NL + NL +
            "🔹 روشن/خاموش کردن سیستم اخطار" + NL +
            "🔹 تعداد اخطار تا اقدام: 3 / 4 / 5 / 10" + NL +
            "🔹 اقدام در صورت رسیدن به حد:" + NL +
            "   • سکوت دائم" + NL +
            "   • اخراج از گروه" + NL +
            "   • بن دائم" + NL + NL +
            "دستورات ادمین (با ریپلای):" + NL +
            "• اخطار" + NL +
            "• سکوت" + NL +
            "• آزاد" + NL +
            "• پاک اخطار" + NL + NL +
            "نمایش تعداد اخطار خودت:" + NL +
            "بنویس: اخطارها"
        )
        try:
            await query.edit_message_text(text_out, reply_markup=back_btn(owner))
        except Exception:
            pass
        return

    if action == "guide_purge":
        text_out = (
            "9 - پاکسازی" + NL + "━━━━━━━━━━━━━━━━━━" + NL + NL +
            "پاکسازی دستی (توی گروه):" + NL +
            "• پاکسازی → همه پیام های کش شده" + NL +
            "• پاکسازی 10 → 10 پیام آخر" + NL +
            "• پاکسازی 50 → 50 پیام آخر" + NL +
            "• پاکسازی 100 → 100 پیام آخر" + NL + NL +
            "پاکسازی خودکار:" + NL +
            "پنل → تنظیمات → پاکسازی" + NL +
            "• روشن/خاموش" + NL +
            "• ساعت (مثلاً 03:00)" + NL +
            "• بخش ها: متن، گیف، استیکر،" + NL +
            "  عکس، ویدیو، ویس، فایل" + NL + NL +
            "📌 محدودیت: 48 ساعت اخیر + 100 پیام در هر بار"
        )
        try:
            await query.edit_message_text(text_out, reply_markup=back_btn(owner))
        except Exception:
            pass
        return

    if action == "guide_link":
        text_out = (
            "10 - لینک گروه" + NL + "━━━━━━━━━━━━━━━━━━" + NL + NL +
            "پنل → تنظیمات → لینک گروه" + NL +
            "یا توی گروه بنویس: لینک" + NL + NL +
            "🔹 لینک یکبار مصرف" + NL +
            "   بعد از اولین استفاده منقضی می شه" + NL + NL +
            "🔹 لینک دائمی" + NL +
            "   همیشه کار می کنه" + NL + NL +
            "بعد از ساخت لینک:" + NL +
            "• اشتراک گذاری (Share تلگرام)" + NL +
            "• ارسال به صورت عکس" + NL +
            "• ارسال به صورت متن" + NL + NL +
            "📌 لینک ها با اسپویلر مخفی هستن" + NL +
            "(کاربر باید روش بزنه تا ببینه)"
        )
        try:
            await query.edit_message_text(text_out, reply_markup=back_btn(owner))
        except Exception:
            pass
        return

    if action == "guide_vip":
        text_out = (
            "11 - اعضای ویژه (VIP)" + NL + "━━━━━━━━━━━━━━━━━━" + NL + NL +
            "فقط مالک گروه می تونه VIP بذاره." + NL + NL +
            "دستورات (توی گروه - با ریپلای):" + NL +
            "• تنظیم ویژه → VIP دائمی" + NL +
            "• تنظیم ویژه 24 → 24 ساعته" + NL +
            "• تنظیم ویژه 48 → 48 ساعته" + NL +
            "• تنظیم ویژه 72 → 72 ساعته" + NL +
            "• تنظیم ویژه 5 روز → 5 روزه" + NL +
            "• تنظیم ویژه 7 روز → 7 روزه" + NL +
            "• تنظیم ویژه 30 روز → 30 روزه" + NL +
            "• حذف ویژه" + NL +
            "• لیست ویژه ها" + NL + NL +
            "دسترسی VIP (قابل تنظیم):" + NL +
            "• ارسال عکس، گیف، ویدیو، استیکر" + NL +
            "• ارسال ویس، فایل، لینک" + NL +
            "• منشن کردن" + NL + NL +
            "محدودیت VIP:" + NL +
            "• معاف از NSFW نیست" + NL +
            "• نمی تونه فوروارد کنه" + NL +
            "• نمی تونه همه رو تگ کنه"
        )
        try:
            await query.edit_message_text(text_out, reply_markup=back_btn(owner))
        except Exception:
            pass
        return

    if action == "guide_deputy":
        text_out = (
            "12 - معاون گروه" + NL + "━━━━━━━━━━━━━━━━━━" + NL + NL +
            "دستورات (توی گروه - با ریپلای):" + NL +
            "• معاون → تعیین معاون" + NL +
            "• حذف معاون" + NL +
            "• معاون (بدون ریپلای) → لیست معاونین" + NL + NL +
            "کی می تونه معاون تعیین کنه؟" + NL +
            "• مالک ربات" + NL +
            "• ادمین های ربات (سودو)" + NL +
            "• مالک گروه" + NL +
            "• سازنده گروه" + NL + NL +
            "تنظیم دسترسی معاون:" + NL +
            "پنل → تنظیمات → دسترسی معاون" + NL +
            "(فقط مالک می تونه تنظیم کنه)"
        )
        try:
            await query.edit_message_text(text_out, reply_markup=back_btn(owner))
        except Exception:
            pass
        return

    if action == "guide_group_owner":
        text_out = (
            "13 - مالک گروه" + NL + "━━━━━━━━━━━━━━━━━━" + NL + NL +
            "مالک گروه کیه؟" + NL +
            "کاربری که ربات رو برای مدیریت گروه" + NL +
            "بهش تحویل می دیم. دسترسی تنظیمات داره." + NL + NL +
            "دستورات (توی گروه - با ریپلای):" + NL +
            "• مالک → تعیین مالک" + NL +
            "• مالک (بدون ریپلای) → نمایش مالک" + NL +
            "• حذف مالک" + NL + NL +
            "کی می تونه مالک تعیین کنه؟" + NL +
            "• مالک ربات (تو)" + NL +
            "• ادمین های ربات (سودو)" + NL + NL +
            "دسترسی مالک گروه:" + NL +
            "• همه تنظیمات گروه" + NL +
            "• تعیین معاون" + NL +
            "• مدیریت VIP" + NL +
            "• لینک، پاکسازی، NSFW و..."
        )
        try:
            await query.edit_message_text(text_out, reply_markup=back_btn(owner))
        except Exception:
            pass
        return

    if action == "guide_access":
        text_out = (
            "14 - مدیریت دسترسی" + NL + "━━━━━━━━━━━━━━━━━━" + NL + NL +
            "دستور: دسترسی (با ریپلای)" + NL + NL +
            "روی پیام کاربر ریپلای کن" + NL +
            "و بنویس: دسترسی" + NL + NL +
            "بسته به نقش کاربر:" + NL +
            "• مالک ربات/ادمین ربات → نمایش فقط" + NL +
            "• مالک گروه → دسترسی های معاون" + NL +
            "• معاون → دسترسی های معاون" + NL +
            "• عضو ویژه (VIP) → 8 دسترسی VIP" + NL +
            "• عضو عادی → 12 دسترسی ادمین" + NL + NL +
            "کی می تونه دسترسی تغییر بده؟" + NL +
            "• مالک ربات" + NL +
            "• ادمین های ربات" + NL +
            "• مالک گروه" + NL + NL +
            "📌 هر دکمه بزنی → toggle می شه"
        )
        try:
            await query.edit_message_text(text_out, reply_markup=back_btn(owner))
        except Exception:
            pass
        return

    if action == "guide_botadmin":
        text_out = (
            "15 - ادمین های ربات (سودو)" + NL + "━━━━━━━━━━━━━━━━━━" + NL + NL +
            "توی پی وی ربات:" + NL +
            "• ادمین ربات کن 123456789" + NL +
            "• یا ریپلای روی فوروارد + ادمین ربات کن" + NL +
            "• حذف ادمین ربات 123456789" + NL +
            "• لیست ادمین های ربات" + NL + NL +
            "دسترسی کامل (سودو):" + NL +
            "• همه تنظیمات" + NL +
            "• تعیین مالک گروه" + NL +
            "• ریستارت / پیکربندی" + NL +
            "• تمدید اشتراک" + NL +
            "• افزودن ربات به گروه های دیگه" + NL + NL +
            "محدودیت:" + NL +
            "• نمی تونه ادمین ربات اضافه/حذف کنه" + NL +
            "  (فقط مالک ربات)"
        )
        try:
            await query.edit_message_text(text_out, reply_markup=back_btn(owner))
        except Exception:
            pass
        return

    if action == "guide_sub":
        text_out = (
            "16 - اشتراک و تمدید" + NL + "━━━━━━━━━━━━━━━━━━" + NL + NL +
            "/activate 30 - فعال سازی 30 روزه" + NL +
            "/activate 90 - 90 روزه" + NL +
            "/activate 365 - 1 ساله" + NL +
            "/deactivate - غیرفعال کردن" + NL +
            "/subscription - وضعیت اشتراک" + NL + NL +
            "کی می تونه؟" + NL +
            "• مالک ربات" + NL +
            "• ادمین های ربات (سودو)" + NL +
            "• مالک گروه" + NL + NL +
            "بدون اشتراک، ربات توی گروه کار نمی کنه" + NL +
            "(وسط پیام ها و کلمات کلیدی بلاک می شه)"
        )
        try:
            await query.edit_message_text(text_out, reply_markup=back_btn(owner))
        except Exception:
            pass
        return

    if action == "guide_owner":
        text_out = '📌 بخش سازنده\n━━━━━━━━━━━━━━━━━━\n\n🔒 FJ (جوین اجباری):\n• /setfj [link] → افزودن لینک\n• /setfj → حذف همه\n• توی PV ربات\n\n📢 کانال لاگ:\n• گلوبال: PV → بخش سازنده → 📢 کانال لاگ گلوبال\n• گروه: پنل گروه → ⚙️ تنظیمات گروه → 📢 کانال لاگ گروه\n• روش: یه پیام از کانال رو فوروارد کن\n\n👑 پنل سازنده (PV):\n• 🖥 مدیریت سیستم\n• 🔧 بخش سازنده\n• 💎 مدیریت اشتراک\u200cها\n• 📖 راهنمای کامل\n• ⚙️ تنظیمات این گروه\n• 📢 کانال لاگ گلوبال\n\n🛡 ویژه:\n• /restart → ری\u200cاستارت\n• /stats → آمار\n• /setfj → FJ\n\n🎙 Userbot:\n• ضبط کال (PV مالک)\n• فقط سازنده/سودو'
        try:
            await query.edit_message_text(text_out, reply_markup=back_btn(owner))
        except Exception:
            pass
        return


def register(app):
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_handler, block=False), group=30)
    app.add_handler(CallbackQueryHandler(cb_handler, pattern="^guide_"), group=31)
