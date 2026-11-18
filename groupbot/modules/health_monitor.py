"""health_monitor.py — چک خودکار سلامت ۴ سرویس + alert به owner."""
import logging, subprocess, os, time, sqlite3, asyncio
from pathlib import Path
from telegram.ext import ContextTypes
from config import OWNER_ID

log = logging.getLogger("health_monitor")
NL = chr(10)

# ═══ تنظیمات ═══
CHECK_INTERVAL = 300        # هر ۵ دقیقه
ALERT_COOLDOWN = 1800       # هر ۳۰ دقیقه یه alert برای هر سرویس
SERVICES = {
    "🤖 ربات مدیریت":  "main.py",
    "🎵 ربات موزیک":   "bot.py",
    "📡 Media Server": "server.py",
    "▶️ پلیر":  "player.py",
}

# ═══ state (توی حافظه) ═══
_last_alert = {}    # {service: timestamp}
_last_state = {}    # {service: "up"/"down"}


def _is_alive(pattern):
    """چک می‌کنه پروسه‌ای با این pattern زنده‌ست."""
    try:
        out = subprocess.check_output(
            ["bash", "-c", f"ps aux | grep -F '{pattern}' | grep -v grep"],
            timeout=5, stderr=subprocess.DEVNULL
        ).decode().strip()
        return bool(out)
    except Exception:
        return False


async def _health_check(context: ContextTypes.DEFAULT_TYPE):
    """job callback — هر ۵ دقیقه."""
    global _last_alert, _last_state
    now = time.time()
    down = []

    for name, pattern in SERVICES.items():
        alive = _is_alive(pattern)
        cur = "up" if alive else "down"
        prev = _last_state.get(name)

        # تغییر وضعیت: از up به down
        if cur == "down" and prev != "down":
            down.append(name)
            _last_state[name] = "down"
        elif cur == "up" and prev == "down":
            # برگشت به حالت عادی → پیام "recovered"
            try:
                await context.bot.send_message(
                    OWNER_ID,
                    f"✅ **سرویس برگشت:** {name}"
                )
            except Exception as e:
                log.warning(f"recover msg err: {e}")
            _last_state[name] = "up"
            _last_alert.pop(name, None)
        elif prev is None:
            # اولین اجرا
            _last_state[name] = cur

    # alert برای سرویس‌های down
    if down:
        # چک cooldown
        alert_list = []
        for name in down:
            last = _last_alert.get(name, 0)
            if now - last > ALERT_COOLDOWN:
                alert_list.append(name)
                _last_alert[name] = now

        if alert_list:
            txt = "🚨 **هشدار سلامت سرویس‌ها**" + NL + "━━━━━━━━━━━━━━━━━" + NL
            for n in alert_list:
                txt += f"❌ {n} — خاموش" + NL
            txt += NL + "🛠 برای ری‌استارت: `/restart_service`"
            try:
                await context.bot.send_message(OWNER_ID, txt, parse_mode="Markdown")
                log.warning(f"[HEALTH] alerts: {alert_list}")
            except Exception as e:
                log.warning(f"alert err: {e}")


async def cmd_health(update, context: ContextTypes.DEFAULT_TYPE):
    """دستور /health — نمایش وضعیت زنده."""
    u = update.effective_user
    if u.id != OWNER_ID:
        return
    msg = update.effective_message

    txt = "🩺 **وضعیت سلامت سرویس‌ها**" + NL + "━━━━━━━━━━━━━━━━━" + NL
    for name, pattern in SERVICES.items():
        alive = _is_alive(pattern)
        txt += f"{'✅' if alive else '❌'} {name}" + NL

    from datetime import datetime as _dt
    txt += NL + f"🕐 `{_dt.now().strftime('%H:%M:%S')}`"
    try:
        await msg.reply_text(txt, parse_mode="Markdown")
    except Exception as e:
        log.warning(f"health cmd err: {e}")




SVC_LABEL = {
    "main":   "🤖 ربات مدیریت",
    "bot":    "🎵 ربات موزیک",
    "server": "📡 Media Server",
    "player": "▶️ پلیر",
}


async def cmd_restart_service(update, context: ContextTypes.DEFAULT_TYPE):
    """دستور /restart_service — لیست سرویس‌ها برای ری‌استارت."""
    u = update.effective_user
    if u.id != OWNER_ID:
        return
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    kb = [
        [InlineKeyboardButton(SVC_LABEL["main"],   callback_data="rs:main")],
        [InlineKeyboardButton(SVC_LABEL["bot"],    callback_data="rs:bot")],
        [InlineKeyboardButton(SVC_LABEL["server"], callback_data="rs:server")],
        [InlineKeyboardButton(SVC_LABEL["player"], callback_data="rs:player")],
        [InlineKeyboardButton("❌ بستن", callback_data="rs:close")],
    ]
    await update.message.reply_text(
        "🛠 **ری‌استارت سرویس**" + NL + "━━━━━━━━━━━━━━━━━" + NL + "کدوم رو ری‌استارت کنم؟",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="Markdown",
    )


async def cb_restart_service(update, context: ContextTypes.DEFAULT_TYPE):
    """callback دکمه‌های ری‌استارت."""
    from telegram import InlineKeyboardMarkup, InlineKeyboardButton
    q = update.callback_query
    u = q.from_user
    if u.id != OWNER_ID:
        await q.answer("⛔", show_alert=True)
        return

    data = q.data
    if data == "rs:close":
        try:
            await q.message.delete()
        except Exception:
            pass
        return

    # ★ دکمه بازگشت به منوی ری‌استارت
    if data == "rs:menu":
        from telegram import InlineKeyboardMarkup, InlineKeyboardButton
        kb = [
            [InlineKeyboardButton(SVC_LABEL["main"],   callback_data="rs:main")],
            [InlineKeyboardButton(SVC_LABEL["bot"],    callback_data="rs:bot")],
            [InlineKeyboardButton(SVC_LABEL["server"], callback_data="rs:server")],
            [InlineKeyboardButton(SVC_LABEL["player"], callback_data="rs:player")],
            [InlineKeyboardButton("❌ بستن", callback_data="rs:close")],
        ]
        try:
            await q.edit_message_text(
                "🛠 **ری‌استارت سرویس**" + NL + "━━━━━━━━━━━━━━━━━" + NL + "کدوم رو ری‌استارت کنم؟",
                reply_markup=InlineKeyboardMarkup(kb),
                parse_mode="Markdown",
            )
        except Exception:
            pass
        return

    svc = data.split(":", 1)[1]
    label = SVC_LABEL.get(svc, svc)

    await q.answer(f"⏳ ری‌استارت {label}...", show_alert=False)
    try:
        await q.edit_message_text(
            f"⏳ **در حال ری‌استارت {label}...**" + NL + NL + "۱۵ ثانیه صبر کن...",
            parse_mode="Markdown"
        )
    except Exception:
        pass

    # اجرای detached
    try:
        subprocess.Popen(
            ["setsid", "bash", str(Path.home() / ".restart_svc.sh"), svc],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    except Exception as e:
        try:
            await q.edit_message_text(f"❌ خطای اجرا: {e}")
        except Exception:
            pass
        return

    await asyncio.sleep(15)

    # چک وضعیت
    alive = _is_alive(svc + ".py")
    status = "✅ بالا اومد" if alive else "❌ بالا نیومد"
    back_kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 دوباره تلاش", callback_data="rs:" + svc)],
        [InlineKeyboardButton("🔙 منوی ری‌استارت", callback_data="rs:menu")],
    ])
    try:
        await q.edit_message_text(
            f"{status} — **{label}**" + NL + NL + f"🕐 `{time.strftime('%H:%M:%S')}`",
            reply_markup=back_kb,
            parse_mode="Markdown",
        )
    except Exception as e:
        log.warning(f"restart status err: {e}")





async def cmd_watchdog(update, context):
    """دستور /watchdog — وضعیت watchog"""
    u = update.effective_user
    if u.id != OWNER_ID:
        return
    
    import subprocess
    msg = update.effective_message
    
    # چک زنده بودن
    try:
        out = subprocess.check_output(
            ["bash", "-c", "ps aux | grep watchdog.py | grep -v grep"],
            timeout=3
        ).decode().strip()
        alive = bool(out)
    except:
        alive = False
    
    # لاگ آخر
    from pathlib import Path
    log_path = Path.home() / "logs" / "watchdog.log"
    log_tail = ""
    if log_path.exists():
        lines = log_path.read_text(errors="ignore").strip().split("\n")
        log_tail = "\n".join(lines[-10:])
    
    text = (
        f"🐕 **Watchdog Status**\n"
        f"{'━'*20}\n"
        f"وضعیت: {'✅ زنده' if alive else '❌ خاموش'}\n\n"
        f"📋 **آخرین ۱۰ خط لاگ:**\n"
        f"```\n{log_tail[:800]}\n```"
    )
    
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    kb = []
    if alive:
        kb.append([InlineKeyboardButton("🔄 ری‌استارت", callback_data="watchdog_restart")])
    else:
        kb.append([InlineKeyboardButton("▶️ استارت", callback_data="watchdog_start")])
    
    await msg.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(kb) if kb else None)


async def cb_watchdog(update, context):
    """callback watchdog"""
    q = update.callback_query
    if q.from_user.id != OWNER_ID:
        await q.answer("⛔", show_alert=True)
        return
    
    import subprocess
    from pathlib import Path
    
    if q.data == "watchdog_start":
        script = 'pkill -9 -f "watchdog.py" 2>/dev/null; sleep 1; : > ~/logs/watchdog.log; setsid python3 -u ~/watchdog.py < /dev/null > ~/logs/watchdog.log 2>&1 &'
        subprocess.Popen(["bash", "-c", script], start_new_session=True)
        await q.answer("▶️ Watchdog استارت شد", show_alert=True)
    elif q.data == "watchdog_restart":
        script = 'pkill -9 -f "watchdog.py" 2>/dev/null; sleep 1; : > ~/logs/watchdog.log; setsid python3 -u ~/watchdog.py < /dev/null > ~/logs/watchdog.log 2>&1 &'
        subprocess.Popen(["bash", "-c", script], start_new_session=True)
        await q.answer("🔄 Watchdog ری‌استارت شد", show_alert=True)
    
    try:
        await q.message.delete()
    except: pass

def register(app):
    from telegram.ext import CommandHandler, CallbackQueryHandler
    app.add_handler(CommandHandler("health", cmd_health), group=-99996)
    app.add_handler(CommandHandler("watchdog", cmd_watchdog), group=-99996)
    app.add_handler(CallbackQueryHandler(cb_watchdog, pattern="^watchdog_"), group=-99996)
    app.add_handler(CommandHandler(["restart_service", "restart"], cmd_restart_service), group=-99996)
    app.add_handler(CallbackQueryHandler(cb_restart_service, pattern="^rs:"), group=-99996)
    try:
        if hasattr(app, 'job_queue') and app.job_queue:
            app.job_queue.run_repeating(
                _health_check, interval=CHECK_INTERVAL, first=120,
                name="health_monitor"
            )
            print("[health_monitor] registered (job_queue, interval=300s)")
        else:
            print("[health_monitor] no job_queue")
    except Exception as e:
        print(f"[health_monitor] reg err: {e}")
