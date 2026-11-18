"""تنظیمات per-group برای هر گروه - فقط Owner و Sudo"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from config import OWNER_ID
from database import (
    get_ai_setting, set_ai_setting,
    get_ai_setting, set_ai_setting,
    get_chat_cooldown, set_chat_cooldown,
    get_chat_panel_delete, set_chat_panel_delete,
    get_chat_panel_timeout, set_chat_panel_timeout,
    get_chat_expire_delete, set_chat_expire_delete,
    is_bot_admin
)


def _fmt_sec(s):
    try:
        s = int(s)
    except (ValueError, TypeError):
        return str(s)
    if s == 0:
        return "خاموش"
    if s < 60:
        return f"{s} ثانیه"
    m = s // 60
    return f"{m} دقیقه"




async def _safe_edit(query, text=None, reply_markup=None):
    """ویرایش پیام با هندل خطای flood"""
    try:
        if text is not None:
            await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")
        else:
            await query.edit_message_reply_markup(reply_markup=reply_markup)
        return True
    except Exception as e:
        err = str(e)
        if "Flood control exceeded" in err or "flood" in err.lower():
            # استخراج ثانیه‌ها
            import re
            m = re.search(r'Retry in (\d+) seconds', err)
            sec = m.group(1) if m else "چند"
            try:
                await query.answer(f"⏳ لطفاً {sec} ثانیه صبر کن", show_alert=True)
            except Exception:
                pass
        else:
            print("[SAFE EDIT ERR]", err)
        return False



def _build_timer_menu(uid, chat_id):
    """منوی متمرکز تنظیمات تایمر"""
    cd = get_chat_cooldown(chat_id)
    pd = get_chat_panel_delete(chat_id)
    pt = get_chat_panel_timeout(chat_id)
    ed = get_chat_expire_delete(chat_id)
    try:
        from database import get_chat_panel_warning
        warn = get_chat_panel_warning(chat_id)
    except Exception:
        warn = 0
    warn_icon = "✅" if warn == 1 else "❌"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"⏰ Cooldown: {_fmt_sec(cd)}", callback_data=f"owner_set_cd:{uid}:{chat_id}")],
        [InlineKeyboardButton(f"🗑 حذف پنل: {_fmt_sec(pd)}", callback_data=f"owner_set_del:{uid}:{chat_id}")],
        [InlineKeyboardButton(f"⏳ انقضای پنل: {_fmt_sec(pt)}", callback_data=f"owner_set_pt:{uid}:{chat_id}")],
        [InlineKeyboardButton(f"💬 حذف پیام expire: {_fmt_sec(ed)}", callback_data=f"owner_set_ed:{uid}:{chat_id}")],
        [InlineKeyboardButton(f"🔔 هشدار بسته شدن: {warn_icon}", callback_data=f"owner_set_warn:{uid}:{chat_id}")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data=f"timer_back:{uid}:{chat_id}")],
    ])


def _build_reports_menu(uid, chat_id):
    """زیرمنوی تنظیمات گزارش"""
    dl, cd = get_report_settings(chat_id)
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"📊 سهمیه روزانه: {dl}", callback_data=f"owner_rep_dl:{uid}:{chat_id}")],
        [InlineKeyboardButton(f"⏱ فاصله بین گزارش‌ها: {fmt_rep_cd(cd)}", callback_data=f"owner_rep_cd:{uid}:{chat_id}")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data=f"rep_settings_back:{uid}:{chat_id}")],
    ])


def _build_ai_menu(uid, chat_id):
    """زیرمنوی تنظیمات هوش مصنوعی"""
    cd = get_chat_cooldown(chat_id)
    ai_on = get_ai_setting(chat_id, "ai_enabled", "0") == "1"
    ai_p = get_ai_setting(chat_id, "ai_personality", "persian")
    ai_t = get_ai_setting(chat_id, "ai_trigger", "mention")
    ai_a = get_ai_setting(chat_id, "ai_adult", "0") == "1"

    ai_on_lbl = "✅ فعال" if ai_on else "❌ غیرفعال"
    p_labels = {"persian": "😐 نرمال", "formal": "🎩 رسمی", "funny": "😂 شوخ", "cool": "😎 خونسرد", "rude": "😈 خبیث"}
    t_labels = {"mention": "📢 فقط منشن", "30percent": "30% پیام‌ها", "50percent": "50% پیام‌ها", "always": "همه پیام‌ها"}

    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"🤖 پاسخ هوشمند: {ai_on_lbl}", callback_data=f"owner_set_ai_on:{uid}:{chat_id}")],
        [InlineKeyboardButton(f"😈 شخصیت: {p_labels.get(ai_p, '😐')}", callback_data=f"owner_set_ai_p:{uid}:{chat_id}")],
        [InlineKeyboardButton(f"🗣️ فرکانس: {t_labels.get(ai_t, 'متوسط')}", callback_data=f"owner_set_ai_t:{uid}:{chat_id}")],
        [InlineKeyboardButton(f"🔞 حالت بزرگسال: {'✅' if ai_a else '❌'}", callback_data=f"owner_set_ai_a:{uid}:{chat_id}")],
        [InlineKeyboardButton(f"💬 حذف جواب AI: {_fmt_sec(get_ai_setting(chat_id, 'ai_delete_seconds', get_ai_setting(0, 'sys_ai_delete_seconds', '0')))}", callback_data=f"owner_set_ai_del:{uid}:{chat_id}")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data=f"ai_back:{uid}:{chat_id}")],
    ])


def _build_menu(uid, chat_id):
    cd = get_chat_cooldown(chat_id)
    dl = get_chat_panel_delete(chat_id)
    pt = get_chat_panel_timeout(chat_id)
    ed = get_chat_expire_delete(chat_id)
    ai_on = get_ai_setting(chat_id, "ai_enabled", "0") == "1"
    ai_p = get_ai_setting(chat_id, "ai_personality", "persian")
    ai_t = get_ai_setting(chat_id, "ai_trigger", "mention")
    ai_a = get_ai_setting(chat_id, "ai_adult", "0") == "1"
    ai_on_lbl = "✅ فعال" if ai_on else "❌ غیرفعال"
    p_labels = {"persian": "😄 طنز", "formal": "🙂 مؤدب", "funny": "🤣 بامزه", "cool": "😎 خفن", "rude": "😈 خیلی خیلی خفن"}
    t_labels = {"mention": "فقط منشن/کلمه کلیدی", "30percent": "30% پیام‌ها", "50percent": "50% پیام‌ها", "always": "همه پیام‌ها"}
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⏱ تنظیمات تایمر", callback_data=f"timer_menu:{uid}:{chat_id}")],
        [InlineKeyboardButton("🗣️ AI", callback_data=f"ai_menu:{uid}:{chat_id}")],
        [InlineKeyboardButton("🛡 Anti-Raid", callback_data=f"raid_panel:{uid}:{chat_id}")],
        [InlineKeyboardButton("🤖 Anti-Bot", callback_data=f"abot_panel:{uid}:{chat_id}")],
        [InlineKeyboardButton("📊 تنظیمات گزارش", callback_data=f"rep_settings_menu:{uid}:{chat_id}")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data=f"owner_set_back:{uid}:{chat_id}")],
    ])


async def owner_set_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    data = query.data
    parts = data.split(":")
    action = parts[0]

    # دسترسی: Owner یا Sudo
    is_owner = user.id == OWNER_ID
    is_sudo = False
    try:
        is_sudo = is_bot_admin(user.id)
    except Exception:
        pass
    if not (is_owner or is_sudo):
        await query.answer("⛔ فقط سازنده یا سودو!", show_alert=True)
        return

    uid = user.id
    chat_id = 0
    try:
        if len(parts) > 2 and parts[2].lstrip('-').isdigit():
            chat_id = int(parts[2])
    except Exception:
        pass

    if query.message.chat.type == "private":
        chat_id = 0

    if action == "owner_set_group":
        try:
            await _safe_edit(query, "⚙️ *تنظیمات این گروه*\n\nاز دکمه‌ها استفاده کن:\n\n⚠️ فقط برای همین گروه اعمال می‌شه.", _build_menu(uid, chat_id))
        except Exception as e:
            print("[OWNER_SET_GROUP ERR]", str(e))
        await query.answer()
        return

    if action == "owner_set_ai_on":
        try:
            from database import get_ai_setting, set_ai_setting
            cur = get_ai_setting(chat_id, "ai_enabled", "0")
            new = "0" if cur == "1" else "1"
            set_ai_setting(chat_id, "ai_enabled", new)
            await _safe_edit(query, None, _build_ai_menu(uid, chat_id))
            await query.answer("✅ فعال شد" if new == "1" else "❌ غیرفعال شد")
        except Exception as e:
            print("[AI_ON ERR]", str(e))
            await query.answer("❌ خطا", show_alert=True)
        return

    if action == "owner_set_ai_p":
        try:
            from database import get_ai_setting, set_ai_setting
            opts = ["persian", "formal", "funny", "cool", "rude"]
            cur = get_ai_setting(chat_id, "ai_personality", "persian")
            try:
                i = opts.index(cur)
                new = opts[(i + 1) % len(opts)]
            except ValueError:
                new = "persian"
            set_ai_setting(chat_id, "ai_personality", new)
            await _safe_edit(query, None, _build_ai_menu(uid, chat_id))
            await query.answer("✅ شخصیت تغییر کرد")
        except Exception as e:
            print("[AI_P ERR]", str(e))
            await query.answer("❌ خطا", show_alert=True)
        return

    if action == "owner_set_ai_t":
        try:
            from database import get_ai_setting, set_ai_setting
            opts = ["mention", "30percent", "50percent", "always"]
            cur = get_ai_setting(chat_id, "ai_trigger", "mention")
            try:
                i = opts.index(cur)
                new = opts[(i + 1) % len(opts)]
            except ValueError:
                new = "mention"
            set_ai_setting(chat_id, "ai_trigger", new)
            await _safe_edit(query, None, _build_ai_menu(uid, chat_id))
            await query.answer("✅ فرکانس تغییر کرد")
        except Exception as e:
            print("[AI_T ERR]", str(e))
            await query.answer("❌ خطا", show_alert=True)
        return

    if action == "owner_set_ai_a":
        try:
            from database import get_ai_setting, set_ai_setting
            cur = get_ai_setting(chat_id, "ai_adult", "0")
            new = "0" if cur == "1" else "1"
            set_ai_setting(chat_id, "ai_adult", new)
            await _safe_edit(query, None, _build_ai_menu(uid, chat_id))
            await query.answer("✅ حالت بزرگسال" if new == "1" else "❌ غیرفعال")
        except Exception as e:
            print("[AI_A ERR]", str(e))
            await query.answer("❌ خطا", show_alert=True)
        return

    if action == "owner_set_ai_del":
        try:
            from database import get_chat_ai_delete, set_chat_ai_delete
            opts = [0, 30, 60, 120, 300, 600]
            cur = get_chat_ai_delete(chat_id)
            try:
                i = opts.index(cur)
                new = opts[(i + 1) % len(opts)]
            except ValueError:
                new = 0
            set_chat_ai_delete(chat_id, new)
            await _safe_edit(query, None, _build_ai_menu(uid, chat_id))
            lbl = "خاموش" if new == 0 else f"{new} ثانیه"
            await query.answer(f"✅ {lbl}")
        except Exception as e:
            print("[AI_DEL ERR]", str(e))
            await query.answer("❌ خطا", show_alert=True)
        return

    if action == "owner_set_back":
        try:
            from modules.start import sudo_panel_menu
            await _safe_edit(query, "منوی اصلی - بخش مورد نظر:", sudo_panel_menu(uid, chat_id))
        except Exception as e:
            print("[OWNER_SET_BACK ERR]", str(e))
            await query.answer("❌ خطا در بازگشت", show_alert=True)
            return
        await query.answer()
        return

    if action == "owner_set_cd":
        try:
            opts = [0, 5, 10, 15, 30, 60]
            cur = get_chat_cooldown(chat_id)
            try:
                i = opts.index(cur)
                new = opts[(i + 1) % len(opts)]
            except ValueError:
                new = 30
            set_chat_cooldown(chat_id, new)
            try:
                await _safe_edit(query, None, _build_menu(uid, chat_id))
            except Exception:
                pass
            cd_lbl = "خاموش" if new == 0 else f"{new} ثانیه"
            await query.answer(f"✅ Cooldown: {cd_lbl}")
        except Exception as e:
            print("[OWNER_SET_CD ERR]", str(e))
            await query.answer("❌ خطا", show_alert=True)
        return

    if action == "owner_set_del":
        try:
            opts = [0, 10, 15, 30, 60, 120, 300]
            cur = get_chat_panel_delete(chat_id)
            try:
                i = opts.index(cur)
                new = opts[(i + 1) % len(opts)]
            except ValueError:
                new = 30
            set_chat_panel_delete(chat_id, new)
            try:
                await _safe_edit(query, None, _build_menu(uid, chat_id))
            except Exception:
                pass
            await query.answer(f"✅ حذف پنل: {_fmt_sec(new)}")
        except Exception as e:
            print("[OWNER_SET_DEL ERR]", str(e))
            await query.answer("❌ خطا", show_alert=True)
        return

    if action == "rep_settings_menu":
        try:
            await _safe_edit(query, "📊 تنظیمات گزارش\n\nبرای تغییر هر گزینه روی آن بزنید.", reply_markup=_build_reports_menu(uid, chat_id))
        except Exception as e:
            print("[REP MENU ERR] " + str(e))
        return

    if action == "rep_settings_back":
        try:
            await _safe_edit(query, "⚙️ تنظیمات این گروه", reply_markup=_build_menu(uid, chat_id))
        except Exception as e:
            print("[REP BACK ERR] " + str(e))
        return

    if action == "ai_menu":
        try:
            await _safe_edit(query, "🗣️ AI\n\nتنظیمات پاسخ‌دهی خودکار:", reply_markup=_build_ai_menu(uid, chat_id))
        except Exception as e:
            print("[AI MENU ERR] " + str(e))
        return

    if action == "ai_back":
        try:
            await _safe_edit(query, "⚙️ تنظیمات این گروه", reply_markup=_build_menu(uid, chat_id))
        except Exception as e:
            print("[AI BACK ERR] " + str(e))
        return

    if action == "timer_menu":
        try:
            await _safe_edit(query, "⏱ تنظیمات تایمر\n\nتایمر بر اساس عدم فعالیت است.", reply_markup=_build_timer_menu(uid, chat_id))
        except Exception as e:
            print("[TIMER MENU ERR] " + str(e))
        return

    if action == "owner_rep_dl":
        try:
            cur = get_report_settings(chat_id)[0]
            try:
                i = REP_LIMIT_OPTS.index(cur)
            except ValueError:
                i = 0
            new = REP_LIMIT_OPTS[(i + 1) % len(REP_LIMIT_OPTS)]
            set_report_daily_limit(chat_id, new)
            try:
                await _safe_edit(query, "⚙️ تنظیمات این گروه", reply_markup=_build_reports_menu(uid, chat_id))
            except Exception:
                pass
            await query.answer(f"✅ سهمیه: {new} گزارش")
        except Exception as e:
            print("[REP_DL ERR] " + str(e))
        return

    if action == "owner_rep_cd":
        try:
            cur = get_report_settings(chat_id)[1]
            try:
                i = REP_CD_OPTS.index(cur)
            except ValueError:
                i = 0
            new = REP_CD_OPTS[(i + 1) % len(REP_CD_OPTS)]
            set_report_cooldown(chat_id, new)
            try:
                await _safe_edit(query, "⚙️ تنظیمات این گروه", reply_markup=_build_reports_menu(uid, chat_id))
            except Exception:
                pass
            await query.answer(f"✅ فاصله: {fmt_rep_cd(new)}")
        except Exception as e:
            print("[REP_CD ERR] " + str(e))
        return

    if action == "timer_back":
        try:
            await _safe_edit(query, "⚙️ تنظیمات این گروه", reply_markup=_build_menu(uid, chat_id))
        except Exception as e:
            print("[TIMER BACK ERR] " + str(e))
        return

    if action == "owner_set_warn":
        try:
            from database import get_chat_panel_warning, set_chat_panel_warning
            cur = get_chat_panel_warning(chat_id)
            new = 0 if cur == 1 else 1
            set_chat_panel_warning(chat_id, new)
            try:
                await _safe_edit(query, "⏱ تنظیمات تایمر", reply_markup=_build_timer_menu(uid, chat_id))
            except Exception:
                pass
            await query.answer("🔔 هشدار " + ("فعال" if new == 1 else "غیرفعال"))
        except Exception as e:
            print("[WARN ERR] " + str(e))
        return

    if action == "owner_set_pt":
        try:
            opts = [30, 60, 180, 300]
            cur = get_chat_panel_timeout(chat_id)
            try:
                i = opts.index(cur)
                new = opts[(i + 1) % len(opts)]
            except ValueError:
                new = 300
            set_chat_panel_timeout(chat_id, new)
            try:
                await _safe_edit(query, None, _build_menu(uid, chat_id))
            except Exception:
                pass
            await query.answer(f"✅ انقضا: {_fmt_sec(new)}")
        except Exception as e:
            print("[OWNER_SET_PT ERR]", str(e))
            await query.answer("❌ خطا", show_alert=True)
        return

    if action == "owner_set_ed":
        try:
            opts = [0, 10, 20, 30, 60, 120]
            cur = get_chat_expire_delete(chat_id)
            try:
                i = opts.index(cur)
                new = opts[(i + 1) % len(opts)]
            except ValueError:
                new = 20
            set_chat_expire_delete(chat_id, new)
            try:
                await _safe_edit(query, None, _build_menu(uid, chat_id))
            except Exception:
                pass
            await query.answer(f"✅ حذف پیام expire: {_fmt_sec(new)}")
        except Exception as e:
            print("[OWNER_SET_ED ERR]", str(e))
            await query.answer("❌ خطا", show_alert=True)
        return

    await query.answer()


def register(app):
    app.add_handler(
        CallbackQueryHandler(owner_set_cb, pattern=r"^(owner_set_|timer_menu|timer_back|ai_menu|ai_back|rep_settings_menu|rep_settings_back|owner_rep_dl|owner_rep_cd)"),
        group=-45
    )
    print("OK module owner_set_group loaded")
