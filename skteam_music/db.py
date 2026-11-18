"""db.py — خواندن از groupbot.db + settings.db"""
import sqlite3
from pathlib import Path

GB_DB = Path.home() / "groupbot" / "data" / "groupbot.db"
SK_DB = Path.home() / "skteam_music" / "data" / "settings.db"
OWNER_ID = 7955185125


def _conn_gb():
    return sqlite3.connect(str(GB_DB), timeout=5)


def _conn_sk():
    return sqlite3.connect(str(SK_DB), timeout=5)


def is_owner(uid):
    try:
        return int(uid) == OWNER_ID
    except:
        return False


def is_sudo(uid):
    """سودو فقط اگه توی bot_admins یا users.is_sudo=1 ثبت شده"""
    try:
        if int(uid) == OWNER_ID:
            return True
    except:
        return False
    try:
        c = _conn_gb()
        # جدول bot_admins (اصلی)
        for sql in [
            "SELECT 1 FROM bot_admins WHERE user_id=? LIMIT 1",
            "SELECT 1 FROM users WHERE user_id=? AND is_sudo=1 LIMIT 1",
            "SELECT 1 FROM sudo_users WHERE user_id=? LIMIT 1",
        ]:
            try:
                r = c.execute(sql, (uid,)).fetchone()
                if r:
                    c.close()
                    return True
            except Exception:
                continue
        c.close()
        return False
    except Exception:
        return False


def is_music_authorized(chat_id, uid):
    """چک از هر دو DB"""
    import time
    now = int(time.time())
    # ۱. groupbot.db
    try:
        c = _conn_gb()
        r = c.execute(
            "SELECT until_ts FROM music_authorized WHERE chat_id=? AND user_id=?",
            (chat_id, uid),
        ).fetchone()
        c.close()
        if r:
            until = int(r[0] or 0)
            if until == 0 or until > now:
                return True
    except Exception:
        pass
    # ۲. settings.db
    try:
        c = _conn_sk()
        r = c.execute(
            "SELECT until_ts FROM music_authorized WHERE chat_id=? AND user_id=?",
            (chat_id, uid),
        ).fetchone()
        c.close()
        if r:
            until = int(r[0] or 0)
            if until == 0 or until > now:
                return True
    except Exception:
        pass
    return False


def list_group_admins(chat_id):
    try:
        c = _conn_gb()
        rows = c.execute("SELECT user_id FROM admins WHERE chat_id=?", (chat_id,)).fetchall()
        c.close()
        return [r[0] for r in rows]
    except Exception:
        return []

# ═══════════════════════════════════════════════
# Global settings (از groupbot.db)
# ═══════════════════════════════════════════════
def get_global(key, default=None):
    try:
        c = _conn_gb()
        r = c.execute("SELECT value FROM global_settings WHERE key=?", (key,)).fetchone()
        c.close()
        return r[0] if r else default
    except Exception:
        return default


def set_global(key, value):
    try:
        import datetime as _dt
        now = _dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c = _conn_gb()
        c.execute("INSERT OR REPLACE INTO global_settings (key, value, updated_at) VALUES (?, ?, ?)",
                  (key, str(value), now))
        c.commit()
        c.close()
        return True
    except Exception as e:
        print("[db.set_global] " + str(e))
        return False


def get_global_int(key, default=0):
    try:
        return int(get_global(key, default) or default)
    except:
        return default

def get_all_bot_admins():
    """لیست همه سودوها"""
    try:
        c = _conn_gb()
        rows = c.execute("SELECT user_id, first_name, username, added_at FROM bot_admins").fetchall()
        c.close()
        return rows
    except Exception:
        return []


def is_bot_admin(user_id):
    """آیا کاربر سودوئه؟"""
    try:
        c = _conn_gb()
        r = c.execute("SELECT 1 FROM bot_admins WHERE user_id=?", (user_id,)).fetchone()
        c.close()
        return bool(r)
    except Exception:
        return False
