# ═══ SK.TEAM Instance Lock ═══
import fcntl as _sk_fcntl
import sys as _sk_sys
import os as _sk_os
from pathlib import Path as _sk_P

_sk_lock_handle = None
def _sk_acquire_lock(_name):
    global _sk_lock_handle
    _sk_lock_path = _sk_P.home() / f".skteam_{_name}.lock"
    try:
        _sk_lock_handle = open(_sk_lock_path, 'w')
        _sk_fcntl.flock(_sk_lock_handle, _sk_fcntl.LOCK_EX | _sk_fcntl.LOCK_NB)
        _sk_lock_handle.write(str(_sk_os.getpid()))
        _sk_lock_handle.flush()
    except (IOError, OSError):
        print(f"[SK-LOCK] Instance '{_name}' already running. Exiting.")
        _sk_sys.exit(0)
# ═══ end lock ═══

from telegram import Update
import importlib
import os
import random

def get_best_proxy():
    proxy_file = os.path.expanduser("~/best_proxies.txt")
    if not os.path.exists(proxy_file):
        return None
    try:
        with open(proxy_file, "r") as f:
            proxies = [line.strip() for line in f if line.strip()]
        if not proxies:
            return None
        return random.choice(proxies)
    except Exception:
        return None

from telegram.ext import Application
from config import BOT_TOKEN
from database import (
    init_db, init_members_table, init_bot_chats_table, init_purge_table,
    init_group_owner_table
)


def load_modules(app):
    modules_dir = "modules"
    for filename in sorted(os.listdir(modules_dir)):
        if filename.endswith(".py") and not filename.startswith("_"):
            module_name = filename[:-3]
            try:
                module = importlib.import_module("modules." + module_name)
                if hasattr(module, "register"):
                    module.register(app)
                    print("OK module " + module_name + " loaded")
                else:
                    print("No register in " + module_name)
            except Exception as e:
                print("Error in " + module_name + ": " + str(e))


# [LOG-WRAPPER-START]
class _LogFakeCtx:
    """context جعلی برای log_event"""
    def __init__(self, bot): self.bot = bot

async def _try_log(bot, action, **kw):
    try:
        from modules.logger import log_event
        ctx = _LogFakeCtx(bot)
        await log_event(ctx, action, **kw)
    except Exception as e:
        print("[LOG WRAP ERR " + str(action) + "] " + str(e))


def main():
    _sk_acquire_lock("manager")
    print("Starting bot...")
    init_db()
    init_members_table()
    init_bot_chats_table()
    init_purge_table()
    init_group_owner_table()
    try:
        from database import init_global_blacklist_tables
        init_global_blacklist_tables()
        print("OK: global blacklist tables initialized")
    except Exception as e:
        print("[GBL INIT ERR] " + str(e))

    try:
        from database import init_spam_tracker_table
        init_spam_tracker_table()
        print("OK: spam_tracker table initialized")
    except Exception as e:
        print("[SPAM INIT ERR] " + str(e))

    try:
        from database import init_voice_call_history_table
        init_voice_call_history_table()
        print("OK: voice_call_history table initialized")
    except Exception as e:
        print("[VCH INIT ERR] " + str(e))

    try:
        from database import init_user_contacts_table
        init_user_contacts_table()
        print("OK: user_contacts table initialized")
    except Exception as e:
        print("[CONTACTS INIT ERR] " + str(e))

    # راه‌اندازی جدول‌های آمار پیام
    try:
        from database import init_msg_stats_tables
        init_msg_stats_tables()
        print("OK: msg stats tables initialized")
    except Exception as _e:
        print("[MSG STATS INIT ERR] " + str(_e))

    # راه‌اندازی جدول رویدادهای گروه
    try:
        from database import init_group_events_table
        init_group_events_table()
        print("OK: group events table initialized")
    except Exception as _e:
        print("[GROUP EVENTS INIT ERR] " + str(_e))

    # راه‌اندازی جدول‌های جوین اجباری
    try:
        from database import init_fj_tables
        init_fj_tables()
        print("OK: FJ tables initialized")
    except Exception as _e:
        print("[FJ INIT ERR] " + str(_e))

    # ساخت اپلیکیشن تلگرام
    app = Application.builder().token(BOT_TOKEN).build()

    # لود کردن ماژول‌ها
    load_modules(app)

    # شروع ربات
    print("Bot is starting polling...")


    # [LOGGER-REG-ONE]
    try:
        from modules.logger import register as register_logger
        register_logger(app)
        # [SYS-STATS-BG]
        try:
            from modules.logger import collect_system_stats
            if hasattr(app, 'job_queue') and app.job_queue:
                app.job_queue.run_repeating(collect_system_stats, interval=300, first=60)
                print("OK system stats job registered (every 5 min)")
        except Exception as _sje:
            print("[SYS STATS JOB ERR] " + str(_sje))

    except Exception as _le:
        print("[LOGGER REG ERR] " + str(_le))

    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
