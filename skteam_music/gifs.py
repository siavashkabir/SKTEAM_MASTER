"""مدیریت GIF های پلیر برای هر گروه"""
import sqlite3, time
from pathlib import Path

BASE = Path(__file__).parent
DB = BASE / "data" / "settings.db"
DB.parent.mkdir(parents=True, exist_ok=True)

def _init():
    c = sqlite3.connect(str(DB))
    c.execute("""CREATE TABLE IF NOT EXISTS chat_gifs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id INTEGER,
        file_id TEXT,
        name TEXT,
        added_by INTEGER,
        added_at INTEGER,
        is_active INTEGER DEFAULT 0
    )""")
    c.commit()
    c.close()

_init()

def add(chat_id, file_id, name, uid):
    """اضافه کردن گیف جدید. اگه اولین گیف گروه باشه، فعال می‌شه."""
    c = sqlite3.connect(str(DB))
    count = c.execute("SELECT COUNT(*) FROM chat_gifs WHERE chat_id=?", (chat_id,)).fetchone()[0]
    is_active = 1 if count == 0 else 0
    cur = c.execute(
        "INSERT INTO chat_gifs (chat_id, file_id, name, added_by, added_at, is_active) VALUES (?,?,?,?,?,?)",
        (chat_id, file_id, name[:40], uid, int(time.time()), is_active)
    )
    gid = cur.lastrowid
    c.commit()
    c.close()
    return gid

def list_all(chat_id):
    c = sqlite3.connect(str(DB))
    rows = c.execute(
        "SELECT id, file_id, name, added_by, added_at, is_active FROM chat_gifs WHERE chat_id=? ORDER BY id DESC",
        (chat_id,)
    ).fetchall()
    c.close()
    return [
        {"id": r[0], "file_id": r[1], "name": r[2], "added_by": r[3], "added_at": r[4], "is_active": bool(r[5])}
        for r in rows
    ]

def get(chat_id, gif_id):
    c = sqlite3.connect(str(DB))
    r = c.execute("SELECT id, file_id, name, is_active FROM chat_gifs WHERE chat_id=? AND id=?",
                  (chat_id, gif_id)).fetchone()
    c.close()
    if not r: return None
    return {"id": r[0], "file_id": r[1], "name": r[2], "is_active": bool(r[3])}

def delete(chat_id, gif_id):
    c = sqlite3.connect(str(DB))
    row = c.execute("SELECT is_active FROM chat_gifs WHERE chat_id=? AND id=?",
                    (chat_id, gif_id)).fetchone()
    c.execute("DELETE FROM chat_gifs WHERE chat_id=? AND id=?", (chat_id, gif_id))
    # اگه فعال بود، اولی رو فعال کن
    if row and row[0]:
        first = c.execute("SELECT id FROM chat_gifs WHERE chat_id=? ORDER BY id LIMIT 1",
                          (chat_id,)).fetchone()
        if first:
            c.execute("UPDATE chat_gifs SET is_active=1 WHERE id=?", (first[0],))
    c.commit()
    c.close()

def set_active(chat_id, gif_id):
    c = sqlite3.connect(str(DB))
    c.execute("UPDATE chat_gifs SET is_active=0 WHERE chat_id=?", (chat_id,))
    c.execute("UPDATE chat_gifs SET is_active=1 WHERE chat_id=? AND id=?", (chat_id, gif_id))
    c.commit()
    c.close()

def active(chat_id):
    c = sqlite3.connect(str(DB))
    r = c.execute("SELECT id, file_id, name FROM chat_gifs WHERE chat_id=? AND is_active=1 LIMIT 1",
                  (chat_id,)).fetchone()
    c.close()
    if not r: return None
    return {"id": r[0], "file_id": r[1], "name": r[2]}

def count(chat_id):
    c = sqlite3.connect(str(DB))
    n = c.execute("SELECT COUNT(*) FROM chat_gifs WHERE chat_id=?", (chat_id,)).fetchone()[0]
    c.close()
    return n
