import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, MessageHandler, CallbackQueryHandler, filters

NL = chr(10)

TRIGGERS = ["مایک", "مایک بسته", "مایک‌بسته", "mock"]

MOCK_GAME = {}

# ============ سوالات عادی (200 سوال) ============
from modules.mock_questions import MOCK_QUESTIONS, MOCK_ADULT


def mock_start_kb(uid):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("▶️ شروع بازی (فقط استارت‌کننده)", callback_data="mk_start:" + str(uid))],
        [InlineKeyboardButton("❌ بستن", callback_data="mk_close:" + str(uid))],
    ])


def mock_category_kb(uid):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔒 سوالات عادی", callback_data="mk_cat_normal:" + str(uid))],
        [InlineKeyboardButton("🔞 سوالات +18", callback_data="mk_cat_adult:" + str(uid))],
        [InlineKeyboardButton("🎲 مخلوط", callback_data="mk_cat_mix:" + str(uid))],
    ])


def mock_control_kb(uid):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➡️ سوال بعدی", callback_data="mk_next:" + str(uid)),
         InlineKeyboardButton("⏭️ رد کردن", callback_data="mk_skip:" + str(uid))],
        [InlineKeyboardButton("🎚️ تغییر نوع سوال", callback_data="mk_change:" + str(uid))],
        [InlineKeyboardButton("🛑 پایان بازی", callback_data="mk_end:" + str(uid))],
    ])


def mock_change_kb(uid):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔒 عادی", callback_data="mk_switch_normal:" + str(uid))],
        [InlineKeyboardButton("🔞 +18", callback_data="mk_switch_adult:" + str(uid))],
        [InlineKeyboardButton("🎲 مخلوط", callback_data="mk_switch_mix:" + str(uid))],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="mk_back_game:" + str(uid))],
    ])




def mock_location_kb(uid):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👥 نمایش در گروه", callback_data="mk_loc_group:" + str(uid))],
        [InlineKeyboardButton("📩 نمایش در پیوی گاد", callback_data="mk_loc_pv:" + str(uid))],
    ])


def _pick_question(g):
    mode = g.get("mode", "normal")
    if mode == "normal":
        pool = MOCK_QUESTIONS
    elif mode == "adult":
        pool = MOCK_ADULT
    else:
        pool = MOCK_QUESTIONS + MOCK_ADULT
    used = g.get("used_qs", [])
    available = [i for i in range(len(pool)) if i not in used]
    if not available:
        used = []
        available = list(range(len(pool)))
    idx = random.choice(available)
    used.append(idx)
    g["used_qs"] = used
    return pool[idx]


def _make_question_text(g, question, god_name):
    mode = g.get("mode", "normal")
    mode_label = "🔒 عادی" if mode == "normal" else "🔞 +18" if mode == "adult" else "🎲 مخلوط"
    return (
        "🎮 مایک بسته" + NL +
        "━━━━━━━━━━━━━━━━" + NL +
        "👤 گاد: " + god_name + NL +
        "📚 نوع سوال: " + mode_label + NL +
        "━━━━━━━━━━━━━━━━" + NL + NL +
        "📌 سوال:" + NL + NL +
        "« " + question + " »" + NL + NL +
        "🎙️ گاد سوال رو توی ویس‌کال می‌خونه." + NL +
        "🎤 بقیه توی ویس‌کال جواب می‌دن." + NL + NL +
        "👇 کنترل‌ها (فقط گاد):"
    )


async def mock_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    if not msg or not chat or not user or not msg.text:
        return
    if chat.type not in ("group", "supergroup"):
        return
    try:
        from database import get_setting
        if get_setting(chat.id, "games_enabled", "1") != "1":
            return
    except Exception:
        pass
    if msg.text.strip().lower() not in [t.lower() for t in TRIGGERS]:
        return
    g = MOCK_GAME.get(chat.id)
    if g and g.get("active"):
        await msg.reply_text("⚠️ یه بازی در جریانه.")
        return
    MOCK_GAME[chat.id] = {
        "god_id": user.id, "active": False,
        "pinned_msg_id": 0, "mode": "normal",
        "used_qs": [], "current_q": None,
    }
    await msg.reply_text(
        "🎮 مایک بسته" + NL +
        "━━━━━━━━━━━━━━━━" + NL + NL +
        "📌 یه نفر «گاد» میشه که سوالات رو توی ویس‌کال می‌خونه." + NL +
        "📌 سوال بالای گروه پین میشه و دکمه‌ها زیرش نمایش داده میشه." + NL +
        "📌 فقط گاد می‌تونه سوال بعدی یا رد کنه." + NL + NL +
        "👤 گاد این بازی: " + (user.first_name or "کاربر") + NL + NL +
        "👇 برای شروع، روی دکمه زیر بزن:",
        reply_markup=mock_start_kb(user.id)
    )


async def mock_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    user = query.from_user
    actual_chat = query.message.chat
    # اگه توی پیوی هستیم، گروه بازی رو پیدا کن
    if actual_chat.type == "private":
        game_chat_id = None
        for cid, gm in MOCK_GAME.items():
            if gm.get("god_id") == user.id:
                game_chat_id = cid
                break
        if not game_chat_id:
            await query.answer("بازی فعالی پیدا نشد!", show_alert=True)
            return
        class _FakeChat:
            pass
        chat = _FakeChat()
        chat.id = game_chat_id
        chat.type = "supergroup"
    else:
        chat = actual_chat
    parts = data.split(":")
    action = parts[0]

    if action == "mk_close":
        g = MOCK_GAME.get(chat.id)
        if g and g.get("god_id") and user.id != g.get("god_id"):
            await query.answer("فقط گاد می‌تونه ببنده!", show_alert=True)
            return
        try:
            await query.message.delete()
        except Exception:
            pass
        MOCK_GAME.pop(chat.id, None)
        await query.answer()
        return

    if action == "mk_start":
        g = MOCK_GAME.get(chat.id)
        if not g:
            await query.answer("اول «مایک بسته» رو بزن!", show_alert=True)
            return
        if g.get("active"):
            await query.answer("شروع شده!", show_alert=True)
            return
        if user.id != g.get("god_id"):
            await query.answer("فقط استارت‌کننده می‌تونه شروع کنه!", show_alert=True)
            return
        await query.answer()
        try:
            await query.edit_message_text(
                "🎮 محل نمایش سوالات رو انتخاب کن:" + NL + NL +
                "👤 گاد: " + (user.first_name or "کاربر") + NL + NL +
                "👥 گروه: سوال توی گروه پین میشه، همه می‌بینن" + NL +
                "📩 پیوی گاد: سوال فقط به پیوی گاد میره، توی گروه پین نمیشه",
                reply_markup=mock_location_kb(user.id)
            )
        except Exception:
            pass
        return
        if g.get("active"):
            await query.answer("شروع شده!", show_alert=True)
            return
        if user.id != g.get("god_id"):
            await query.answer("فقط استارت‌کننده می‌تونه شروع کنه!", show_alert=True)
            return
        await query.answer()
        try:
            await query.edit_message_text(
                "🎮 نوع سوالات رو انتخاب کن:" + NL + NL +
                "👤 گاد: " + (user.first_name or "کاربر"),
                reply_markup=mock_category_kb(user.id)
            )
        except Exception:
            pass
        return

    if action.startswith("mk_cat_"):
        g = MOCK_GAME.get(chat.id)
        if not g:
            await query.answer()
            return
        if user.id != g.get("god_id"):
            await query.answer("فقط گاد!", show_alert=True)
            return
        mode = action.replace("mk_cat_", "")
        if mode not in ("normal", "adult", "mix"):
            await query.answer("نامعتبر", show_alert=True)
            return
        g["mode"] = mode
        g["used_qs"] = []
        g["active"] = True
        await query.answer()
        loc = g.get("display_in", "group")
        god_name = user.first_name or "کاربر"
        q = _pick_question(g)
        g["current_q"] = q
        text = _make_question_text(g, q, god_name)
        if loc == "group":
            try:
                await query.edit_message_text(text, reply_markup=mock_control_kb(user.id))
                try:
                    await context.bot.pin_chat_message(chat_id=chat.id, message_id=query.message.message_id, disable_notification=True)
                    g["pinned_msg_id"] = query.message.message_id
                except Exception as e:
                    print("[MOCK PIN ERR] " + str(e))
            except Exception as e:
                print("[MOCK GROUP ERR] " + str(e))
        else:
            try:
                await context.bot.send_message(chat_id=user.id, text=text, reply_markup=mock_control_kb(user.id))
            except Exception as e:
                print("[MOCK PV ERR] " + str(e))
            try:
                await query.edit_message_text(
                    "📩 سوالات به پیوی گاد (" + god_name + ") ارسال شد." + NL + NL +
                    "🎙️ گاد سوال رو توی ویس‌کال می‌خونه." + NL +
                    "🎤 بقیه توی ویس‌کال جواب می‌دن." + NL +
                    "👇 کنترل‌ها توی پیوی گاد مدیریت میشه."
                )
            except Exception:
                pass
        return
        if user.id != g.get("god_id"):
            await query.answer("فقط گاد!", show_alert=True)
            return
        mode = action.replace("mk_cat_", "")
        if mode not in ("normal", "adult", "mix"):
            await query.answer("نامعتبر", show_alert=True)
            return
        g["mode"] = mode
        g["used_qs"] = []
        g["active"] = True
        await query.answer()
        loc = g.get("display_in", "group")
        god_name = user.first_name or "کاربر"
        q = _pick_question(g)
        g["current_q"] = q
        text = _make_question_text(g, q, god_name)
        if loc == "group":
            try:
                await query.edit_message_text(text, reply_markup=mock_control_kb(user.id))
                try:
                    await context.bot.pin_chat_message(chat_id=chat.id, message_id=query.message.message_id, disable_notification=True)
                    g["pinned_msg_id"] = query.message.message_id
                except Exception as e:
                    print("[MOCK PIN ERR] " + str(e))
            except Exception as e:
                print("[MOCK GROUP ERR] " + str(e))
        else:
            # PV: به پیوی گاد بفرست، توی گروه پیام اطلاع بده
            try:
                await context.bot.send_message(chat_id=user.id, text=text, reply_markup=mock_control_kb(user.id))
            except Exception as e:
                print("[MOCK PV ERR] " + str(e))
            try:
                await query.edit_message_text(
                    "📩 سوالات به پیوی گاد (" + god_name + ") ارسال شد." + NL + NL +
                    "🎙️ گاد سوال رو توی ویس‌کال می‌خونه." + NL +
                    "🎤 بقیه توی ویس‌کال جواب می‌دن." + NL +
                    "👇 کنترل‌ها توی پیوی گاد مدیریت میشه."
                )
            except Exception:
                pass
        return
    
    # ====== انتخاب محل نمایش ======
    if action.startswith("mk_loc_"):
        g = MOCK_GAME.get(chat.id)
        if not g:
            await query.answer()
            return
        if user.id != g.get("god_id"):
            await query.answer("فقط گاد!", show_alert=True)
            return
        loc = action.replace("mk_loc_", "")
        if loc not in ("group", "pv"):
            await query.answer("نامعتبر", show_alert=True)
            return
        g["display_in"] = loc
        await query.answer()
        try:
            await query.edit_message_text(
                "🎮 نوع سوالات رو انتخاب کن:" + NL + NL +
                "👤 گاد: " + (user.first_name or "کاربر") + NL +
                "📍 محل نمایش: " + ("👥 گروه" if loc == "group" else "📩 پیوی گاد"),
                reply_markup=mock_category_kb(user.id)
            )
        except Exception as e:
            print("[MOCK LOC ERR] " + str(e))
        return
        if user.id != g.get("god_id"):
            await query.answer("فقط گاد!", show_alert=True)
            return
        loc = action.replace("mk_loc_", "")
        if loc not in ("group", "pv"):
            await query.answer("نامعتبر", show_alert=True)
            return
        g["display_in"] = loc
        await query.answer()
        # بعد از انتخاب محل → انتخاب نوع سوال
        try:
            await query.edit_message_text(
                "🎮 نوع سوالات رو انتخاب کن:" + NL + NL +
                "👤 گاد: " + (user.first_name or "کاربر") + NL +
                "📍 محل نمایش: " + ("👥 گروه" if loc == "group" else "📩 پیوی گاد"),
                reply_markup=mock_category_kb(user.id)
            )
        except Exception as e:
            print("[MOCK LOC ERR] " + str(e))
        return

    if action in ("mk_next", "mk_skip", "mk_end"):
        g = MOCK_GAME.get(chat.id)
        if not g or not g.get("active"):
            await query.answer("بازی فعال نیست!", show_alert=True)
            return
        if user.id != g.get("god_id"):
            await query.answer("فقط گاد (استارت‌کننده) می‌تونه کنترل کنه!", show_alert=True)
            return
        if action in ("mk_next", "mk_skip"):
            q = _pick_question(g)
            g["current_q"] = q
            god_name = user.first_name or "کاربر"
            text = _make_question_text(g, q, god_name)
            display_in = g.get("display_in", "group")
            if display_in == "pv":
                try:
                    await context.bot.send_message(chat_id=user.id, text=text, reply_markup=mock_control_kb(user.id))
                except Exception as e:
                    print("[MOCK PV NEXT ERR] " + str(e))
                await query.answer("✅ سوال جدید به پیوی ارسال شد")
                return
            try:
                await query.edit_message_text(text, reply_markup=mock_control_kb(user.id))
                try:
                    await context.bot.pin_chat_message(chat_id=chat.id, message_id=query.message.message_id, disable_notification=True)
                    g["pinned_msg_id"] = query.message.message_id
                except Exception as e:
                    print("[MOCK REPIN ERR] " + str(e))
            except Exception as e:
                print("[MOCK NEXT ERR] " + str(e))
            await query.answer("✅ سوال جدید")
            return
        if action == "mk_end":
            if g.get("pinned_msg_id"):
                try:
                    await context.bot.unpin_chat_message(chat_id=chat.id, message_id=g["pinned_msg_id"])
                except Exception:
                    pass
            try:
                await query.message.delete()
            except Exception:
                pass
            MOCK_GAME.pop(chat.id, None)
            await query.answer("بازی تموم شد")
            try:
                await context.bot.send_message(chat_id=chat.id, text="🛑 بازی مایک بسته تموم شد.")
            except Exception:
                pass
            return

    await query.answer()


def register(app):
    app.add_handler(MessageHandler(filters.Regex(r"^(مایک|مایک بسته|مایک‌بسته|mock)$"), mock_handler), group=4)
    app.add_handler(CallbackQueryHandler(mock_callback, pattern="^(mk_)"), group=4)
