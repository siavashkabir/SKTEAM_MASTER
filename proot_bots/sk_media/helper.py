"""helper.py — مدیریت هلپرها برای مقیاس‌پذیری"""
import os, sqlite3, logging
from pathlib import Path

log = logging.getLogger("helper")
HELPERS_DB = Path("/data/data/com.termux/files/home/groupbot/data/groupbot.db")


def get_active_helpers():
    """برگردوندن همه هلپرهای فعال"""
    try:
        if not HELPERS_DB.exists():
            return []
        c = sqlite3.connect(str(HELPERS_DB), timeout=5)
        rows = c.execute("""SELECT id, name, session_string, api_id, api_hash, groups_count 
                            FROM helpers WHERE enabled=1 
                            ORDER BY groups_count ASC""").fetchall()
        c.close()
        return [
            {"id": r[0], "name": r[1], "session": r[2], 
             "api_id": r[3], "api_hash": r[4], "groups": r[5]}
            for r in rows
        ]
    except Exception as e:
        log.warning(f"get_active_helpers: {e}")
        return []


def get_helper_for_chat(chat_id):
    """کدوم هلپر مسئول این گروهه؟"""
    try:
        c = sqlite3.connect(str(HELPERS_DB), timeout=5)
        r = c.execute("""SELECT h.id, h.name, h.session_string, h.api_id, h.api_hash
                         FROM helpers h
                         INNER JOIN helper_groups hg ON h.id = hg.helper_id
                         WHERE hg.chat_id = ? AND h.enabled = 1
                         LIMIT 1""", (chat_id,)).fetchone()
        c.close()
        if r:
            return {"id": r[0], "name": r[1], "session": r[2], "api_id": r[3], "api_hash": r[4]}
        return None
    except Exception as e:
        log.warning(f"get_helper_for_chat: {e}")
        return None
