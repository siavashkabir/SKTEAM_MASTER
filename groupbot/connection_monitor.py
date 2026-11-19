#!/usr/bin/env python3
"""
Connection Monitor - نگهبان اتصال ربات به تلگرام
- چک می‌کنه VPN/اتصال وصل هست یا نه
- اگه وصل شد و ربات اجرا نیست، راه‌اندازی می‌کنه
- اگه ربات گیر کرده، ری‌استارت می‌کنه
"""
import os
import time
import subprocess
import datetime

LOG_FILE = os.path.expanduser("~/groupbot/connection_monitor.log")
BOT_LOG = os.path.expanduser("~/groupbot_bot.log")
BOT_DIR = os.path.expanduser("~/groupbot")
# CHECK_INTERVAL از دیتابیس خونده می‌شه (قابل تنظیم از پنل)
def get_check_interval():
    try:
        import turso_db as sqlite3
        from datetime import datetime
        db_path = os.path.expanduser("~/groupbot/data/groupbot.db")
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("SELECT value FROM settings WHERE chat_id=0 AND setting_name='monitor_interval'")
        r = c.fetchone()
        conn.close()
        if r and r[0]:
            v = int(r[0])
            if 5 <= v <= 300:
                return v
    except Exception:
        pass
    return 10
STUCK_THRESHOLD = 300  # 5 دقیقه بی‌حرکتی = گیر کرده


def log(msg):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def is_telegram_reachable():
    """ping به تلگرام"""
    try:
        r = subprocess.run(
            ["ping", "-c", "1", "-W", "3", "api.telegram.org"],
            capture_output=True, timeout=10
        )
        return r.returncode == 0
    except Exception:
        return False


def is_bot_running():
    try:
        r = subprocess.run(
            ["pgrep", "-f", "main.py"],
            capture_output=True, timeout=5
        )
        return r.returncode == 0
    except Exception:
        return False


def bot_is_stuck():
    """اگه لاگ ربات بیش از STUCK_THRESHOLD ساکن باشه = گیر کرده"""
    try:
        if not os.path.exists(BOT_LOG):
            return False
        mtime = os.path.getmtime(BOT_LOG)
        return (time.time() - mtime) > STUCK_THRESHOLD
    except Exception:
        return False


def start_bot():
    try:
        cmd = (
            f"cd {BOT_DIR} && source venv/bin/activate && "
            f"nohup python3 -u main.py > {BOT_LOG} 2>&1 &"
        )
        subprocess.Popen(cmd, shell=True, executable="/bin/bash")
        log("🚀 ربات راه‌اندازی شد")
        return True
    except Exception as e:
        log(f"❌ خطا در راه‌اندازی: {e}")
        return False


def kill_bot():
    try:
        subprocess.run(
            ["pkill", "-9", "-f", "main.py"],
            capture_output=True, timeout=5
        )
        log("🛑 ربات متوقف شد")
    except Exception:
        pass


def is_monitor_enabled():
    """چک می‌کنه monitor فعاله یا نه"""
    try:
        import turso_db as sqlite3
        db_path = os.path.expanduser("~/groupbot/data/groupbot.db")
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("SELECT value FROM settings WHERE chat_id=0 AND setting_name='sys_monitor_enabled'")
        r = c.fetchone()
        conn.close()
        if r and r[0]:
            return r[0] == "1"
    except Exception:
        pass
    return True


def main():
    log("=" * 50)
    log("Connection Monitor started")
    log(f"Check every {get_check_interval()}s, stuck if no log for {STUCK_THRESHOLD}s")
    log("=" * 50)

    while True:
        try:
            time.sleep(get_check_interval())

            # اگه از پنل خاموش شده، کاری نکن
            if not is_monitor_enabled():
                log("⏸️ monitor خاموشه - از پنل فعالش کن")
                time.sleep(60)
                continue

            reachable = is_telegram_reachable()
            running = is_bot_running()

            if not reachable:
                log("⚠️ تلگرام در دسترس نیست (VPN قطع؟) - منتظر...")
                continue

            # تلگرام OK
            if not running:
                log("ℹ️ تلگرام OK ولی ربات اجرا نیست - راه‌اندازی...")
                start_bot()
                time.sleep(10)
                continue

            # ربات اجرا هست، چک گیر کردن
            if bot_is_stuck():
                log("⚠️ ربات گیر کرده (لاگ ساکن) - ری‌استارت...")
                kill_bot()
                time.sleep(3)
                start_bot()
                time.sleep(10)
            else:
                log("✅ همه چیز OK")

        except Exception as e:
            log(f"خطای حلقه: {e}")


if __name__ == "__main__":
    main()
