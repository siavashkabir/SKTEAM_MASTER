import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, MessageHandler, CallbackQueryHandler, filters

NL = chr(10)

DICE_GAMES = {
    "تاس": "🎲", "dice": "🎲",
    "دارت": "🎯", "dart": "🎯",
    "بولینگ": "🎳", "bowling": "🎳",
    "بسکتبال": "🏀", "basketball": "🏀",
    "فوتبال": "⚽", "football": "⚽",
    "اسلات": "🎰", "slot": "🎰",
}

GUESS_STATE = {}
COIN_TRIGGERS = ["شیر یا خط", "سکه", "coin"]
RPS_TRIGGERS = ["سنگ کاغذ قیچی", "rps"]
GUESS_TRIGGERS = ["حدس عدد", "guess"]
LOTTERY_TRIGGERS = ["قرعه‌کشی", "قرعه کشی", "lottery"]

RPS_EMOJI = {"rock": "🪨", "paper": "📄", "scissors": "✂️"}
RPS_FA = {"rock": "سنگ", "paper": "کاغذ", "scissors": "قیچی"}


def rps_menu_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🪨 سنگ", callback_data="rps_rock"),
         InlineKeyboardButton("📄 کاغذ", callback_data="rps_paper"),
         InlineKeyboardButton("✂️ قیچی", callback_data="rps_scissors")],
    ])


async def games_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    if msg and msg.text:
        print("[GAMES DEBUG] got: " + msg.text.strip())
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
    text = msg.text.strip()
    text_low = text.lower()

    # ۱. بازی‌های شانسی
    for trigger, emoji in DICE_GAMES.items():
        if text_low == trigger.lower():
            try:
                await context.bot.send_dice(chat_id=chat.id, emoji=emoji)
            except Exception as e:
                print("[DICE ERR] " + str(e))
            return

    # ۲. شیر یا خط
    if text_low in [t.lower() for t in COIN_TRIGGERS]:
        result = random.choice(["🦁 شیر", "📝 خط"])
        await msg.reply_text("🪙 سکه انداخته شد..." + NL + NL + "نتیجه: " + result)
        return

    # ۳. سنگ کاغذ قیچی
    if text_low in [t.lower() for t in RPS_TRIGGERS]:
        await msg.reply_text(
            "🎮 سنگ کاغذ قیچی!" + NL + NL + "انتخاب کن:",
            reply_markup=rps_menu_kb()
        )
        return

    # ۴. حدس عدد - شروع
    if text_low in [t.lower() for t in GUESS_TRIGGERS]:
        num = random.randint(1, 100)
        GUESS_STATE[(chat.id, user.id)] = num
        await msg.reply_text(
            "🎯 بازی حدس عدد شروع شد!" + NL + NL +
            "یه عدد بین ۱ تا ۱۰۰ انتخاب کردم. حدس بزن!" + NL +
            "برای حدس، بنویس: `حدس ۵۰`",
            parse_mode="Markdown"
        )
        return

    # ۵. حدس عدد - چک
    if text_low.startswith("حدس "):
        if (chat.id, user.id) not in GUESS_STATE:
            await msg.reply_text("❌ اول با «حدس عدد» بازی رو شروع کن.")
            return
        try:
            guess = int(text.split(" ", 1)[1].strip())
        except Exception:
            return
        target = GUESS_STATE[(chat.id, user.id)]
        if guess == target:
            await msg.reply_text("🎉 آفرین! درست حدس زدی. عدد " + str(target) + " بود!")
            GUESS_STATE.pop((chat.id, user.id), None)
        elif guess < target:
            await msg.reply_text("⬆️ بالاتر! عدد بزرگ‌تره.")
        else:
            await msg.reply_text("⬇️ پایین‌تر! عدد کوچیک‌تره.")
        return

    # ۶. قرعه‌کشی
    if text_low in [t.lower() for t in LOTTERY_TRIGGERS]:
        if not msg.reply_to_message:
            await msg.reply_text("❌ روی پیام یه نفر ریپلای بزن و بنویس «قرعه‌کشی».")
            return
        target = msg.reply_to_message.from_user
        if target:
            await msg.reply_text("🎉 قرعه‌کشی: برنده " + (target.first_name or "کاربر") + " هست!")
        return


async def rps_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    await query.answer()
    if not data.startswith("rps_"):
        return
    user_choice = data.replace("rps_", "")
    bot_choice = random.choice(["rock", "paper", "scissors"])
    if user_choice == bot_choice:
        result = "🤝 مساوی!"
    elif (user_choice == "rock" and bot_choice == "scissors") or \
         (user_choice == "paper" and bot_choice == "rock") or \
         (user_choice == "scissors" and bot_choice == "paper"):
        result = "🎉 تو بردی!"
    else:
        result = "😢 من بردم!"
    text = (
        "🎮 سنگ کاغذ قیچی" + NL + "━━━━━━━━━━━━━━━━" + NL +
        "👤 تو: " + RPS_EMOJI[user_choice] + " " + RPS_FA[user_choice] + NL +
        "🤖 ربات: " + RPS_EMOJI[bot_choice] + " " + RPS_FA[bot_choice] + NL + NL +
        result
    )
    try:
        await query.edit_message_text(text, reply_markup=rps_menu_kb())
    except Exception as e:
        print("[RPS ERR] " + str(e))


def register(app):
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, games_text_handler), group=6)
    app.add_handler(CallbackQueryHandler(rps_callback, pattern="^rps_"), group=6)
