"""مدیریت سیستم - فقط برای سازنده"""
import os
import time
import asyncio
import subprocess
import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler, MessageHandler, filters, ApplicationHandlerStop
from config import OWNER_ID, DATABASE_PATH
from database import (
    get_chat_panel_timeout, get_chat_expire_delete,
    get_setting, set_setting, get_all_bot_chats, check_active,
    vacuum_database, check_db_integrity, get_db_stats,
    cleanup_old_records, truncate_log_file, cleanup_temp_files,
    cleanup_old_backups
)


def _fmt(n):
    if n is None: return "N/A"
    for u in ['B', 'KB', 'MB', 'GB']:
        if n < 1024: return f"{n:.2f} {u}"
        n /= 1024
    return f"{n:.2f} TB"


def build_system_menu(uid=0, chat_id=0):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🖥 وضعیت سیستم", callback_data=f"sysinfo_menu:{uid}:{chat_id}")],
        [InlineKeyboardButton("🤖 مدیریت AI", callback_data="ai_panel")],
        [InlineKeyboardButton("👥 بانک کاربران", callback_data="uc_menu")],
        [InlineKeyboardButton("📜 لاگ‌ها", callback_data=f"sys_logs:{uid}:{chat_id}"),
         InlineKeyboardButton("🚫 اسپم‌ترکر", callback_data=f"spam_tracker_menu:{uid}:{chat_id}")],
        [InlineKeyboardButton("📖 بیوگرافی ربات", callback_data=f"bio_panel:{uid}:{chat_id}")],
         [InlineKeyboardButton("💾 بکاپ فوری", callback_data=f"sys_backup:{uid}:{chat_id}"),
         InlineKeyboardButton("🗄 دیتابیس", callback_data=f"sys_db:{uid}:{chat_id}")],
        [InlineKeyboardButton("🧹 پاکسازی", callback_data=f"sys_clean:{uid}:{chat_id}"),
         InlineKeyboardButton("🌐 شبکه", callback_data=f"sys_net:{uid}:{chat_id}")],
        [InlineKeyboardButton("⚙️ تنظیمات سیستم", callback_data=f"sys_settings:{uid}:{chat_id}")],
        [InlineKeyboardButton("🔄 ری‌استارت ربات", callback_data=f"sys_restart:{uid}:{chat_id}")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data=f"sys_back:{uid}:{chat_id}"),
         InlineKeyboardButton("❌ بستن", callback_data=f"menu_close:{uid}")],
    ])


def build_db_menu(uid=0, chat_id=0):
    try:
        size = _fmt(os.path.getsize(DATABASE_PATH))
    except Exception:
        size = "N/A"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"📊 حجم فعلی: {size}", callback_data=f"sys_db_size:{uid}:{chat_id}")],
        [InlineKeyboardButton("📈 آمار جداول", callback_data=f"sys_db_stats:{uid}:{chat_id}")],
        [InlineKeyboardButton("🗜 VACUUM (بهینه‌سازی)", callback_data=f"sys_db_vacuum:{uid}:{chat_id}")],
        [InlineKeyboardButton("🔍 بررسی سلامت", callback_data=f"sys_db_check:{uid}:{chat_id}")],
        [InlineKeyboardButton("📤 Export دیتابیس", callback_data=f"sys_db_export:{uid}:{chat_id}")],
        [InlineKeyboardButton("⚠️ پاکسازی رکوردهای قدیمی", callback_data=f"sys_db_cleanup:{uid}:{chat_id}")],
        [InlineKeyboardButton(_tml, callback_data=f"sys_set_deltimer:{uid}:{chat_id}")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data=f"sys_menu:{uid}:{chat_id}")],
    ])


def build_clean_menu(uid=0, chat_id=0):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📄 برش لاگ (فقط اخیر)", callback_data=f"sys_clean_log:{uid}:{chat_id}")],
        [InlineKeyboardButton("🗑 حذف کامل لاگ", callback_data=f"sys_clean_logall:{uid}:{chat_id}")],
        [InlineKeyboardButton("💾 پاکسازی بکاپ‌های قدیمی", callback_data=f"sys_clean_backup:{uid}:{chat_id}")],
        [InlineKeyboardButton("🧽 پاک کردن فایل‌های temp", callback_data=f"sys_clean_temp:{uid}:{chat_id}")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data=f"sys_menu:{uid}:{chat_id}")],
    ])


def build_net_menu(uid=0, chat_id=0):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🏓 تست اتصال تلگرام", callback_data=f"sys_net_tg:{uid}:{chat_id}")],
        [InlineKeyboardButton("🌐 تست SIGHTENGINE", callback_data=f"sys_net_se:{uid}:{chat_id}")],
        [InlineKeyboardButton("📡 تست DNS", callback_data=f"sys_net_dns:{uid}:{chat_id}")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data=f"sys_menu:{uid}:{chat_id}")],
    ])




async def _safe_edit_sys(query, text=None, reply_markup=None):
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
            import re
            m = re.search(r'Retry in (\d+) seconds', err)
            sec = m.group(1) if m else "چند"
            try:
                await query.answer(f"⏳ {sec} ثانیه صبر کن", show_alert=True)
            except Exception:
                pass
        else:
            print("[SAFE EDIT ERR]", err)
        return False


def _fmt_sec2(s):
    s = int(s)
    if s == 0:
        return "خاموش"
    if s < 60:
        return f"{s} ثانیه"
    return f"{s // 60} دقیقه"


def build_settings_menu(uid=0, chat_id=0):
    w = get_setting(0, "sys_restart_warning", "1") == "1"
    d = get_setting(0, "sys_restart_delay", "10")
    gb = get_setting(0, "auto_global_ban_enabled", "1") == "1"
    ac = get_setting(0, "sys_auto_cleanup", "1") == "1"
    av = get_setting(0, "sys_auto_vacuum", "1") == "1"
    ui = get_setting(0, "sys_sudo_userinfo", "0") == "1"
    cd_sec = get_setting(0, "sys_cooldown_seconds", "30")
    pt = get_setting(0, "sys_panel_timeout_seconds", "300")
    ed = get_setting(0, "sys_expire_delete_seconds", "20")
    dl = get_setting(0, "sys_panel_delete_time", "30")
    _adc = get_setting(0, "auto_delete_commands", "1") == "1"
    _adl = "🗑 حذف خودکار دستور " + ("✅" if _adc else "❌")
    _tml = "⏱ تایمر: " + str(get_setting(0, 'sys_panel_delete_time', '30')) + "s"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"🔔 هشدار قبل از ری‌استارت: {'✅' if w else '❌'}", callback_data=f"sys_tog_warn:{uid}:{chat_id}")],
        [InlineKeyboardButton(f"⏱ تأخیر ری‌استارت: {d} ثانیه", callback_data=f"sys_set_delay:{uid}:{chat_id}")],
        [InlineKeyboardButton(f"🚫 Global Ban خودکار: {'✅' if gb else '❌'}", callback_data=f"sys_tog_gb:{uid}:{chat_id}")],
        [InlineKeyboardButton(f"🔐 دسترسی سودو به /userinfo: {'✅' if ui else '❌'}", callback_data=f"sys_tog_ui:{uid}:{chat_id}")],
        [InlineKeyboardButton(f"📡 بازه چک اتصال: {get_setting(0, 'monitor_interval', '10')} ثانیه", callback_data=f"sys_set_monitor:{uid}:{chat_id}")],
        [InlineKeyboardButton(f"🚀 اجرای خودکار در Termux: {'✅' if get_setting(0, 'sys_autostart', '1') == '1' else '❌'}", callback_data=f"sys_tog_autostart:{uid}:{chat_id}")],
        [InlineKeyboardButton(f"📡 Connection Monitor: {'✅' if get_setting(0, 'sys_monitor_enabled', '1') == '1' else '❌'}", callback_data=f"sys_tog_monitor:{uid}:{chat_id}")],
        [InlineKeyboardButton(f"🧹 پاکسازی خودکار: {'✅' if ac else '❌'}", callback_data=f"sys_tog_ac:{uid}:{chat_id}")],
        [InlineKeyboardButton(f"🗜 VACUUM خودکار هفتگی: {'✅' if av else '❌'}", callback_data=f"sys_tog_av:{uid}:{chat_id}")],
        [InlineKeyboardButton(_adl, callback_data=f"sys_tog_autodel:{uid}:{chat_id}")],
        [InlineKeyboardButton(_tml, callback_data=f"sys_set_deltimer:{uid}:{chat_id}")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data=f"sys_menu:{uid}:{chat_id}")],
    ])


async def do_backup_with_notify(context):
    """بکاپ رو اجرا می‌کنه و بعدش پیام تأیید به Owner می‌ده"""
    from modules.backup_daemon import run_backup, BACKUP_DIR
    import glob
    import asyncio

    before = set(glob.glob(os.path.join(BACKUP_DIR, 'groupbot_backup_*.tar.gz')))

    try:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, run_backup)

        after = set(glob.glob(os.path.join(BACKUP_DIR, 'groupbot_backup_*.tar.gz')))
        new_files = after - before

        if new_files:
            latest = max(new_files, key=os.path.getmtime)
            size = os.path.getsize(latest)
            size_str = f"{size / 1024 / 1024:.2f} MB"
            try:
                await context.bot.send_message(
                    chat_id=OWNER_ID,
                    text=f"✅ بکاپ با موفقیت انجام شد\n\n📁 {os.path.basename(latest)}\n💾 حجم: {size_str}"
                )
            except Exception as e:
                print("[BACKUP NOTIFY ERR]", str(e))
        else:
            try:
                await context.bot.send_message(
                    chat_id=OWNER_ID,
                    text="⚠️ بکاپ تموم شد ولی فایل جدیدی پیدا نشد."
                )
            except Exception:
                pass
    except Exception as e:
        try:
            await context.bot.send_message(
                chat_id=OWNER_ID,
                text=f"❌ خطا در بکاپ:\n\n{str(e)[:300]}"
            )
        except Exception:
            pass


async def sys_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    user = query.from_user
    data = query.data
    parts = data.split(":")
    action = parts[0]

    if user.id != OWNER_ID:
        await query.answer("⛔ فقط سازنده!", show_alert=True)
        return

    uid = user.id
    chat_id = 0
    try:
        if len(parts) > 2 and parts[2].lstrip('-').isdigit():
            chat_id = int(parts[2])
    except Exception:
        pass

    if action == "bio_panel":
        try:
            from database import get_setting as _gs
            _bio = _gs(0, "bio_text", "")
        except Exception:
            _bio = ""
        if not _bio:
            _bio = "(پیش‌فرض - متن اسکای‌تیم)"
        _text = "📖 *بیوگرافی ربات*\n\n" + _bio
        _kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("✏️ ادیت بیو", callback_data=f"bio_edit:{uid}:{chat_id}")],
            [InlineKeyboardButton("🔄 بازنشانی پیش‌فرض", callback_data=f"bio_reset:{uid}:{chat_id}")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data=f"sys_menu:{uid}:{chat_id}")],
        ])
        try:
            await query.edit_message_text(_text, reply_markup=_kb, parse_mode="Markdown")
        except Exception:
            try:
                await query.edit_message_text(_text, reply_markup=_kb)
            except Exception:
                pass
        await query.answer()
        return

    if action == "bio_edit":
        context.user_data["bio_waiting"] = True
        _kb = InlineKeyboardMarkup([[InlineKeyboardButton("❌ لغو", callback_data=f"bio_panel:{uid}:{chat_id}")]])
        try:
            await query.edit_message_text("✏️ متن جدید بیوگرافی رو بفرست:\n\n(متن خالی = بازگشت به پیش‌فرض)", reply_markup=_kb)
        except Exception:
            pass
        await query.answer()
        return

    if action == "bio_reset":
        try:
            from database import set_setting
            set_setting(0, "bio_text", "")
            await query.answer("✅ به پیش‌فرض برگشت", show_alert=True)
        except Exception:
            await query.answer("❌ خطا", show_alert=True)
        return

    if action == "sys_menu":
        try:
            await query.edit_message_text("🖥 *مدیریت سیستم*",
                                          reply_markup=build_system_menu(uid, chat_id),
                                          parse_mode="Markdown")
        except Exception as e:
            print("[SYS MENU]", str(e))
        await query.answer()
        return

    if action == "sys_back":
        try:
            from modules.start import sudo_panel_menu
            await query.edit_message_text("منوی اصلی - بخش مورد نظر:",
                                          reply_markup=sudo_panel_menu(uid, chat_id))
        except Exception as e:
            print("[SYS BACK]", str(e))
        await query.answer()
        return

    if action == "sys_db":
        try:
            await query.edit_message_text("🗄 *مدیریت دیتابیس*",
                                          reply_markup=build_db_menu(uid, chat_id),
                                          parse_mode="Markdown")
        except Exception:
            pass
        await query.answer()
        return

    if action == "sys_db_size":
        try:
            s = os.path.getsize(DATABASE_PATH)
            await query.answer(f"📊 {_fmt(s)}", show_alert=True)
        except Exception:
            await query.answer("❌ خطا", show_alert=True)
        return

    if action == "sys_db_stats":
        stats = get_db_stats()
        text = "📈 *آمار جداول:*\n\n"
        for t, cnt in sorted(stats.items(), key=lambda x: -x[1]):
            text += f"• `{t}`: {cnt}\n"
        if len(text) > 3800:
            text = text[:3800] + "..."
        try:
            await query.edit_message_text(text, parse_mode="Markdown",
                                          reply_markup=InlineKeyboardMarkup([
                                              [InlineKeyboardButton("🔙 بازگشت", callback_data=f"sys_db:{uid}:{chat_id}")]
                                          ]))
        except Exception:
            pass
        await query.answer()
        return

    if action == "sys_db_vacuum":
        await query.answer("🗜 در حال VACUUM...")
        b, a, ok = vacuum_database()
        if ok:
            saved = b - a
            pct = round(100.0 * saved / b, 1) if b > 0 else 0
            text = f"✅ *VACUUM انجام شد*\n\n📊 قبل: `{_fmt(b)}`\n📊 بعد: `{_fmt(a)}`\n💾 صرفه‌جویی: `{_fmt(saved)}` ({pct}%)"
        else:
            text = "❌ خطا در VACUUM"
        try:
            await query.edit_message_text(text, parse_mode="Markdown",
                                          reply_markup=InlineKeyboardMarkup([
                                              [InlineKeyboardButton("🔙 بازگشت", callback_data=f"sys_db:{uid}:{chat_id}")]
                                          ]))
        except Exception:
            pass
        return

    if action == "sys_db_check":
        await query.answer("🔍 در حال بررسی...")
        result = check_db_integrity()
        if result == "ok":
            text = "✅ *دیتابیس سالمه*\n\nنتیجه: `ok`"
        else:
            text = f"⚠️ *مشکل پیدا شد*\n\n`{result[:500]}`"
        try:
            await query.edit_message_text(text, parse_mode="Markdown",
                                          reply_markup=InlineKeyboardMarkup([
                                              [InlineKeyboardButton("🔙 بازگشت", callback_data=f"sys_db:{uid}:{chat_id}")]
                                          ]))
        except Exception:
            pass
        return

    if action == "sys_db_export":
        await query.answer("📤 در حال ارسال...")
        try:
            with open(DATABASE_PATH, "rb") as f:
                await context.bot.send_document(
                    chat_id=OWNER_ID, document=f,
                    filename=f"groupbot_db_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.db",
                    caption="📤 Export دیتابیس"
                )
        except Exception as e:
            print("[DB EXPORT]", str(e))
        return

    if action == "sys_db_cleanup":
        await query.answer("⚠️ در حال پاکسازی...")
        r = cleanup_old_records()
        text = "🧹 *پاکسازی انجام شد*\n\n"
        for k, v in r.items():
            text += f"• `{k}`: {v} رکورد\n"
        text += "\n✅ اسپم‌ترکر، بلاک‌لیست سراسری، اعضا و group_events دست نخورده موندن."
        try:
            await query.edit_message_text(text, parse_mode="Markdown",
                                          reply_markup=InlineKeyboardMarkup([
                                              [InlineKeyboardButton("🔙 بازگشت", callback_data=f"sys_db:{uid}:{chat_id}")]
                                          ]))
        except Exception:
            pass
        return

    if action == "sys_clean":
        try:
            await query.edit_message_text("🧹 *پاکسازی و نگهداری*",
                                          reply_markup=build_clean_menu(uid, chat_id),
                                          parse_mode="Markdown")
        except Exception:
            pass
        await query.answer()
        return

    if action == "sys_clean_log":
        await query.answer("📄 در حال برش...")
        b, a = truncate_log_file(5000)
        text = f"✅ *لاگ برش شد*\n\n📊 قبل: `{_fmt(b)}`\n📊 بعد: `{_fmt(a)}`"
        try:
            await query.edit_message_text(text, parse_mode="Markdown",
                                          reply_markup=InlineKeyboardMarkup([
                                              [InlineKeyboardButton("🔙 بازگشت", callback_data=f"sys_clean:{uid}:{chat_id}")]
                                          ]))
        except Exception:
            pass
        return

    if action == "sys_clean_logall":
        await query.answer()
        try:
            log_path = os.path.expanduser("~/groupbot_bot.log")
            size = os.path.getsize(log_path) if os.path.exists(log_path) else 0
            with open(log_path, "w") as f:
                f.write("")
            await query.edit_message_text(f"✅ *لاگ کامل پاک شد*\n\n📊 آزاد شد: `{_fmt(size)}`",
                                          parse_mode="Markdown",
                                          reply_markup=InlineKeyboardMarkup([
                                              [InlineKeyboardButton("🔙 بازگشت", callback_data=f"sys_clean:{uid}:{chat_id}")]
                                          ]))
        except Exception as e:
            print("[LOG DEL]", str(e))
        return

    if action == "sys_clean_backup":
        await query.answer("💾 در حال پاکسازی...")
        n, freed = cleanup_old_backups(7)
        text = f"✅ *بکاپ‌های قدیمی پاک شدن*\n\n🗑 تعداد: `{n}` فایل\n💾 آزاد شد: `{_fmt(freed)}`"
        try:
            await query.edit_message_text(text, parse_mode="Markdown",
                                          reply_markup=InlineKeyboardMarkup([
                                              [InlineKeyboardButton("🔙 بازگشت", callback_data=f"sys_clean:{uid}:{chat_id}")]
                                          ]))
        except Exception:
            pass
        return

    if action == "sys_clean_temp":
        await query.answer("🧽 در حال پاکسازی...")
        n, freed = cleanup_temp_files()
        text = f"✅ *فایل‌های temp پاک شدن*\n\n🗑 تعداد: `{n}` فایل\n💾 آزاد شد: `{_fmt(freed)}`"
        try:
            await query.edit_message_text(text, parse_mode="Markdown",
                                          reply_markup=InlineKeyboardMarkup([
                                              [InlineKeyboardButton("🔙 بازگشت", callback_data=f"sys_clean:{uid}:{chat_id}")]
                                          ]))
        except Exception:
            pass
        return

    if action == "sys_net":
        try:
            await query.edit_message_text("🌐 *شبکه و اتصال*",
                                          reply_markup=build_net_menu(uid, chat_id),
                                          parse_mode="Markdown")
        except Exception:
            pass
        await query.answer()
        return

    if action == "sys_net_tg":
        await query.answer("🏓 در حال تست...")
        try:
            r = subprocess.run(["ping", "-c", "4", "api.telegram.org"],
                               capture_output=True, text=True, timeout=15)
            out = r.stdout
            if "0% packet loss" in out:
                emoji = "🟢"
            elif "100% packet loss" in out:
                emoji = "🔴"
            else:
                emoji = "🟡"
            text = f"{emoji} *تست اتصال تلگرام*\n\n```\n{out[-800:]}\n```"
            if len(text) > 3800:
                text = text[:3800]
        except Exception as e:
            text = f"❌ خطا: `{e}`"
        try:
            await query.edit_message_text(text, parse_mode="Markdown",
                                          reply_markup=InlineKeyboardMarkup([
                                              [InlineKeyboardButton("🔙 بازگشت", callback_data=f"sys_net:{uid}:{chat_id}")]
                                          ]))
        except Exception:
            pass
        return

    if action == "sys_net_se":
        await query.answer("🌐 در حال تست...")
        try:
            import requests
            t0 = time.time()
            r = requests.get("https://api.sightengine.com", timeout=10)
            lat = round((time.time() - t0) * 1000)
            text = f"✅ *SIGHTENGINE در دسترسه*\n\n📊 کد: `{r.status_code}`\n⏱ تأخیر: `{lat}ms`"
        except Exception as e:
            text = f"❌ خطا: `{str(e)[:200]}`"
        try:
            await query.edit_message_text(text, parse_mode="Markdown",
                                          reply_markup=InlineKeyboardMarkup([
                                              [InlineKeyboardButton("🔙 بازگشت", callback_data=f"sys_net:{uid}:{chat_id}")]
                                          ]))
        except Exception:
            pass
        return

    if action == "sys_net_dns":
        await query.answer("📡 در حال تست...")
        try:
            r = subprocess.run(["nslookup", "api.telegram.org"],
                               capture_output=True, text=True, timeout=10)
            text = f"📡 *نتیجه DNS*\n\n```\n{r.stdout[-1500:]}\n```"
            if len(text) > 3800:
                text = text[:3800]
        except Exception as e:
            text = f"❌ خطا: `{e}`"
        try:
            await query.edit_message_text(text, parse_mode="Markdown",
                                          reply_markup=InlineKeyboardMarkup([
                                              [InlineKeyboardButton("🔙 بازگشت", callback_data=f"sys_net:{uid}:{chat_id}")]
                                          ]))
        except Exception:
            pass
        return

    if action == "sys_settings":
        try:
            await query.edit_message_text("⚙️ *تنظیمات سیستم*",
                                          reply_markup=build_settings_menu(uid, chat_id),
                                          parse_mode="Markdown")
        except Exception:
            pass
        await query.answer()
        return

    toggles = {
        "sys_tog_warn": ("sys_restart_warning", "1"),
        "sys_tog_gb": ("auto_global_ban_enabled", "1"),
        "sys_tog_ac": ("sys_auto_cleanup", "1"),
        "sys_tog_av": ("sys_auto_vacuum", "1"),
        "sys_tog_ui": ("sys_sudo_userinfo", "0"),
    }
    if action in toggles:
        key, default = toggles[action]
        cur = get_setting(0, key, default)
        new = "0" if cur == "1" else "1"
        set_setting(0, key, new)
        try:
            await query.edit_message_reply_markup(reply_markup=build_settings_menu(uid, chat_id))
        except Exception:
            pass
        await query.answer("✅ تغییر کرد")
        return



    if action == "sys_set_cd":
        opts = ["0", "3", "5", "10", "15", "30", "60"]
        cur = get_setting(0, "sys_cooldown_seconds", "30")
        try:
            i = opts.index(cur)
            new = opts[(i + 1) % len(opts)]
        except ValueError:
            new = "30"
        set_setting(0, "sys_cooldown_seconds", new)
        try:
            await query.edit_message_reply_markup(reply_markup=build_settings_menu(uid, chat_id))
        except Exception:
            pass
        await query.answer(f"✅ {_fmt_sec2(new)}")
        return

    if action == "sys_set_del":
        opts = ["0", "10", "15", "30", "60", "120", "300"]
        cur = get_setting(0, "sys_panel_delete_time", "30")
        try:
            i = opts.index(cur)
            new = opts[(i + 1) % len(opts)]
        except ValueError:
            new = "30"
        set_setting(0, "sys_panel_delete_time", new)
        try:
            await query.edit_message_reply_markup(reply_markup=build_settings_menu(uid, chat_id))
        except Exception:
            pass
        await query.answer(f"✅ {_fmt_sec2(new)}")
        return

    if action == "sys_set_pt":
        opts = ["30", "60", "180", "300"]
        cur = get_setting(0, "sys_panel_timeout_seconds", "300")
        try:
            i = opts.index(cur)
            new = opts[(i + 1) % len(opts)]
        except ValueError:
            new = "300"
        set_setting(0, "sys_panel_timeout_seconds", new)
        try:
            await query.edit_message_reply_markup(reply_markup=build_settings_menu(uid, chat_id))
        except Exception:
            pass
        await query.answer(f"✅ {_fmt_sec2(new)}")
        return

    if action == "sys_set_ed":
        opts = ["0", "10", "20", "30", "60", "120"]
        cur = get_setting(0, "sys_expire_delete_seconds", "20")
        try:
            i = opts.index(cur)
            new = opts[(i + 1) % len(opts)]
        except ValueError:
            new = "20"
        set_setting(0, "sys_expire_delete_seconds", new)
        try:
            await query.edit_message_reply_markup(reply_markup=build_settings_menu(uid, chat_id))
        except Exception:
            pass
        await query.answer(f"✅ {_fmt_sec2(new)}")
        return

    if action == "sys_tog_autostart":
        try:
            cur = get_setting(0, "sys_autostart", "1")
            new = "0" if cur == "1" else "1"
            set_setting(0, "sys_autostart", new)
            # آپدیت .bashrc
            import os as _os
            bashrc = _os.path.expanduser("~/.bashrc")
            try:
                with open(bashrc, "r", encoding="utf-8") as _f:
                    _c = _f.read()
                marker = "# Skteam Bot - اجرای خودکار"
                # حذف بخش قدیمی
                if marker in _c:
                    parts = _c.split(marker, 1)
                    # پیدا کردن انتهای بلوک
                    rest = parts[1]
                    # حذف تا آخر بلوک (fi بعدی)
                    import re as _re
                    rest = _re.sub(r"^[\s\S]*?fi\n", "", rest, count=1)
                    _c = parts[0] + rest
                # اگه باید فعال بشه، اضافه کن
                if new == "1":
                    _c += "\n" + marker + " در هر بار باز شدن Termux\n"
                    _c += 'if [ -z "$SKTEAM_STARTED" ]; then\n'
                    _c += '    export SKTEAM_STARTED=1\n'
                    _c += '    if ! pgrep -f "main.py" > /dev/null 2>&1; then\n'
                    _c += '        echo "راه‌اندازی خودکار ربات..."\n'
                    _c += '        bash ~/groupbot/startup.sh\n'
                    _c += '    fi\n'
                    _c += 'fi\n'
                with open(bashrc, "w", encoding="utf-8") as _f:
                    _f.write(_c)
                print("[AUTOSTART] .bashrc آپدیت شد, new=" + new)
            except Exception as _e:
                print("[AUTOSTART ERR]", str(_e))
            try:
                await query.edit_message_reply_markup(reply_markup=build_settings_menu(uid, chat_id))
            except Exception:
                pass
            await query.answer("✅ فعال" if new == "1" else "❌ غیرفعال")
        except Exception as e:
            print("[AUTOSTART OUTER ERR]", str(e))
            await query.answer("❌ خطا", show_alert=True)
        return

    if action == "sys_tog_monitor":
        cur = get_setting(0, "sys_monitor_enabled", "1")
        new = "0" if cur == "1" else "1"
        set_setting(0, "sys_monitor_enabled", new)
        # اگه خاموش شد، daemon رو بکش
        import subprocess as _sp
        if new == "0":
            try:
                _sp.run(["pkill", "-f", "connection_monitor.py"], timeout=5)
                print("[MONITOR] daemon متوقف شد")
            except Exception:
                pass
        else:
            try:
                _sp.Popen(
                    "cd ~/groupbot && nohup python3 -u connection_monitor.py > ~/groupbot_connection_monitor.log 2>&1 &",
                    shell=True, executable="/bin/bash"
                )
                print("[MONITOR] daemon راه‌اندازی شد")
            except Exception:
                pass
        try:
            await query.edit_message_reply_markup(reply_markup=build_settings_menu(uid, chat_id))
        except Exception:
            pass
        await query.answer("✅ فعال" if new == "1" else "❌ غیرفعال")
        return

    if action == "sys_set_monitor":
        opts = ["5", "10", "15", "20", "30", "60", "90", "120"]
        cur = get_setting(0, "monitor_interval", "10")
        try:
            i = opts.index(cur)
            new = opts[(i + 1) % len(opts)]
        except ValueError:
            new = "10"
        set_setting(0, "monitor_interval", new)
        try:
            await query.edit_message_reply_markup(reply_markup=build_settings_menu(uid, chat_id))
        except Exception:
            pass
        await query.answer(f"✅ {new} ثانیه")
        return

    if action == "sys_set_delay":
        opts = ["10", "15", "20", "30", "45", "60"]
        cur = get_setting(0, "sys_restart_delay", "10")
        try:
            i = opts.index(cur)
            new = opts[(i + 1) % len(opts)]
        except ValueError:
            new = "10"
        set_setting(0, "sys_restart_delay", new)
        try:
            await query.edit_message_reply_markup(reply_markup=build_settings_menu(uid, chat_id))
        except Exception:
            pass
        await query.answer(f"✅ {new} ثانیه")
        return

    if action == "sys_logs":
        await query.answer("📜 در حال ارسال...")
        try:
            log_path = os.path.expanduser("~/groupbot_bot.log")
            if os.path.exists(log_path):
                with open(log_path, "rb") as lf:
                    await context.bot.send_document(
                        chat_id=OWNER_ID, document=lf,
                        filename="groupbot_bot.log", caption="📄 لاگ کامل"
                    )
        except Exception as e:
            print("[SYS LOGS]", str(e))
        return

    if action == "sys_backup":
        await query.answer("💾 شروع بکاپ...")
        try:
            await query.edit_message_text(
                "💾 *بکاپ در حال اجراست...*\n\nبعد از اتمام، پیام تأیید به پیوی میاد.",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 بازگشت", callback_data=f"sys_menu:{uid}:{chat_id}")]
                ])
            )
        except Exception:
            pass
        try:
            asyncio.create_task(do_backup_with_notify(context))
        except Exception as e:
            print("[SYS BACKUP TASK ERR]", str(e))
        return

    if action == "sys_restart":
        w = get_setting(0, "sys_restart_warning", "1") == "1"
        d = get_setting(0, "sys_restart_delay", "10")
        text = (f"🔄 *آیا مطمئنی؟*\n\n⏱ تأخیر: `{d}` ثانیه\n"
                f"🔔 هشدار به گروه‌ها: {'✅' if w else '❌'}\n\n"
                "⚠️ ربات چند ثانیه آفلاین می‌شه.")
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ بله، ری‌استارت کن", callback_data=f"sys_restart_yes:{uid}:{chat_id}")],
            [InlineKeyboardButton("❌ لغو", callback_data=f"sys_menu:{uid}:{chat_id}")],
        ])
        try:
            await query.edit_message_text(text, reply_markup=kb, parse_mode="Markdown")
        except Exception:
            pass
        await query.answer()
        return

    if action == "sys_restart_yes":
        d = int(get_setting(0, "sys_restart_delay", "10"))
        w = get_setting(0, "sys_restart_warning", "1") == "1"
        try:
            await query.edit_message_text(f"🔄 *ری‌استارت در حال انجام...*\n\n⏱ `{d}` ثانیه",
                                          parse_mode="Markdown")
        except Exception:
            pass
        await query.answer("🔄 شروع شد")

        sent = 0
        if w:
            try:
                for cid, _ in get_all_bot_chats():
                    try:
                        if not check_active(cid):
                            continue
                        await context.bot.send_message(
                            chat_id=cid,
                            text=f"🔄 ربات در حال بروزرسانی است.\n\nتا {d} ثانیه دیگر مجدداً در دسترس خواهد بود."
                        )
                        sent += 1
                        await asyncio.sleep(0.1)
                    except Exception:
                        pass
            except Exception as e:
                print("[RESTART WARN]", str(e))

        try:
            await context.bot.send_message(
                chat_id=OWNER_ID,
                text=f"🔄 ری‌استارت ربات شروع شد.\n📤 هشدار به {sent} گروه\n⏱ تأخیر: {d} ثانیه"
            )
        except Exception:
            pass

        cmd = (f"sleep {d} && pkill -15 -f 'main.py' ; sleep 3 && "
               f"cd ~/groupbot && source venv/bin/activate && "
               f"nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 &")
        subprocess.Popen(cmd, shell=True, start_new_session=True)
        return

    await query.answer()



async def bio_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """گرفتن متن جدید بیوگرافی از Owner"""
    msg = update.effective_message
    user = update.effective_user
    if not msg or not user or user.id != OWNER_ID:
        return
    if not context.user_data.get("bio_waiting"):
        return
    text = (msg.text or "").strip()
    try:
        await msg.delete()
    except Exception:
        pass
    if len(text) > 500:
        text = text[:500]
    try:
        from database import set_setting
        set_setting(0, "bio_text", text)
    except Exception as e:
        print("[BIO SAVE ERR]", str(e))
    context.user_data.pop("bio_waiting", None)
    try:
        if text:
            await context.bot.send_message(chat_id=user.id, text="\u2705 \u0628\u06cc\u0648\u06af\u0631\u0627\u0641\u06cc \u0630\u062e\u06cc\u0631\u0647 \u0634\u062f.\n\n\u0628\u0631\u0627\u06cc \u062f\u06cc\u062f\u0646: \u067e\u0646\u0644 \u2192 \u0645\u062f\u06cc\u0631\u06cc\u062a \u0633\u06cc\u0633\u062a\u0645 \u2192 \U0001f4d6 \u0628\u06cc\u0648\u06af\u0631\u0627\u0641\u06cc")
        else:
            await context.bot.send_message(chat_id=user.id, text="\u2705 \u0628\u0627\u0632\u06af\u0634\u062a \u0628\u0647 \u067e\u06cc\u0634\u200c\u0641\u0631\u0636.")
    except Exception:
        pass
    raise ApplicationHandlerStop



async def _sys_autodel_toggle(update, context):
    query = update.callback_query
    if not query: return
    try:
        from database import get_setting, set_setting
        cur = get_setting(0, 'auto_delete_commands', '1')
        nxt = '0' if cur == '1' else '1'
        set_setting(0, 'auto_delete_commands', nxt)
        st = 'فعال' if nxt == '1' else 'غیرفعال'
        await query.answer('حذف خودکار: ' + st, show_alert=True)
        uid = query.from_user.id
        cid = query.message.chat_id
        try:
            await query.edit_message_text('⚙️ تنظیمات سیستم:', reply_markup=build_settings_menu(uid, cid))
        except Exception: pass
    except Exception as e:
        print('[AUTODEL ERR] ' + str(e))


async def _sys_deltimer(update, context):
    query = update.callback_query
    if not query: return
    try:
        from database import get_setting, set_setting
        opts = ['10','20','30','60','180','300','600']
        cur = str(get_setting(0, 'sys_panel_delete_time', '30'))
        try: i = opts.index(cur)
        except Exception: i = 2
        nx = (i + 1) % len(opts)
        set_setting(0, 'sys_panel_delete_time', opts[nx])
        await query.answer('تایمر: ' + opts[nx] + 's', show_alert=True)
        uid = query.from_user.id
        cid = query.message.chat_id
        try:
            await query.edit_message_text('⚙️ تنظیمات سیستم:', reply_markup=build_settings_menu(uid, cid))
        except Exception: pass
    except Exception as e:
        print('[DELTIMER ERR] ' + str(e))

def register(app):
    app.add_handler(CallbackQueryHandler(sys_cb, pattern=r"^sys_"), group=-40)
    app.add_handler(CallbackQueryHandler(_sys_autodel_toggle, pattern=r"^sys_tog_autodel:"), group=-40)
    app.add_handler(CallbackQueryHandler(_sys_deltimer, pattern=r"^sys_set_deltimer:"), group=-40)
    app.add_handler(CallbackQueryHandler(sys_cb, pattern=r"^bio_"), group=-40)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE, bio_text_handler), group=-40)
    print("OK module system_management loaded")
