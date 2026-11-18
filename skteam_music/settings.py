"""Panel settings per-chat"""
import sqlite3
from pathlib import Path

BASE = Path(__file__).parent
DB = BASE / "data" / "settings.db"
DB.parent.mkdir(parents=True, exist_ok=True)

DEFAULT = {
    "skin": "sample",
    "refresh_sec": 5,
    "auto_delete_sec": 40,
    "gif_enabled": 1,
}

def _init():
    c = sqlite3.connect(str(DB))
    c.execute("""CREATE TABLE IF NOT EXISTS panel_settings (
        chat_id INTEGER PRIMARY KEY,
        skin TEXT DEFAULT 'sample',
        refresh_sec INTEGER DEFAULT 5,
        auto_delete_sec INTEGER DEFAULT 40,
        gif_enabled INTEGER DEFAULT 1,
        updated_at INTEGER
    )""")
    c.commit()
    c.close()

_init()

def get(chat_id: int, key: str = None):
    c = sqlite3.connect(str(DB))
    r = c.execute("SELECT skin, refresh_sec, auto_delete_sec, gif_enabled FROM panel_settings WHERE chat_id=?",
                  (chat_id,)).fetchone()
    c.close()
    if not r:
        return DEFAULT[key] if key else dict(DEFAULT)
    data = {"skin": r[0], "refresh_sec": r[1], "auto_delete_sec": r[2], "gif_enabled": r[3]}
    return data[key] if key else data

def set_val(chat_id: int, key: str, value):
    import time
    c = sqlite3.connect(str(DB))
    c.execute("INSERT OR IGNORE INTO panel_settings (chat_id) VALUES (?)", (chat_id,))
    if key in ("skin", "refresh_sec", "auto_delete_sec", "gif_enabled"):
        c.execute(f"UPDATE panel_settings SET {key}=?, updated_at=? WHERE chat_id=?",
                  (value, int(time.time()), chat_id))
    c.commit()
    c.close()

def all_chats():
    c = sqlite3.connect(str(DB))
    rows = c.execute("SELECT chat_id FROM panel_settings").fetchall()
    c.close()
    return [r[0] for r in rows]


# ─── Bot Config (Edit Message) ───
def _cfg_init():
    import sqlite3
    c = sqlite3.connect(str(DB))
    c.execute("""CREATE TABLE IF NOT EXISTS bot_config (
        key TEXT PRIMARY KEY,
        value TEXT
    )""")
    c.commit()
    c.close()

_cfg_init()

CFG_DEFAULTS = {
    "welcome_title": "🎵 Sk.Team Music Player",
    "welcome_intro": (
        "سلام 👋\n"
        "من ربات موزیک‌پلیر گروه Sk.Team هستم.\n\n"
        "🎧 قابلیت‌های من:\n"
        "• پخش آهنگ از SoundCloud با کیفیت بالا\n"
        "• صف پخش (تا ۳۰ آهنگ)\n"
        "• اکولایزر، سرعت، تکرار، شافل\n"
        "• پاکسازی پیام‌های گروه\n"
        "• کنترل صدا و میوت\n\n"
        "🎙 ربات رکورد ویس‌کال:\n"
        "• ضبط جلسات ویس‌کال گروه\n"
        "• ارسال به PV مالک گروه\n"
        "• طول کلیپ قابل تنظیم"
    ),
    "footer_contact": "📞 تماس با سازنده: @Siavashska",
    "footer_channel": "📢 کانال Sk.Team: @Skteamchnl",
    "footer_website": "🌐 وب‌سایت: (تعریف نشده)",
    "channel_url": "https://t.me/Skteamchnl",
    "website_url": "",
    "bio_text": "🎵 Sk.Team Music Player — ربات موزیک‌پلیر حرفه‌ای",
    "creator_url": "https://t.me/Siavashska",
}

def get_cfg(key, default=None):
    import sqlite3
    try:
        c = sqlite3.connect(str(DB))
        r = c.execute("SELECT value FROM bot_config WHERE key=?", (key,)).fetchone()
        c.close()
        if r and r[0]:
            return r[0]
        if default is not None:
            return default
        return CFG_DEFAULTS.get(key, "")
    except Exception:
        return default if default is not None else CFG_DEFAULTS.get(key, "")

def set_cfg(key, value):
    import sqlite3, time as _t
    try:
        c = sqlite3.connect(str(DB))
        c.execute("""INSERT OR REPLACE INTO bot_config (key, value) VALUES (?, ?)""",
                  (key, value))
        c.commit()
        c.close()
        return True
    except Exception:
        return False

def get_all_cfg():
    """همه config ها با default"""
    result = dict(CFG_DEFAULTS)
    try:
        import sqlite3
        c = sqlite3.connect(str(DB))
        rows = c.execute("SELECT key, value FROM bot_config").fetchall()
        c.close()
        for k, v in rows:
            if v is not None:
                result[k] = v
    except Exception:
        pass
    return result

# ═══════════════════════════════════════════════
# Global Fallback
# ═══════════════════════════════════════════════
_GB_DB = Path.home() / "groupbot" / "data" / "groupbot.db"


def _get_global(key, default=None):
    """خوندن تنظیم سراسری از groupbot.db"""
    try:
        import sqlite3 as _s
        if not _GB_DB.exists():
            return default
        c = _s.connect(str(_GB_DB), timeout=3)
        r = c.execute("SELECT value FROM global_settings WHERE key=?", (key,)).fetchone()
        c.close()
        return r[0] if r else default
    except Exception:
        return default


def _set_global(key, value):
    """ذخیره تنظیم سراسری در groupbot.db"""
    try:
        import sqlite3 as _s
        import datetime as _dt
        now = _dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c = _s.connect(str(_GB_DB), timeout=3)
        c.execute("INSERT OR REPLACE INTO global_settings (key, value, updated_at) VALUES (?, ?, ?)",
                  (key, str(value), now))
        c.commit()
        c.close()
        return True
    except Exception:
        return False


def get_with_global(chat_id, key):
    """اول per-chat، اگه نبود global"""
    # چک کن per-chat هست
    try:
        c = sqlite3.connect(str(DB))
        r = c.execute("SELECT 1 FROM panel_settings WHERE chat_id=?", (chat_id,)).fetchone()
        c.close()
        if r:
            v = get(chat_id, key)
            if v is not None:
                return v
    except Exception:
        pass
    # fallback به global
    map_key = {
        "skin": "default_skin",
        "refresh_sec": "refresh_sec",
        "auto_delete_sec": "auto_delete_sec",
        "gif_enabled": "gif_enabled",
    }.get(key, key)
    gv = _get_global(map_key)
    if gv is None:
        return DEFAULT.get(key)
    # تبدیل نوع
    if key in ("refresh_sec", "auto_delete_sec", "gif_enabled"):
        try: return int(gv)
        except: return DEFAULT.get(key)
    return gv
