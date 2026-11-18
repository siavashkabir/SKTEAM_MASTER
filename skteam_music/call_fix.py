# call_fix.py
import bot as _bot

try:
    from pathlib import Path as _P
    import sqlite3 as _s
    _db = _P.home() / "skteam_music" / "data" / "settings.db"
    _conn = _s.connect(str(_db), timeout=5)
    _rows = _conn.execute(
        "SELECT first_name, username FROM sk_group_owners WHERE chat_id=?",
        (-1004349813270,)
    ).fetchall()
    _conn.close()
    _extra = ()
    for _fn, _un in _rows:
        if _fn:
            _extra = _extra + (_fn.lower().strip(),)
        if _un:
            _extra = _extra + (_un.lower().strip(),)
    if _extra:
        _bot.CALL_WORDS = _bot.CALL_WORDS + _extra
        print("[CALLFIX] added: " + str(_extra))
except Exception as _e:
    print("[CALLFIX ERR] " + str(_e))
