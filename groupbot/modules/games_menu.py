from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler, MessageHandler, filters

NL = chr(10)

TRIGGERS = ["بازی", "بازی ها", "بازی‌ها", "games"]


def games_menu_kb(uid, chat_id):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎲 بازی‌های شانسی", callback_data="gm_dice:" + str(uid) + ":" + str(chat_id))],
        [InlineKeyboardButton("🪙 بازی‌های ساده", callback_data="gm_simple:" + str(uid) + ":" + str(chat_id))],
        [InlineKeyboardButton("🎭 جرئت یا حقیقت", callback_data="gm_td:" + str(uid) + ":" + str(chat_id))],
        [InlineKeyboardButton("🎯 چالش", callback_data="gm_ch:" + str(uid) + ":" + str(chat_id))],
        [InlineKeyboardButton("🎓 کوییز", callback_data="gm_quiz:" + str(uid) + ":" + str(chat_id))],
            [InlineKeyboardButton("🕵️ مایک بسته", callback_data="gm_mock:" + str(uid) + ":" + str(chat_id))],
[InlineKeyboardButton("❌ بستن", callback_data="gm_close:" + str(uid) + ":" + str(chat_id))],
    ])


async def games_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    if not msg or not chat or not user or not msg.text:
        return
    if chat.type not in ("group", "supergroup"):
        return
    if msg.text.strip().lower() not in [t.lower() for t in TRIGGERS]:
        return

    # چک فعال بودن بازی
    try:
        from database import get_setting, is_group_owner, is_bot_admin
        from config import OWNER_ID
        games_on = get_setting(chat.id, "games_enabled", "1") == "1"
        if not games_on:
            # فقط مالک، سازنده، ادمین ربات بتونن
            allowed = (user.id == OWNER_ID or is_bot_admin(user.id) or is_group_owner(chat.id, user.id))
            if not allowed:
                await msg.reply_text("🎮 بازی‌ها در این گروه غیرفعاله.")
                return
    except Exception as e:
        print("[GAMES ENABLED CHK ERR] " + str(e))

    # چک اجبار به جوین کانال بازی
    try:
        from database import get_force_joins, is_user_verified, set_user_verified
        joins = [j for j in get_force_joins(chat.id) if j[1] == "game_channel"]
        if joins and not is_user_verified(chat.id, user.id):
            missing = []
            kb_rows = []
            for j in joins:
                fid, ftype, tid, tlink, tname = j
                link = tlink if tlink.startswith("http") else "https://t.me/" + tlink.replace("@", "")
                is_member = False
                try:
                    m = await context.bot.get_chat_member(tid, user.id)
                    if m.status not in ("left", "kicked"):
                        is_member = True
                except Exception as e:
                    print("[GAME JOIN CHK ERR] " + str(e))
                if not is_member:
                    missing.append(tname or tlink)
                    kb_rows.append([InlineKeyboardButton("📢 " + (tname or tlink), url=link)])
            if missing:
                kb_rows.append([InlineKeyboardButton("✅ عضو شدم، بررسی کن", callback_data="gm_check:" + str(user.id) + ":" + str(chat.id))])
                kb_rows.append([InlineKeyboardButton("❌ بستن", callback_data="gm_close:" + str(user.id) + ":" + str(chat.id))])
                await msg.reply_text(
                    "🎮 برای دسترسی به بازی‌ها، ابتدا باید در کانال‌های زیر عضو شوید:" + NL + NL +
                    "پس از عضویت، روی «✅ عضو شدم» بزنید.",
                    reply_markup=InlineKeyboardMarkup(kb_rows)
                )
                return
            else:
                set_user_verified(chat.id, user.id, method="game_join")
    except Exception as e:
        print("[GAME JOIN CHECK ERR] " + str(e))

    await msg.reply_text(
        "🎮 بازی‌ها" + NL + "━━━━━━━━━━━━━━━━" + NL + NL +
        "یکی از دسته‌های زیر رو انتخاب کن:",
        reply_markup=games_menu_kb(user.id, chat.id)
    )


async def games_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    user = query.from_user
    chat = query.message.chat
    parts = data.split(":")
    action = parts[0]
    uid = int(parts[1]) if len(parts) > 1 else user.id
    chat_id = int(parts[2]) if len(parts) > 2 else 0

    if action == "gm_close":
        try:
            await query.message.delete()
        except Exception:
            pass
        await query.answer()
        return

    if action == "gm_check":
        await query.answer("در حال بررسی...")
        try:
            from database import get_force_joins, set_user_verified
            joins = [j for j in get_force_joins(chat_id) if j[1] == "game_channel"]
            missing = []
            for j in joins:
                fid, ftype, tid, tlink, tname = j
                try:
                    m = await context.bot.get_chat_member(tid, user.id)
                    if m.status in ("left", "kicked"):
                        missing.append(tname or tlink)
                except Exception:
                    missing.append(tname or tlink)
            if missing:
                await query.answer("هنوز عضو نشدی!", show_alert=True)
                return
            set_user_verified(chat_id, user.id, method="game_join")
            try:
                await query.edit_message_text(
                    "🎮 بازی‌ها" + NL + "━━━━━━━━━━━━━━━━" + NL + NL +
                    "یکی از دسته‌های زیر رو انتخاب کن:",
                    reply_markup=games_menu_kb(uid, chat_id)
                )
            except Exception:
                pass
        except Exception as e:
            print("[GM CHECK ERR] " + str(e))
        return

    await query.answer()

    if action == "gm_dice":
        try:
            await query.edit_message_text(
                "🎲 بازی‌های شانسی" + NL + "━━━━━━━━━━━━━━━━" + NL + NL +
                "کافیه یکی از این کلمات رو توی گروه بنویسی:" + NL + NL +
                "• تاس" + NL + "• دارت" + NL + "• بولینگ" + NL +
                "• بسکتبال" + NL + "• فوتبال" + NL + "• اسلات" + NL + NL +
                "ربات انیمیشن می‌فرسته و عدد نشون می‌ده.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 بازگشت", callback_data="gm_back:" + str(uid) + ":" + str(chat_id))],
                ])
            )
        except Exception:
            pass
        return

    if action == "gm_simple":
        try:
            await query.edit_message_text(
                "🪙 بازی‌های ساده" + NL + "━━━━━━━━━━━━━━━━" + NL + NL +
                "کافیه یکی از این کلمات رو توی گروه بنویسی:" + NL + NL +
                "• شیر یا خط" + NL +
                "• سنگ کاغذ قیچی (با دکمه)" + NL +
                "• حدس عدد (بعدش «حدس ۵۰»)" + NL +
                "• قرعه‌کشی (با ریپلای)",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 بازگشت", callback_data="gm_back:" + str(uid) + ":" + str(chat_id))],
                ])
            )
        except Exception:
            pass
        return

    if action == "gm_td":
        try:
            await query.edit_message_text(
                "🎭 جرئت یا حقیقت" + NL + "━━━━━━━━━━━━━━━━" + NL + NL +
                "کلمه «جرئت یا حقیقت» رو توی گروه بزن." + NL +
                "بعدش ۲+ نفر «شرکت کردن» بزنن و استارت‌کننده بازی رو شروع کنه." + NL + NL +
                "حالت +18 هم با دکمه «⚙️ حالت» قابل فعال‌سازیه.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 بازگشت", callback_data="gm_back:" + str(uid) + ":" + str(chat_id))],
                ])
            )
        except Exception:
            pass
        return

    if action == "gm_ch":
        try:
            await query.edit_message_text(
                "🎯 چالش" + NL + "━━━━━━━━━━━━━━━━" + NL + NL +
                "کلمه «چالش» رو توی گروه بزن." + NL +
                "می‌تونی چالش تصادفی بگیری یا لیست ۵ چالش.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 بازگشت", callback_data="gm_back:" + str(uid) + ":" + str(chat_id))],
                ])
            )
        except Exception:
            pass
        return

    if action == "gm_quiz":
        try:
            await query.edit_message_text(
                "🎓 کوییز اطلاعات عمومی" + NL + "━━━━━━━━━━━━━━━━" + NL + NL +
                "کلمه «کوییز» رو توی گروه بزن." + NL +
                "بعد از شرکت ۲+ نفر، استارت‌کننده بازی رو شروع کنه." + NL + NL +
                "دسته‌ها: عمومی، تاریخ، ورزش، سینما، علمی، جغرافیا",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 بازگشت", callback_data="gm_back:" + str(uid) + ":" + str(chat_id))],
                ])
            )
        except Exception:
            pass
        return

    if action == "gm_mock":
        try:
            from modules.mock import MOCK_GAME
            g = MOCK_GAME.get(chat_id)
            if g and g.get("active"):
                await query.answer("⚠️ یک بازی دیگر در جریان است!", show_alert=True)
                return
            MOCK_GAME[chat_id] = {
                "god_id": user.id,
                "active": False,
                "pinned_msg_id": 0,
                "mode": "normal",
                "used_qs": [],
                "current_q": None
            }
            await query.answer()
            await query.edit_message_text(
                "🕵️‍♂️ بازی مایک بسته" + NL +
                "━━━━━━━━━━━━━━" + NL + NL +
                "برای شروع بازی، روی دکمه زیر بزنید:",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("▶️ شروع بازی", callback_data="mk_start:" + str(user.id))],
                    [InlineKeyboardButton("❌ بستن", callback_data="gm_close:" + str(uid) + ":" + str(chat_id))]
                ])
            )
        except Exception as e:
            print("[GM MOCK ERR] " + str(e))
        return

    if action == "gm_back":
        try:
            await query.edit_message_text(
                "🎮 بازی‌ها" + NL + "━━━━━━━━━━━━━━━━" + NL + NL +
                "یکی از دسته‌های زیر رو انتخاب کن:",
                reply_markup=games_menu_kb(uid, chat_id)
            )
        except Exception:
            pass
        return


def register(app):
    app.add_handler(MessageHandler(filters.Regex(r"^(بازی|بازی ها|بازی‌ها|games)$"), games_menu_handler), group=4)
    app.add_handler(CallbackQueryHandler(games_menu_callback, pattern="^(gm_)"), group=4)
