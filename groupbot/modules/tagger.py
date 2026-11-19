import turso_db as sqlite3
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import MessageHandler, filters, ContextTypes, CallbackQueryHandler
from config import DATABASE_PATH

NL = chr(10)

# ذخیره اینکه هر کاربر روی کدوم پیام ریپلای کرده
REPLY_CACHE = {}


def tag_menu(uid):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("تگ ادمین ها", callback_data="tag_admins:" + str(uid))],
        [InlineKeyboardButton("تگ اعضای فعال", callback_data="tag_active:" + str(uid))],
        [InlineKeyboardButton("تگ همه اعضا", callback_data="tag_all:" + str(uid))],
        [InlineKeyboardButton("تگ تصادفی (۱۰ نفر)", callback_data="tag_random:" + str(uid))],
        [InlineKeyboardButton("بستن", callback_data="tag_close:" + str(uid))],
    ])


def get_db_members(chat_id):
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        c.execute("SELECT user_id, first_name FROM members WHERE chat_id = ?", (chat_id,))
        rows = c.fetchall()
        conn.close()
        return rows
    except Exception as e:
        print("[TAG DB ERR] " + str(e))
        return []


async def is_admin(chat, user_id):
    try:
        member = await chat.get_member(user_id)
        return member.status in ("administrator", "creator")
    except Exception as e:
        print("[TAG ADMIN ERR] " + str(e))
        return False


def mention(user_id, name):
    return "[" + (name or "user") + "](tg://user?id=" + str(user_id) + ")"


async def send_tags(msg, mentions, reply_to_id=None):
    if not mentions:
        await msg.reply_text("هنوز عضوی توی دیتابیس نیست")
        return
    batch_size = 25
    total = len(mentions)
    for i in range(0, total, batch_size):
        batch = mentions[i:i + batch_size]
        text = " ".join(batch)
        sent = False
        if reply_to_id:
            try:
                await msg.reply_text(
                    text,
                    parse_mode="Markdown",
                    reply_to_message_id=reply_to_id,
                    allow_sending_without_reply=True
                )
                sent = True
            except Exception as e:
                print("[TAG REPLY ERR] " + str(e))
        if not sent:
            try:
                await msg.reply_text(text, parse_mode="Markdown")
            except Exception as e:
                print("[TAG SEND ERR] " + str(e))


async def do_admins(msg, context, chat_id, reply_to_id=None):
    try:
        admins = await context.bot.get_chat_administrators(chat_id)
        mentions = [mention(a.user.id, a.user.first_name) for a in admins if a.user.id != context.bot.id]
        await send_tags(msg, mentions, reply_to_id)
    except Exception as e:
        await msg.reply_text("خطا: " + str(e))


async def do_all(msg, chat_id, reply_to_id=None):
    members = get_db_members(chat_id)
    if not members:
        await msg.reply_text("هنوز عضوی توی دیتابیس نیست")
        return
    mentions = [mention(m[0], m[1]) for m in members]
    await send_tags(msg, mentions, reply_to_id)


async def do_random(msg, chat_id, reply_to_id=None):
    members = get_db_members(chat_id)
    if not members:
        await msg.reply_text("هنوز عضوی توی دیتابیس نیست")
        return
    count = min(10, len(members))
    picked = random.sample(members, count)
    mentions = [mention(m[0], m[1]) for m in picked]
    await send_tags(msg, mentions, reply_to_id)


async def reply_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    if not msg or not chat or not user:
        return
    if chat.type not in ("group", "supergroup"):
        return

    text = (msg.text or "").strip()
    if not text:
        return

    print("[TAGGER] got: " + text)

    admin = await is_admin(chat, user.id)
    if not admin:
        return

    # فقط کلمه "تگ" → منو
    if text.strip() in ("تگ", "tag") or text.lower() in ("tag all",):
        # اگه ریپلای داره، آیدی رو ذخیره کن
        if msg.reply_to_message:
            REPLY_CACHE[user.id] = msg.reply_to_message.message_id
            print("[TAGGER] cached reply_to=" + str(msg.reply_to_message.message_id))
        else:
            REPLY_CACHE.pop(user.id, None)
        try:
            await msg.reply_text("یه گزینه رو انتخاب کن:", reply_markup=tag_menu(user.id))
            print("[TAGGER] menu sent")
        except Exception as e:
            print("[TAG MENU ERR] " + str(e))
        return

    # متن مستقیم
    reply_to_id = msg.reply_to_message.message_id if msg.reply_to_message else None

    if "تگ ادمین" in text or "تگ مدیر" in text:
        await do_admins(msg, context, chat.id, reply_to_id)
        return

    if "تگ فعال" in text:
        await do_all(msg, chat.id, reply_to_id)
        return

    if "تگ همه" in text or "تگ کل" in text or "تگ گروه" in text:
        await do_all(msg, chat.id, reply_to_id)
        return

    if "تگ تصادفی" in text or "تگ رندوم" in text:
        await do_random(msg, chat.id, reply_to_id)
        return


async def cb_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    clicker = query.from_user.id

    parts = data.split(":")
    action = parts[0]
    owner = int(parts[1]) if len(parts) > 1 else clicker

    if clicker != owner:
        await query.answer("این منو برای شما نیست", show_alert=True)
        return

    await query.answer()
    chat_id = query.message.chat_id

    # از cache بخون
    reply_to_id = REPLY_CACHE.get(clicker)
    print("[TAG CB] " + action + " reply_to=" + str(reply_to_id))

    if action == "tag_close":
        REPLY_CACHE.pop(clicker, None)
        try:
            await query.message.delete()
        except Exception:
            pass
        return

    if action == "tag_admins":
        await do_admins(query.message, context, chat_id, reply_to_id)
        return

    if action == "tag_active":
        await do_all(query.message, chat_id, reply_to_id)
        return

    if action == "tag_all":
        await do_all(query.message, chat_id, reply_to_id)
        return

    if action == "tag_random":
        await do_random(query.message, chat_id, reply_to_id)
        return


def register(app):
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_handler, block=False), group=10)
    app.add_handler(CallbackQueryHandler(cb_handler, pattern="^tag_"))
