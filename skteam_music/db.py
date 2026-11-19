"""db.py — خواندن از groupbot.db + settings.db، با مدیریت بهتر خطا"""
import turso_db as sqlite3
import logging
from pathlib import Path

log = logging.getLogger("skteam_music.db")

GB_DB = Path.home() / "groupbot" / "data" / "groupbot.db"
SK_DB = Path.home() / "skteam_music" / "data" / "settings.db"
OWNER_ID = 7955185125


def _conn_gb():
    """اتصال به groupbot.db با timeout و error logging"""
    try:
        return sqlite3.connect(str(GB_DB), timeout=5)
    except sqlite3.OperationalError as e:
        log.error(f"Cannot connect to {GB_DB}: {e}")
        raise


def _conn_sk():
    """اتصال به settings.db با timeout و error logging"""
    try:
        return sqlite3.connect(str(SK_DB), timeout=5)
    except sqlite3.OperationalError as e:
        log.error(f"Cannot connect to {SK_DB}: {e}")
        raise


def is_owner(uid):
    """بررسی مالک"""
    try:
        return int(uid) == OWNER_ID
    except (ValueError, TypeError):
        return False


def is_sudo(uid):
    """سودو فقط اگه توی bot_admins یا users.is_sudo=1 ثبت شده"""
    try:
        if int(uid) == OWNER_ID:
            return True
    except (ValueError, TypeError):
        return False
    
    c = None
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
                    return True
            except (sqlite3.OperationalError, sqlite3.DatabaseError):
                continue
        return False
    except sqlite3.Error as e:
        log.debug(f"is_sudo check failed for {uid}: {e}")
        return False
    finally:
        if c:
            c.close()


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
    except sqlite3.Error as e:
        log.debug(f"music_authorized check in groupbot failed: {e}")
    
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
    except sqlite3.Error as e:
        log.debug(f"music_authorized check in settings failed: {e}")
    
    return False


def list_group_admins(chat_id):
    """لیست ادمین‌های گروه"""
    try:
        c = _conn_gb()
        rows = c.execute("SELECT user_id FROM admins WHERE chat_id=?", (chat_id,)).fetchall()
        c.close()
        return [r[0] for r in rows] if rows else []
    except sqlite3.Error as e:
        log.error(f"list_group_admins({chat_id}) failed: {e}")
        return []


# ═══════════════════════════════════════════════
# Global settings (از groupbot.db)
# ═══════════════════════════════════════════════
def get_global(key, default=None):
    """دریافت تنظیم سراسری"""
    try:
        c = _conn_gb()
        r = c.execute("SELECT value FROM global_settings WHERE key=?", (key,)).fetchone()
        c.close()
        return r[0] if r else default
    except sqlite3.Error as e:
        log.debug(f"get_global({key}) failed: {e}")
        return default


def set_global(key, value):
    """تعیین تنظیم سراسری"""
    c = None
    try:
        import datetime as _dt
        now = _dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c = _conn_gb()
        c.execute(
            "INSERT OR REPLACE INTO global_settings (key, value, updated_at) VALUES (?, ?, ?)",
            (key, str(value), now)
        )
        c.commit()
        return True
    except sqlite3.IntegrityError as e:
        log.error(f"set_global({key}) integrity error: {e}")
        return False
    except sqlite3.Error as e:
        log.error(f"set_global({key}) failed: {e}")
        return False
    finally:
        if c:
            c.close()


def get_global_int(key, default=0):
    """دریافت تنظیم سراسری به‌عنوان عدد"""
    try:
        val = get_global(key, default)
        return int(val) if val is not None else default
    except (ValueError, TypeError):
        return default


def get_all_bot_admins():
    """لیست همه سودوها"""
    try:
        c = _conn_gb()
        rows = c.execute(
            "SELECT user_id, first_name, username, added_at FROM bot_admins"
        ).fetchall()
        c.close()
        return rows if rows else []
    except sqlite3.Error as e:
        log.error(f"get_all_bot_admins failed: {e}")
        return []


def is_bot_admin(user_id):
    """آیا کاربر سودوئه؟"""
    try:
        c = _conn_gb()
        r = c.execute("SELECT 1 FROM bot_admins WHERE user_id=?", (user_id,)).fetchone()
        c.close()
        return bool(r)
    except sqlite3.Error as e:
        log.debug(f"is_bot_admin({user_id}) failed: {e}")
        return False
