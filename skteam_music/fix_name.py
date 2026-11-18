import py_compile, os, time

FILE = "music_admin.py"
with open(FILE, encoding="utf-8") as f:
    c = f.read()

# ensure_tables
old_e = '        c.execute("CREATE TABLE IF NOT EXISTS sk_group_owners (chat_id INTEGER, user_id INTEGER, added_at INTEGER, PRIMARY KEY (chat_id, user_id))")'
new_e = '''        c.execute("CREATE TABLE IF NOT EXISTS sk_group_owners (chat_id INTEGER, user_id INTEGER, added_at INTEGER, first_name TEXT, username TEXT, PRIMARY KEY (chat_id, user_id))")
        try:
            c.execute("ALTER TABLE sk_group_owners ADD COLUMN first_name TEXT")
        except Exception: pass
        try:
            c.execute("ALTER TABLE sk_group_owners ADD COLUMN username TEXT")
        except Exception: pass'''
if old_e in c:
    c = c.replace(old_e, new_e, 1)
    print("OK ensure_tables")

# add_sk_owner
old_a = '''def add_sk_owner(chat_id, user_id):
    c = _conn()
    c.execute("INSERT OR REPLACE INTO sk_group_owners (chat_id, user_id, added_at) VALUES (?, ?, ?)", (chat_id, user_id, int(time.time())))
    c.commit(); c.close()'''
new_a = '''def add_sk_owner(chat_id, user_id, first_name="", username=""):
    c = _conn()
    c.execute("INSERT OR REPLACE INTO sk_group_owners (chat_id, user_id, added_at, first_name, username) VALUES (?, ?, ?, ?, ?)", (chat_id, user_id, int(time.time()), first_name or "", username or ""))
    c.commit(); c.close()'''
if old_a in c:
    c = c.replace(old_a, new_a, 1)
    print("OK add_sk_owner")

# list_sk_owners
old_l = '''def list_sk_owners(chat_id):
    try:
        c = _conn()
        rows = c.execute("SELECT user_id FROM sk_group_owners WHERE chat_id=?", (chat_id,)).fetchall()
        c.close()
        return [r[0] for r in rows]
    except Exception:
        return []'''
new_l = '''def list_sk_owners(chat_id):
    try:
        c = _conn()
        rows = c.execute("SELECT user_id, first_name, username FROM sk_group_owners WHERE chat_id=?", (chat_id,)).fetchall()
        c.close()
        return rows
    except Exception:
        return []'''
if old_l in c:
    c = c.replace(old_l, new_l, 1)
    print("OK list_sk_owners")

# _reply_target
old_t = '''    return {"user_id": u.id, "first_name": u.first_name}'''
new_t = '''    return {"user_id": u.id, "first_name": u.first_name or "", "username": u.username or ""}'''
if old_t in c:
    c = c.replace(old_t, new_t, 1)
    print("OK _reply_target")

# handler افزودن مالک
old_h = '''            add_sk_owner(chat.id, tgt["user_id"])
            await msg.reply_text("✅ " + (tgt["first_name"] or "کاربر") + " به مالکین اضافه شد")'''
new_h = '''            _fn = tgt.get("first_name") or ""
            _un = tgt.get("username") or ""
            add_sk_owner(chat.id, tgt["user_id"], _fn, _un)
            _disp = ("@" + _un) if _un else _fn
            await msg.reply_text("✅ " + (_disp or "کاربر") + " به مالکین اضافه شد")'''
if old_h in c:
    c = c.replace(old_h, new_h, 1)
    print("OK handler")

# نمایش مالکین
old_d = '''                s = "👑 مالکین:" + NL
                for o in owners:
                    s += "• " + str(o) + NL
                await msg.reply_text(s)'''
new_d = '''                s = "👑 مالکین:" + NL
                for o in owners:
                    _uid = o[0]
                    _fn = o[1] if len(o) > 1 and o[1] else ""
                    _un = o[2] if len(o) > 2 and o[2] else ""
                    if _un:
                        s += "• " + _fn + " (@" + _un + ")" + NL
                    elif _fn:
                        s += "• " + _fn + " [ID: " + str(_uid) + "]" + NL
                    else:
                        s += "• ID: " + str(_uid) + NL
                await msg.reply_text(s)'''
if old_d in c:
    c = c.replace(old_d, new_d, 1)
    print("OK display")

with open(FILE, "w", encoding="utf-8") as f:
    f.write(c)

try:
    py_compile.compile(FILE, doraise=True)
    print("compile OK")
except Exception as e:
    import shutil
    print("ERR: " + str(e))
    shutil.copy(FILE + ".bak_name", FILE)
    print("rollback")
    exit(1)

os.system("pkill -9 -f bot.py")
time.sleep(2)
os.system("bash -c 'cd ~/skteam_music && . ~/groupbot/venv/bin/activate && nohup python3 -u bot.py < /dev/null > logs/stdout.log 2>&1 &'")
time.sleep(10)
print("Music Bot restarted")
