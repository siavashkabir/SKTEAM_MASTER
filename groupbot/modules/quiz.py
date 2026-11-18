import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, MessageHandler, CallbackQueryHandler, filters

NL = chr(10)

QUIZ_TRIGGERS = ["کوییز", "کوئیز", "quiz"]

# State: {chat_id: {"players": [uid], "names": {uid: name}, "turn": 0, "scores": {uid: score}, "current_q": {}, "active": False, "starter_id": 0, "sent_msgs": [], "category": None}}
QUIZ_GAME = {}

CATEGORIES = {
    "general": "🌍 عمومی",
    "history": "📜 تاریخ",
    "sports": "⚽ ورزش",
    "cinema": "🎬 سینما",
    "science": "🔬 علمی",
    "geo": "🌐 جغرافیا",
}

# فرمت: (سوال، [گزینه‌ها], ایندکس پاسخ درست)
QUESTIONS = {
    "general": [
        ("کدام یک از این‌ها پایتخت فرانسه است؟", ["لندن", "پاریس", "برلین", "مادرید"], 1),
        ("بزرگ‌ترین اقیانوس جهان کدام است؟", ["اطلس", "هند", "آرام", "منجمد شمالی"], 2),
        ("چند قاره در جهان وجود دارد؟", ["5", "6", "7", "8"], 2),
        ("کدام کشور بیشترین جمعیت را دارد؟", ["آمریکا", "هند", "چین", "اندونزی"], 1),
        ("زبان رسمی برزیل چیست؟", ["اسپانیایی", "انگلیسی", "پرتغالی", "فرانسوی"], 2),
        ("کدام حیوان بزرگ‌ترین پستاندار جهان است؟", ["فیل", "نهنگ آبی", "زرافه", "کرگدن"], 1),
        ("واحد اندازه‌گیری نیرو چیست؟", ["وات", "ژول", "نیوتن", "پاسکال"], 2),
        ("کدام فلز در دمای اتاق مایع است؟", ["آهن", "جیوه", "طلا", "مس"], 1),
        ("بلندترین برج جهان کجاست؟", ["ژاپن", "امارات", "چین", "آمریکا"], 1),
        ("چه کسی تلفن را اختراع کرد؟", ["ادیسون", "تسلا", "بل", "مارکونی"], 2),
        ("کدام رنگ از ترکیب آبی و زرد به دست می‌آید؟", ["بنفش", "سبز", "نارنجی", "قهوه‌ای"], 1),
        ("کدام سیاره به سیاره سرخ معروف است؟", ["زهره", "مریخ", "مشتری", "زحل"], 1),
        ("چند بازیکن در یک تیم فوتبال داخل زمین هستند؟", ["9", "10", "11", "12"], 2),
        ("پایتخت ایران کجاست؟", ["اصفهان", "تهران", "شیراز", "مشهد"], 1),
        ("بزرگ‌ترین کشور جهان از نظر مساحت کدام است؟", ["کانادا", "چین", "روسیه", "آمریکا"], 2),
    ],
    "history": [
        ("جنگ جهانی دوم در چه سالی آغاز شد؟", ["1914", "1939", "1945", "1918"], 1),
        ("جنگ جهانی دوم در چه سالی پایان یافت؟", ["1943", "1945", "1947", "1950"], 1),
        ("کوروش کبیر بنیان‌گذار کدام امپراتوری بود؟", ["ساسانیان", "هخامنشیان", "اشکانیان", "سلجوقیان"], 1),
        ("دیوار برلین در چه سالی فرو ریخت؟", ["1985", "1989", "1991", "1993"], 1),
        ("انقلاب فرانسه در چه سالی رخ داد؟", ["1776", "1789", "1799", "1804"], 1),
        ("چه کسی آمریکا را کشف کرد؟", ["ماژلان", "کلمب", "واسکو دوگاما", "جیمز کوک"], 1),
        ("کدام تمدن اولین خط را اختراع کرد؟", ["مصر", "سومر", "چین", "هند"], 1),
        ("هیتلر رهبر کدام حزب بود؟", ["کمونیست", "نازی", "دموکرات", "جمهوری‌خواه"], 1),
        ("اولین انسان روی ماه چه کسی بود؟", ["باز آلدرین", "نیل آرمسترانگ", "یوری گاگارین", "جان گلن"], 1),
        ("جنگ سرد بین کدام دو کشور بود؟", ["آمریکا و چین", "آمریکا و شوروی", "آلمان و فرانسه", "انگلیس و روسیه"], 1),
        ("کدام سلسله ایران را فتح کرد؟", ["عثمانی", "مغول", "عرب", "تیموری"], 2),
        ("انقلاب اسلامی ایران در چه سالی رخ داد؟", ["1977", "1978", "1979", "1980"], 2),
        ("چه کسی اولین رئیس‌جمهور آمریکا بود؟", ["لینکلن", "واشنگتن", "جفرسون", "آدامز"], 1),
        ("کدام کشور اولین بار بمب اتم را ساخت؟", ["شوروی", "آمریکا", "آلمان", "انگلیس"], 1),
        ("رنسانس از کدام کشور شروع شد؟", ["فرانسه", "ایتالیا", "آلمان", "انگلیس"], 1),
    ],
    "sports": [
        ("چند بازیکن در تیم والیبال داخل زمین هستند؟", ["5", "6", "7", "8"], 1),
        ("المپیک هر چند سال یک بار برگزار می‌شود؟", ["2", "3", "4", "5"], 2),
        ("مسی فوتبالیست کدام کشور است؟", ["برزیل", "آرژانتین", "پرتغال", "اسپانیا"], 1),
        ("رونالدو فوتبالیست کدام کشور است؟", ["برزیل", "پرتغال", "آرژانتین", "فرانسه"], 1),
        ("کدام کشور بیشترین قهرمانی جام جهانی فوتبال را دارد؟", ["آلمان", "ایتالیا", "برزیل", "آرژانتین"], 2),
        ("بسکتبال چند کوارتر دارد؟", ["2", "3", "4", "5"], 2),
        ("کدام ورزش با راکت انجام می‌شود؟", ["فوتبال", "تنیس", "بسکتبال", "شنا"], 1),
        ("تیم رئال مادرید در کدام کشور است؟", ["ایتالیا", "اسپانیا", "فرانسه", "انگلیس"], 1),
        ("چه کسی بیشترین توپ طلا را برده است؟", ["مسی", "رونالدو", "پله", "مارادونا"], 0),
        ("کدام ورزش به ورزش پادشاهان معروف است؟", ["فوتبال", "گلف", "تنیس", "شطرنج"], 1),
        ("مسابقات فرمول یک شامل چند تیم است؟", ["8", "10", "12", "14"], 1),
        ("کدام کشور میزبان جام جهانی 2022 بود؟", ["روسیه", "قطر", "برزیل", "آلمان"], 1),
        ("چند دقیقه هر نیمه فوتبال است؟", ["40", "45", "50", "60"], 1),
        ("کدام شنا سرعتی‌ترین است؟", ["کرال سینه", "قورباغه", "پروانه", "کرال پشت"], 0),
        ("کدام ورزش در زمین یخ انجام می‌شود؟", ["هاکی", "اسکی", "اسکیت", "کرلینگ"], 0),
    ],
    "cinema": [
        ("کارگردان فیلم تایتانیک کیست؟", ["اسپیلبرگ", "کامرون", "نولان", "اسکورسیزی"], 1),
        ("فیلم ماتریکس در چه سالی اکران شد؟", ["1997", "1999", "2001", "2003"], 1),
        ("چه کسی نقش جک Sparrow را بازی کرد؟", ["براد پیت", "جانی دپ", "تام کروز", "لئوناردو"], 1),
        ("کارگردان فیلم Inception کیست؟", ["کریستوفر نولان", "کوئنتین", "اسپیلبرگ", "کامرون"], 0),
        ("فیلم Godfather در چه سالی اکران شد؟", ["1969", "1972", "1975", "1980"], 1),
        ("چه کسی نقش آیرون‌من را بازی کرد؟", ["کریس ایوانز", "رابرت داونی", "مارک رافلو", "کریس همسورث"], 1),
        ("انیمیشن شیرشاه محصول کدام شرکت است؟", ["پیکسار", "دیزنی", "دریم‌ورکس", "سونی"], 1),
        ("کارگردان فیلم Avatar کیست؟", ["کامرون", "اسپیلبرگ", "نولان", "پیتر جکسون"], 0),
        ("فیلم Titanic در چه سالی اکران شد؟", ["1995", "1997", "1999", "2001"], 1),
        ("چه کسی برنده اسکار بهترین بازیگر مرد 2020 شد؟", ["خواکین فینیکس", "لئوناردو", "براد پیت", "تام هنکس"], 0),
        ("کدام فیلم بیشترین فروش تاریخ را دارد؟", ["تایتانیک", "آواتار", "انتقام‌جویان", "جنگ ستارگان"], 1),
        ("کارگردان فیلم پارازیت کیست؟", ["بونگ جون هو", "پارک چان ووک", "کیم کی دوک", "لی چانگ دونگ"], 0),
        ("فیلم Fight Club در چه سالی اکران شد؟", ["1997", "1999", "2001", "2003"], 1),
        ("چه کسی نقش نئو در ماتریکس را بازی کرد؟", ["کیانو ریوز", "تام کروز", "برد پیت", "مت دیمون"], 0),
        ("انیمه Spirited Away محصول کدام کشور است؟", ["چین", "کره", "ژاپن", "تایلند"], 2),
    ],
    "science": [
        ("آب از چه عناصری تشکیل شده است؟", ["H2O", "CO2", "O2", "NaCl"], 0),
        ("سرعت نور چقدر است؟", ["300,000 km/s", "150,000 km/s", "1,000 km/s", "30,000 km/s"], 0),
        ("کدام اندام بدن انسان خون را پمپاژ می‌کند؟", ["کبد", "قلب", "ریه", "کلیه"], 1),
        ("چه کسی نظریه نسبیت را ارائه داد؟", ["نیوتن", "اینشتین", "گالیله", "بور"], 1),
        ("بزرگ‌ترین استخوان بدن انسان کدام است؟", ["ران", "بازو", "جمجمه", "دنده"], 0),
        ("کدام گاز بیشترین درصد اتمسفر زمین را تشکیل می‌دهد؟", ["اکسیژن", "نیتروژن", "دی‌اکسید کربن", "هیدروژن"], 1),
        ("خون در کدام اندام تصفیه می‌شود؟", ["قلب", "کلیه", "کبد", "طحال"], 1),
        ("سلول‌های بدن از چه چیزی ساخته شده‌اند؟", ["مولکول", "اتم", "بافت", "اندام"], 0),
        ("کدام سیاره به زمین نزدیک‌تر است؟", ["زهره", "مریخ", "مشتری", "عطارد"], 0),
        ("واحد اندازه‌گیری دما چیست؟", ["متر", "کلوین", "گرم", "ثانیه"], 1),
        ("چه کسی واکسن فلج اطفال را ساخت؟", ["پاستور", "سالک", "ادیسون", "فلمینگ"], 1),
        ("کدام یاخته‌ها در مبارزه با بیماری نقش دارند؟", ["گلبول سفید", "گلبول قرمز", "پلاکت", "پلاسما"], 0),
        ("کدام قند در شیر وجود دارد؟", ["گلوکز", "لاکتوز", "ساکارز", "فروکتوز"], 1),
        ("انرژی هسته‌ای از چه فرایندی آزاد می‌شود؟", ["احتراق", "شکافت", "تبخیر", "انجماد"], 1),
        ("کدام فلز رساناترین است؟", ["مس", "طلا", "نقره", "آهن"], 2),
    ],
    "geo": [
        ("بلندترین کوه جهان کدام است؟", ["اورست", "کی۲", "دماوند", "فوجی"], 0),
        ("طویل‌ترین رودخانه جهان کدام است؟", ["نیل", "آمازون", "میسوری", "یانگ‌تسه"], 0),
        ("بزرگ‌ترین بیابان جهان کدام است؟", ["صحرا", "گبی", "کالاهاری", "آتاکاما"], 0),
        ("پایتخت ژاپن کجاست؟", ["اوساکا", "توکیو", "کیوتو", "ناگویا"], 1),
        ("کدام اقیانوس کوچک‌ترین است؟", ["آرام", "اطلس", "هند", "منجمد شمالی"], 3),
        ("کدام کشور بزرگ‌ترین تولیدکننده نفت است؟", ["عربستان", "روسیه", "آمریکا", "ایران"], 2),
        ("دریای خزر در کدام قاره است؟", ["اروپا و آسیا", "آفریقا", "آمریکا", "استرالیا"], 0),
        ("پایتخت استرالیا کجاست؟", ["سیدنی", "ملبورن", "کانبرا", "پرت"], 2),
        ("کدام کشور بیشترین مرز را با کشورهای دیگر دارد؟", ["روسیه", "چین", "برزیل", "هند"], 1),
        ("پرجمعیت‌ترین شهر جهان کدام است؟", ["توکیو", "دهلی", "شانگهای", "سائوپائولو"], 0),
        ("کوچک‌ترین کشور جهان کدام است؟", ["موناکو", "واتیکان", "سان مارینو", "لیختن‌اشتاین"], 1),
        ("کدام کشور در دو قاره واقع شده است؟", ["مصر", "ترکیه", "روسیه", "همه موارد"], 3),
        ("بلندترین آبشار جهان کدام است؟", ["آنخل", "نیاگارا", "ویکتوریا", "ایگواسو"], 0),
        ("بزرگ‌ترین جزیره جهان کدام است؟", ["گرینلند", "استرالیا", "ماداگاسکار", "بورنئو"], 0),
        ("کدام کشور بیشترین تعداد جزیره را دارد؟", ["اندونزی", "فیلیپین", "سوئد", "نروژ"], 2),
    ],
}


def quiz_main_menu(chat_id):
    g = QUIZ_GAME.get(chat_id)
    players_count = len(g["players"]) if g and g.get("players") else 0
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📝 شرکت کردن (" + str(players_count) + ")", callback_data="qz_join")],
        [InlineKeyboardButton("▶️ شروع بازی", callback_data="qz_start")],
        [InlineKeyboardButton("👥 لیست شرکت‌کننده‌ها", callback_data="qz_list")],
        [InlineKeyboardButton("🏆 امتیازها", callback_data="qz_scores")],
        [InlineKeyboardButton("❌ بستن", callback_data="qz_close")],
    ])


def quiz_category_menu():
    kb = []
    row = []
    for key, label in CATEGORIES.items():
        row.append(InlineKeyboardButton(label, callback_data="qz_cat_" + key))
        if len(row) == 2:
            kb.append(row)
            row = []
    if row:
        kb.append(row)
    kb.append([InlineKeyboardButton("🎲 رندوم", callback_data="qz_cat_random")])
    kb.append([InlineKeyboardButton("🔙 بازگشت", callback_data="qz_back")])
    return InlineKeyboardMarkup(kb)


def quiz_game_kb(chat_id):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎯 سوال بعدی", callback_data="qz_next_q")],
        [InlineKeyboardButton("🏆 امتیازها", callback_data="qz_scores")],
        [InlineKeyboardButton("🛑 پایان بازی", callback_data="qz_end")],
    ])


def quiz_answer_kb(cat, q_idx):
    # دکمه‌های A, B, C, D
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("الف", callback_data="qz_ans_" + cat + "_" + str(q_idx) + "_0")],
        [InlineKeyboardButton("ب", callback_data="qz_ans_" + cat + "_" + str(q_idx) + "_1")],
        [InlineKeyboardButton("ج", callback_data="qz_ans_" + cat + "_" + str(q_idx) + "_2")],
        [InlineKeyboardButton("د", callback_data="qz_ans_" + cat + "_" + str(q_idx) + "_3")],
    ])


async def quiz_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    if not msg or not chat or not user or not msg.text:
        return
    if chat.type not in ("group", "supergroup"):
        return
    try:
        from database import get_setting, is_group_owner, is_bot_admin
        from config import OWNER_ID
        if get_setting(chat.id, "games_enabled", "1") != "1":
            allowed = (user.id == OWNER_ID or is_bot_admin(user.id) or is_group_owner(chat.id, user.id))
            if not allowed:
                return
    except Exception:
        pass
    text = msg.text.strip().lower()
    if text not in [t.lower() for t in QUIZ_TRIGGERS]:
        return
    g = QUIZ_GAME.get(chat.id)
    if g and g.get("active"):
        await msg.reply_text("⚠️ یه بازی در جریانه.")
        return
    if not g:
        QUIZ_GAME[chat.id] = {
            "players": [], "names": {}, "turn": 0, "scores": {},
            "current_q": {}, "active": False, "starter_id": user.id,
            "sent_msgs": [], "category": None, "used_qs": []
        }
    else:
        if not g.get("starter_id"):
            g["starter_id"] = user.id
    await msg.reply_text(
        "🎓 کوییز اطلاعات عمومی" + NL + "━━━━━━━━━━━━━━━━" + NL + NL +
        "📌 برای شرکت، روی «شرکت کردن» بزنید." + NL +
        "📌 حداقل ۲ نفر لازمه." + NL +
        "📌 وقتی همه شرکت کردن، سازنده «شروع بازی» رو بزنه." + NL + NL +
        "👤 کنترل پنل: " + (user.first_name or "کاربر"),
        reply_markup=quiz_main_menu(chat.id)
    )


async def quiz_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    user = query.from_user
    chat = query.message.chat

    # ۱. شرکت کردن
    if data == "qz_join":
        g = QUIZ_GAME.setdefault(chat.id, {"players": [], "names": {}, "turn": 0, "scores": {}, "current_q": {}, "active": False, "starter_id": user.id, "sent_msgs": [], "category": None, "used_qs": []})
        if g.get("active"):
            await query.answer("بازی در جریانه!", show_alert=True)
            return
        if user.id in g["players"]:
            await query.answer("قبلاً شرکت کردی!", show_alert=True)
            return
        g["players"].append(user.id)
        g["names"][user.id] = user.first_name or "کاربر"
        g["scores"][user.id] = 0
        await query.answer("✅ شرکت کردی!")
        try:
            await query.edit_message_reply_markup(reply_markup=quiz_main_menu(chat.id))
        except Exception:
            pass
        return

    # ۲. شروع بازی
    if data == "qz_start":
        g = QUIZ_GAME.get(chat.id)
        if not g or len(g.get("players", [])) < 2:
            await query.answer("حداقل ۲ نفر باید شرکت کنن!", show_alert=True)
            return
        if g.get("active"):
            await query.answer("بازی شروع شده!", show_alert=True)
            return
        if g.get("starter_id") and user.id != g.get("starter_id"):
            await query.answer("فقط سازنده بازی می‌تونه شروع کنه!", show_alert=True)
            return
        await query.answer()
        # نمایش منوی دسته‌بندی
        try:
            await query.edit_message_text(
                "🎓 دسته‌بندی سوال رو انتخاب کن:",
                reply_markup=quiz_category_menu()
            )
        except Exception:
            pass
        return

    # ۳. انتخاب دسته
    if data.startswith("qz_cat_"):
        g = QUIZ_GAME.get(chat.id)
        if not g:
            await query.answer()
            return
        cat = data.replace("qz_cat_", "")
        if cat == "random":
            cat = random.choice(list(QUESTIONS.keys()))
        if cat not in QUESTIONS:
            await query.answer("دسته نامعتبر!", show_alert=True)
            return
        g["active"] = True
        g["turn"] = 0
        g["category"] = cat
        g["used_qs"] = []
        cat_label = CATEGORIES.get(cat, cat)
        # پاک کردن پیام منو
        try:
            await query.message.delete()
        except Exception:
            pass
        # ارسال پیام شروع
        first_uid = g["players"][0]
        first_name = g["names"].get(first_uid, "کاربر")
        text = (
            "🎓 کوییز شروع شد!" + NL + "━━━━━━━━━━━━━━━━" + NL + NL +
            "📚 دسته: " + cat_label + NL +
            "👥 شرکت‌کننده‌ها: " + str(len(g["players"])) + " نفر" + NL +
            "👤 کنترل پنل: " + (user.first_name or "کاربر") + NL + NL +
            "🎯 نوبت: " + first_name + NL + NL +
            "لطفاً " + first_name + " روی «سوال بعدی» بزن."
        )
        try:
            sent = await context.bot.send_message(chat_id=chat.id, text=text, reply_markup=quiz_game_kb(chat.id))
            g["sent_msgs"] = [sent.message_id]
        except Exception as e:
            print("[QUIZ START ERR] " + str(e))
        return

    if data == "qz_back":
        await query.answer()
        try:
            await query.edit_message_text(
                "🎓 کوییز اطلاعات عمومی" + NL + "━━━━━━━━━━━━━━━━" + NL + NL +
                "📌 برای شرکت، روی «شرکت کردن» بزنید.",
                reply_markup=quiz_main_menu(chat.id)
            )
        except Exception:
            pass
        return

    # ۴. سوال بعدی
    if data == "qz_next_q":
        g = QUIZ_GAME.get(chat.id)
        if not g or not g.get("active"):
            await query.answer("بازی فعال نیست!", show_alert=True)
            return
        # چک نوبت
        current_uid = g["players"][g["turn"]]
        if user.id != current_uid:
            await query.answer("نوبت شما نیست! نوبت " + g["names"].get(current_uid, "کاربر") + " هست.", show_alert=True)
            return
        cat = g.get("category")
        if not cat:
            await query.answer("دسته نامشخصه!", show_alert=True)
            return
        pool = QUESTIONS.get(cat, [])
        # پیدا کردن سوال استفاده نشده
        used = g.get("used_qs", [])
        available = [i for i in range(len(pool)) if i not in used]
        if not available:
            used = []
            available = list(range(len(pool)))
        q_idx = random.choice(available)
        used.append(q_idx)
        g["used_qs"] = used
        q_text, options, correct = pool[q_idx]
        g["current_q"] = {"cat": cat, "idx": q_idx, "correct": correct, "answered": False}
        current_name = g["names"].get(current_uid, "کاربر")
        text = (
            "🎯 سوال برای " + current_name + NL + "━━━━━━━━━━━━━━━━" + NL + NL +
            q_text + NL + NL +
            "الف) " + options[0] + NL +
            "ب) " + options[1] + NL +
            "ج) " + options[2] + NL +
            "د) " + options[3]
        )
        # پاک کردن پیام‌های قبلی
        for mid in g.get("sent_msgs", []):
            try:
                await context.bot.delete_message(chat_id=chat.id, message_id=mid)
            except Exception:
                pass
        g["sent_msgs"] = []
        try:
            sent = await context.bot.send_message(chat_id=chat.id, text=text, reply_markup=quiz_answer_kb(cat, q_idx))
            g["sent_msgs"].append(sent.message_id)
        except Exception as e:
            print("[QUIZ Q ERR] " + str(e))
        return

    # ۵. جواب دادن
    if data.startswith("qz_ans_"):
        g = QUIZ_GAME.get(chat.id)
        if not g or not g.get("active"):
            await query.answer("بازی فعال نیست!", show_alert=True)
            return
        current_uid = g["players"][g["turn"]]
        if user.id != current_uid:
            await query.answer("نوبت شما نیست!", show_alert=True)
            return
        if g.get("current_q", {}).get("answered"):
            await query.answer("قبلاً جواب دادی!", show_alert=True)
            return
        parts = data.split("_")
        try:
            cat = parts[2]
            q_idx = int(parts[3])
            ans_idx = int(parts[4])
        except Exception:
            await query.answer("خطا!", show_alert=True)
            return
        q = QUESTIONS.get(cat, [])[q_idx]
        q_text, options, correct = q
        g["current_q"]["answered"] = True
        current_name = g["names"].get(current_uid, "کاربر")
        if ans_idx == correct:
            g["scores"][current_uid] = g["scores"].get(current_uid, 0) + 1
            result = "✅ آفرین " + current_name + "! درست بود. (+1 امتیاز)"
        else:
            result = "❌ متأسفانه غلط بود. جواب درست: " + options[correct]
        await query.answer("درست!" if ans_idx == correct else "غلط!")
        # پیام نتیجه
        for mid in g.get("sent_msgs", []):
            try:
                await context.bot.delete_message(chat_id=chat.id, message_id=mid)
            except Exception:
                pass
        g["sent_msgs"] = []
        try:
            sent = await context.bot.send_message(chat_id=chat.id, text=result, reply_markup=quiz_game_kb(chat.id))
            g["sent_msgs"].append(sent.message_id)
        except Exception as e:
            print("[QUIZ ANS ERR] " + str(e))
        # نفر بعدی
        g["turn"] = (g["turn"] + 1) % len(g["players"])
        return

    # ۶. امتیازها
    if data == "qz_scores":
        g = QUIZ_GAME.get(chat.id)
        if not g or not g.get("scores"):
            await query.answer("هنوز امتیازی ثبت نشده!", show_alert=True)
            return
        await query.answer()
        sorted_scores = sorted(g["scores"].items(), key=lambda x: -x[1])
        text = "🏆 امتیازها" + NL + "━━━━━━━━━━━━━━━━" + NL + NL
        for i, (uid, sc) in enumerate(sorted_scores, 1):
            name = g["names"].get(uid, "کاربر")
            text += str(i) + ". " + name + " — " + str(sc) + " امتیاز" + NL
        try:
            sent = await context.bot.send_message(chat_id=chat.id, text=text, reply_markup=quiz_game_kb(chat.id))
            g.setdefault("sent_msgs", []).append(sent.message_id)
        except Exception:
            pass
        return

    # ۷. لیست شرکت‌کننده‌ها
    if data == "qz_list":
        g = QUIZ_GAME.get(chat.id)
        if not g or not g.get("players"):
            await query.answer("هنوز کسی شرکت نکرده!", show_alert=True)
            return
        await query.answer()
        names = [g["names"].get(p, "کاربر") for p in g["players"]]
        text = "👥 شرکت‌کننده‌ها (" + str(len(names)) + "):" + NL + NL
        for i, n in enumerate(names, 1):
            text += str(i) + ". " + n + NL
        try:
            await query.edit_message_text(text, reply_markup=quiz_main_menu(chat.id))
        except Exception:
            pass
        return

    # ۸. پایان بازی
    if data == "qz_end":
        g = QUIZ_GAME.get(chat.id)
        if g and g.get("starter_id") and user.id != g.get("starter_id"):
            await query.answer("فقط سازنده بازی می‌تونه تموم کنه!", show_alert=True)
            return
        # پاک کردن همه پیام‌های بازی
        for mid in g.get("sent_msgs", []) if g else []:
            try:
                await context.bot.delete_message(chat_id=chat.id, message_id=mid)
            except Exception:
                pass
        # امتیاز نهایی
        final_text = "🛑 بازی تموم شد."
        if g and g.get("scores"):
            sorted_scores = sorted(g["scores"].items(), key=lambda x: -x[1])
            final_text += NL + NL + "🏆 امتیاز نهایی:" + NL
            for i, (uid, sc) in enumerate(sorted_scores, 1):
                final_text += str(i) + ". " + g["names"].get(uid, "?") + " — " + str(sc) + NL
        try:
            await query.message.delete()
        except Exception:
            pass
        QUIZ_GAME.pop(chat.id, None)
        await query.answer("بازی تموم شد")
        try:
            await context.bot.send_message(chat_id=chat.id, text=final_text)
        except Exception:
            pass
        return

    # ۹. بستن
    if data == "qz_close":
        g = QUIZ_GAME.get(chat.id)
        if g and g.get("starter_id") and user.id != g.get("starter_id"):
            await query.answer("فقط سازنده بازی می‌تونه ببنده!", show_alert=True)
            return
        try:
            await query.message.delete()
        except Exception:
            pass
        QUIZ_GAME.pop(chat.id, None)
        await query.answer()
        return

    await query.answer()


def register(app):
    app.add_handler(MessageHandler(filters.Regex(r"^(کوییز|کوئیز|quiz)$"), quiz_text_handler), group=5)
    app.add_handler(CallbackQueryHandler(quiz_callback, pattern="^(qz_)"), group=5)
