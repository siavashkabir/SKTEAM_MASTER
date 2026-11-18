import os
import jdatetime
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display
from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters

NL = chr(10)

ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
FONT_REGULAR = os.path.join(ASSETS_DIR, "Vazirmatn-Regular.ttf")
FONT_BOLD = os.path.join(ASSETS_DIR, "Vazirmatn-Bold.ttf")

PERSIAN_MONTHS = ["فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
                   "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"]
PERSIAN_WEEKDAYS = ["ش", "ی", "د", "س", "چ", "پ", "ج"]
FA_DIGITS = "۰۱۲۳۴۵۶۷۸۹"


def _fa(text):
    try:
        return get_display(arabic_reshaper.reshape(text))
    except Exception:
        return text


def _fa_num(n):
    return "".join(FA_DIGITS[int(ch)] for ch in str(n))


def _get_days_in_month(year, month):
    if month <= 6:
        return 31
    if month <= 11:
        return 30
    try:
        jdatetime.date(year, 12, 30)
        return 30
    except Exception:
        return 29


def generate_calendar_image(year=None):
    if year is None:
        year = jdatetime.date.today().year

    W, H = 1400, 1900
    title_h = 120
    cell_w = W // 3
    cell_h = (H - title_h) // 4
    month_title_h = 50
    weekday_h = 40
    day_h = (cell_h - month_title_h - weekday_h - 30) // 6

    img = Image.new("RGB", (W, H), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    font_title = ImageFont.truetype(FONT_BOLD, 60)
    font_month = ImageFont.truetype(FONT_BOLD, 34)
    font_day = ImageFont.truetype(FONT_REGULAR, 24)
    font_weekday = ImageFont.truetype(FONT_BOLD, 22)

    # عنوان
    title_text = _fa("تقویم سال " + _fa_num(year))
    bbox = draw.textbbox((0, 0), title_text, font=font_title)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) // 2, 30), title_text, fill=(20, 20, 20), font=font_title)

    for m_idx in range(12):
        month = m_idx + 1
        col = m_idx % 3
        row = m_idx // 3
        x0 = col * cell_w + 20
        y0 = title_h + row * cell_h + 10
        x1 = x0 + cell_w - 40
        y1 = y0 + cell_h - 20

        draw.rectangle([x0, y0, x1, y1], outline=(180, 180, 180), width=2)

        # نام ماه
        m_text = _fa(PERSIAN_MONTHS[m_idx])
        bbox = draw.textbbox((0, 0), m_text, font=font_month)
        tw = bbox[2] - bbox[0]
        draw.text((x0 + (x1 - x0 - tw) // 2, y0 + 10), m_text,
                  fill=(200, 50, 50), font=font_month)

        # روزهای هفته
        cell_day_w = (x1 - x0) // 7
        wy = y0 + month_title_h + 5
        for wd_idx, wd in enumerate(PERSIAN_WEEKDAYS):
            cx = x1 - (wd_idx + 0.5) * cell_day_w
            wt = _fa(wd)
            bbox = draw.textbbox((0, 0), wt, font=font_weekday)
            tw = bbox[2] - bbox[0]
            draw.text((cx - tw / 2, wy), wt, fill=(50, 50, 50), font=font_weekday)

        # روزها
        first_day = jdatetime.date(year, month, 1)
        start_wd = first_day.weekday()  # 0=شنبه ... 6=جمعه
        days = _get_days_in_month(year, month)

        for d in range(1, days + 1):
            pos = start_wd + (d - 1)
            r = pos // 7
            c = pos % 7
            dx = x1 - (c + 0.5) * cell_day_w
            dy = wy + weekday_h + r * day_h

            day_text_fa = _fa_num(d)
            bbox = draw.textbbox((0, 0), day_text_fa, font=font_day)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
            draw.text((dx - tw / 2, dy + (day_h - th) / 2),
                      day_text_fa, fill=(0, 0, 0), font=font_day)

    tmp_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "tmp_calendar")
    os.makedirs(tmp_dir, exist_ok=True)
    path = os.path.join(tmp_dir, "calendar_" + str(year) + ".png")
    img.save(path)
    return path


async def calendar_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    chat = update.effective_chat
    if not msg or not chat:
        return
    if chat.type not in ("group", "supergroup"):
        return
    if not msg.text:
        return
    text = msg.text.strip()
    if text != "تقویم" and text.lower() != "calendar":
        return
    try:
        path = generate_calendar_image()
        with open(path, "rb") as f:
            await msg.reply_photo(photo=f, caption="📅 تقویم سال " + _fa_num(jdatetime.date.today().year))
        try:
            os.remove(path)
        except Exception:
            pass
    except Exception as e:
        print("[CALENDAR ERR] " + str(e))
        await msg.reply_text("❌ خطا در ساخت تقویم: " + str(e))


def register(app):
    app.add_handler(MessageHandler(filters.Regex(r"^(تقویم|calendar)$"), calendar_handler), group=5)
