"""ماژول وضعیت سیستم - بدون psutil"""
import os
import time
import shutil
import subprocess
import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from config import OWNER_ID

BOT_START_TIME = time.time()


def _fmt_bytes(n):
    if n is None:
        return "N/A"
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if n < 1024:
            return f"{n:.2f} {unit}"
        n /= 1024
    return f"{n:.2f} PB"


def _fmt_uptime(seconds):
    if seconds is None:
        return "N/A"
    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    mins = int((seconds % 3600) // 60)
    if days > 0:
        return f"{days} روز و {hours} ساعت"
    if hours > 0:
        return f"{hours} ساعت و {mins} دقیقه"
    return f"{mins} دقیقه"


def _run_cmd(cmd):
    """اجرای دستور سیستمی"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
        return result.stdout.strip()
    except Exception:
        return ""


def _get_cpu_percent():
    """محاسبه درصد CPU با /proc/stat"""
    try:
        with open('/proc/stat', 'r') as f:
            line = f.readline()
        parts = line.split()[1:]
        parts = [int(p) for p in parts]
        idle1 = parts[3] + parts[4]
        total1 = sum(parts)
        time.sleep(0.5)
        with open('/proc/stat', 'r') as f:
            line = f.readline()
        parts = line.split()[1:]
        parts = [int(p) for p in parts]
        idle2 = parts[3] + parts[4]
        total2 = sum(parts)
        idle_delta = idle2 - idle1
        total_delta = total2 - total1
        if total_delta == 0:
            return 0.0
        cpu_pct = 100.0 * (1.0 - idle_delta / total_delta)
        return round(cpu_pct, 1)
    except Exception:
        return None


def _get_ram_info():
    """گرفتن اطلاعات RAM از /proc/meminfo"""
    try:
        info = {}
        with open('/proc/meminfo', 'r') as f:
            for line in f:
                parts = line.split()
                if len(parts) >= 2:
                    key = parts[0].rstrip(':')
                    val = int(parts[1]) * 1024  # kB به بایت
                    info[key] = val
        total = info.get('MemTotal', 0)
        available = info.get('MemAvailable', info.get('MemFree', 0))
        used = total - available
        pct = round(100.0 * used / total, 1) if total > 0 else 0
        return {"used": used, "total": total, "pct": pct}
    except Exception:
        return {"used": 0, "total": 0, "pct": 0}


def _get_disk_info():
    """گرفتن اطلاعات دیسک با shutil"""
    try:
        paths_to_check = [
            os.path.expanduser('~'),
            '/data/data/com.termux/files',
        ]
        for p in paths_to_check:
            if os.path.exists(p):
                total, used, free = shutil.disk_usage(p)
                pct = round(100.0 * used / total, 1) if total > 0 else 0
                return {"used": used, "total": total, "pct": pct}
    except Exception:
        pass
    return {"used": 0, "total": 0, "pct": 0}


def _get_uptime():
    """گرفتن آپ‌تایم از /proc/uptime"""
    try:
        with open('/proc/uptime', 'r') as f:
            uptime_seconds = float(f.readline().split()[0])
        return uptime_seconds
    except Exception:
        return None


def _get_bot_stats():
    import sqlite3
    info = {}
    info["uptime"] = time.time() - BOT_START_TIME

    try:
        from config import DATABASE_PATH
        if os.path.exists(DATABASE_PATH):
            info["db_size"] = os.path.getsize(DATABASE_PATH)
            conn = sqlite3.connect(DATABASE_PATH)
            c = conn.cursor()
            for tbl, key in [("groups", "groups_count"), ("members", "members_count"), ("global_blacklist", "gbl_count")]:
                try:
                    c.execute(f"SELECT COUNT(*) FROM {tbl}")
                    info[key] = c.fetchone()[0]
                except Exception:
                    info[key] = 0
            conn.close()
        else:
            info["db_size"] = 0
    except Exception as e:
        info["db_err"] = str(e)

    try:
        log_path = os.path.expanduser("~/groupbot_bot.log")
        if os.path.exists(log_path):
            info["log_size"] = os.path.getsize(log_path)
    except Exception:
        pass

    return info


def build_sysinfo_text():
    ram = _get_ram_info()
    disk = _get_disk_info()
    cpu = _get_cpu_percent()
    uptime = _get_uptime()
    bot_info = _get_bot_stats()
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    text = "🖥 *وضعیت سیستم ربات*\n"
    text += "━━━━━━━━━━━━━━━━━━━━\n\n"

    text += "📊 *منابع سرور:*\n"
    if cpu is not None:
        cpu_emoji = "🟢" if cpu < 50 else "🟡" if cpu < 80 else "🔴"
        text += f"{cpu_emoji} CPU: `{cpu}%`\n"
    else:
        text += "⚪ CPU: `N/A`\n"

    ram_pct = ram["pct"]
    ram_emoji = "🟢" if ram_pct < 60 else "🟡" if ram_pct < 85 else "🔴"
    text += f"{ram_emoji} RAM: `{_fmt_bytes(ram['used'])} / {_fmt_bytes(ram['total'])}` ({ram_pct}%)\n"

    disk_pct = disk["pct"]
    disk_emoji = "🟢" if disk_pct < 70 else "🟡" if disk_pct < 90 else "🔴"
    text += f"{disk_emoji} Disk: `{_fmt_bytes(disk['used'])} / {_fmt_bytes(disk['total'])}` ({disk_pct}%)\n"

    if uptime is not None:
        text += f"⏱ روشن بودن: `{_fmt_uptime(uptime)}`\n"

    text += "\n🤖 *اطلاعات ربات:*\n"
    text += f"🕐 آپ‌تایم ربات: `{_fmt_uptime(bot_info.get('uptime', 0))}`\n"
    text += f"🐍 Python: `{os.sys.version.split()[0]}`\n"

    try:
        import telegram
        text += f"📚 PTB: `{telegram.__version__}`\n"
    except Exception:
        pass

    text += f"👥 گروه‌ها: `{bot_info.get('groups_count', 0)}`\n"
    text += f"👤 اعضا: `{bot_info.get('members_count', 0)}`\n"
    text += f"🚫 بلاک‌لیست: `{bot_info.get('gbl_count', 0)}`\n"
    text += f"💾 دیتابیس: `{_fmt_bytes(bot_info.get('db_size', 0))}`\n"

    if "log_size" in bot_info:
        text += f"📄 لاگ: `{_fmt_bytes(bot_info['log_size'])}`\n"

    text += f"\n🕒 زمان بررسی: `{now}`"

    return text


def build_sysinfo_keyboard(uid, chat_id=0):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 بروزرسانی", callback_data=f"sysinfo_refresh:{uid}:{chat_id}")],
        [InlineKeyboardButton("🔙 بازگشت", callback_data=f"sysinfo_back:{uid}:{chat_id}")],
    ])


async def sysinfo_cb_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    data = query.data
    parts = data.split(":")
    action = parts[0]

    if user.id != OWNER_ID:
        await query.answer("⛔ فقط سازنده!", show_alert=True)
        return

    if action == "sysinfo_menu":
        uid = int(parts[1]) if len(parts) > 1 else user.id
        chat_id = int(parts[2]) if len(parts) > 2 else 0
        if query.message.chat.type == "private":
            chat_id = 0
        try:
            text = build_sysinfo_text()
            await query.edit_message_text(text, reply_markup=build_sysinfo_keyboard(uid, chat_id), parse_mode="Markdown")
        except Exception as e:
            print("[SYSINFO ERR]", str(e))
        await query.answer()
        return

    if action == "sysinfo_refresh":
        uid = int(parts[1]) if len(parts) > 1 else user.id
        chat_id = int(parts[2]) if len(parts) > 2 else query.message.chat_id
        try:
            text = build_sysinfo_text()
            await query.edit_message_text(text, reply_markup=build_sysinfo_keyboard(uid, chat_id), parse_mode="Markdown")
            await query.answer("🔄 بروزرسانی شد")
        except Exception as e:
            print("[SYSINFO REFRESH ERR]", str(e))
            await query.answer("❌ خطا در بروزرسانی", show_alert=True)
        return

    if action == "sysinfo_back":
        uid = int(parts[1]) if len(parts) > 1 else user.id
        chat_id = int(parts[2]) if len(parts) > 2 else query.message.chat_id
        # اگه توی پیوی هستیم، chat_id صفر باید بشه
        if query.message.chat.type == "private":
            chat_id = 0
        try:
            from modules.system_management import build_system_menu
            await query.edit_message_text(
                "منوی اصلی - بخش مورد نظر:",
                reply_markup=build_system_menu(uid, chat_id)
            )
        except Exception as e:
            print("[SYSINFO BACK ERR]", str(e))
            await query.answer("❌ خطا در بازگشت", show_alert=True)
            return
        await query.answer()
        return

    await query.answer()


def register(app):
    app.add_handler(CallbackQueryHandler(sysinfo_cb_handler, pattern=r"^sysinfo_"), group=-50)
    print("OK module system_info loaded (no-psutil)")
