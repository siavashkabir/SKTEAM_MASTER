import py_compile, os, time

FILE = "bot.py"
with open(FILE, encoding="utf-8") as f:
    c = f.read()

# ─── ۱. اضافه کردن import music_admin
if "import music_admin" not in c:
    # بعد از اولین import اضافه کن
    import re
    m = re.search(r'(from jokes import [^\n]+\n)', c)
    if m:
        c = c[:m.end()] + "import music_admin as _ma\n" + c[m.end():]
        print("OK import music_admin")

# ─── ۲. اضافه کردن تابع کمکی گرفتن اسم‌های مالکین
helper = '''

def _get_owner_call_names(chat_id):
    """اسم‌های مالکین برای صدا زدن"""
    names = []
    try:
        import sqlite3 as _s
        from pathlib import Path as _P
        _db = _P.home() / "skteam_music" / "data" / "settings.db"
        conn = _s.connect(str(_db), timeout=5)
        rows = conn.execute("SELECT first_name, username FROM sk_group_owners WHERE chat_id=?", (chat_id,)).fetchall()
        conn.close()
        for fn, un in rows:
            if fn: names.append(fn.lower().strip())
            if un: names.append(un.lower().strip())
    except Exception as e:
        import logging
        logging.getLogger("SktTeam").warning("[CALL] " + str(e))
    return names

'''
if "_get_owner_call_names" not in c:
    # قبل از CALL_WORDS اضافه کن
    idx = c.find("CALL_WORDS")
    if idx > 0:
        line_start = c.rfind("\n", 0, idx) + 1
        c = c[:line_start] + helper + c[line_start:]
        print("OK helper اضافه شد")

# ─── ۳. تغییر چک صدا زدن
old_check = '''    if raw in CALL_WORDS or raw.lower() in ("bot", "robot"):'''
new_check = '''    _owner_names = _get_owner_call_names(cid)
    _raw_low = raw.lower().strip()
    if raw in CALL_WORDS or _raw_low in ("bot", "robot") or _raw_low in _owner_names:'''
if old_check in c:
    c = c.replace(old_check, new_check, 1)
    print("OK چک صدا زدن")

# ─── ۴. fix is_music_auth(uid, cid) → (cid, uid)
c = c.replace("is_music_auth(uid, cid)", "is_music_auth(cid, uid)")
c = c.replace("is_music_auth(uid,cid)", "is_music_auth(cid,uid)")

with open(FILE, "w", encoding="utf-8") as f:
    f.write(c)

try:
    py_compile.compile(FILE, doraise=True)
    print("compile OK")
except Exception as e:
    import shutil
    print("ERR: " + str(e))
    shutil.copy(FILE + ".bak", FILE)
    print("rollback")
    exit(1)

os.system("pkill -9 -f bot.py")
time.sleep(2)
os.system("bash -c 'cd ~/skteam_music && . ~/groupbot/venv/bin/activate && nohup python3 -u bot.py < /dev/null > logs/stdout.log 2>&1 &'")
time.sleep(10)
print("restarted")
