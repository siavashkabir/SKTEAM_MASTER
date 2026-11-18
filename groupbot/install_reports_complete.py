import os, shutil, py_compile, time, sqlite3, re

print("="*80)
print("🔧 نصب کامل سیستم گزارش + تنظیمات آن (یکجا)")
print("="*80)

ts = time.strftime("%H%M%S")
bak_db = f'database.py.bak_rep_{ts}'
bak_start = f'modules/start.py.bak_rep_{ts}'
bak_osg = f'modules/owner_set_group.py.bak_rep_{ts}'
shutil.copy('database.py', bak_db)
shutil.copy('modules/start.py', bak_start)
shutil.copy('modules/owner_set_group.py', bak_osg)
print(f"✅ ۳ بکاپ ساخته شد.")

# ==== 1. جدول reports در DB ====
print("\n=== 1. ساخت جدول reports ===")
try:
    conn = sqlite3.connect('data/groupbot.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER,
            group_title TEXT,
            reporter_id INTEGER,
            reporter_name TEXT,
            reporter_username TEXT,
            reported_user_id INTEGER,
            reported_user_name TEXT,
            reported_user_username TEXT,
            reported_message_id INTEGER,
            reported_message_text TEXT,
            created_at TEXT,
            status TEXT DEFAULT 'pending'
        )
    ''')
    c.execute('CREATE INDEX IF NOT EXISTS idx_reports_gs ON reports(group_id, status)')
    conn.commit()
    conn.close()
    print("✅ جدول reports ساخته شد.")
except Exception as e:
    print(f"❌ {e}")
    exit(1)

# ==== 2. توابع DB ====
print("\n=== 2. اضافه کردن توابع DB ===")
try:
    with open('database.py', 'r', encoding='utf-8') as f:
        db_content = f.read()
    
    if 'def add_report(' not in db_content:
        funcs = '''


# ========== REPORTS SYSTEM ==========
REP_LIMIT_OPTS = [1, 2, 3, 5, 10, 20, 50, 100]
REP_CD_OPTS = [30, 60, 300, 900, 3600, 21600, 86400]


def add_report(gid, gtitle, rep_id, rep_name, rep_user, ru_id, ru_name, ru_user, rmsg_id, rmsg_text):
    try:
        import datetime as _dt
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        c.execute("""INSERT INTO reports 
            (group_id, group_title, reporter_id, reporter_name, reporter_username,
             reported_user_id, reported_user_name, reported_user_username,
             reported_message_id, reported_message_text, created_at, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending')""",
            (gid, gtitle, rep_id, rep_name, rep_user, ru_id, ru_name, ru_user, rmsg_id, rmsg_text,
             _dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        rid = c.lastrowid
        conn.commit()
        conn.close()
        return rid
    except Exception as e:
        print("[ADD REPORT ERR] " + str(e))
        return None


def get_pending_reports(gid, limit=100):
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        c.execute("""SELECT id, group_id, group_title, reporter_id, reporter_name, reporter_username,
                            reported_user_id, reported_user_name, reported_user_username,
                            reported_message_id, reported_message_text, created_at
                     FROM reports WHERE group_id=? AND status='pending'
                     ORDER BY id ASC LIMIT ?""", (gid, limit))
        rows = c.fetchall()
        conn.close()
        return rows
    except Exception as e:
        print("[GET PENDING ERR] " + str(e))
        return []


def count_pending_reports(gid):
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM reports WHERE group_id=? AND status='pending'", (gid,))
        n = c.fetchone()[0]
        conn.close()
        return n
    except Exception:
        return 0


def update_report_status(rid, status):
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        c.execute("UPDATE reports SET status=? WHERE id=?", (status, rid))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print("[UPDATE REPORT ERR] " + str(e))
        return False


def count_user_reports_today(rep_id, gid):
    try:
        import datetime as _dt
        today = _dt.datetime.now().strftime("%Y-%m-%d")
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM reports WHERE reporter_id=? AND group_id=? AND created_at LIKE ?",
                  (rep_id, gid, today + '%'))
        n = c.fetchone()[0]
        conn.close()
        return n
    except Exception:
        return 0


def get_report_settings(cid):
    try:
        dl = int(get_setting(cid, "report_daily_limit", "3") or 3)
    except Exception:
        dl = 3
    try:
        cd = int(get_setting(cid, "report_cooldown", "300") or 300)
    except Exception:
        cd = 300
    return dl, cd


def set_report_daily_limit(cid, value):
    try:
        set_setting(cid, "report_daily_limit", str(int(value)))
        return True
    except Exception:
        return False


def set_report_cooldown(cid, value):
    try:
        set_setting(cid, "report_cooldown", str(int(value)))
        return True
    except Exception:
        return False


def fmt_rep_cd(seconds):
    try:
        s = int(seconds)
    except Exception:
        return str(seconds)
    if s < 60:
        return f"{s} ثانیه"
    if s < 3600:
        return f"{s // 60} دقیقه"
    if s < 86400:
        return f"{s // 3600} ساعت"
    return f"{s // 86400} روز"
'''
        db_content = db_content.rstrip() + funcs + '\n'
        with open('database.py', 'w', encoding='utf-8') as f:
            f.write(db_content)
        print("✅ توابع DB اضافه شدند.")
    
    py_compile.compile('database.py', doraise=True)
except Exception as e:
    print(f"❌ {e}")
    shutil.copy(bak_db, 'database.py')
    exit(1)

# ==== 3. ایجاد modules/reports.py ====
print("\n=== 3. ساخت modules/reports.py ===")
reports_code = '''"""گزارش مخفی پیام‌ها"""
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions
from telegram.ext import ContextTypes, MessageHandler, CallbackQueryHandler, filters, ApplicationHandlerStop
from config import OWNER_ID
from database import (
    is_group_owner, add_report, get_pending_reports,
    count_pending_reports, update_report_status, count_user_reports_today,
    get_report_settings
)

_REPORT_COOLDOWN = {}


def _is_report_trigger(text):
    if not text:
        return False
    return text.strip().lower() in ("report", "گزارش", "/report", "/گزارش")


async def _auto_del(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    try:
        await context.bot.delete_message(chat_id=job.chat_id, message_id=job.data)
    except Exception:
        pass


async def handle_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    if not msg or not chat or not user:
        return
    if chat.type not in ("group", "supergroup"):
        return
    if not msg.text or not _is_report_trigger(msg.text):
        return
    
    if not msg.reply_to_message:
        try:
            w = await msg.reply_text("⚠️ برای گزارش، روی پیام مورد نظر ریپلای کنید و بنویسید report")
            context.job_queue.run_once(_auto_del, 5, chat_id=chat.id, data=w.message_id,
                                        name=f"rw_{w.message_id}")
        except Exception:
            pass
        raise ApplicationHandlerStop
    
    try:
        await msg.delete()
    except Exception:
        pass
    
    key = (user.id, chat.id)
    now = time.time()
    last = _REPORT_COOLDOWN.get(key, 0)
    
    try:
        _dl, _cd = get_report_settings(chat.id)
    except Exception:
        _dl, _cd = 3, 300
    
    if now - last < _cd:
        try:
            w = await context.bot.send_message(
                chat_id=user.id,
                text=f"⏳ لطفاً {int(_cd - (now - last))} ثانیه دیگر صبر کنید."
            )
            context.job_queue.run_once(_auto_del, 5, chat_id=user.id, data=w.message_id,
                                        name=f"rcd_{w.message_id}")
        except Exception:
            pass
        raise ApplicationHandlerStop
    
    today_count = count_user_reports_today(user.id, chat.id)
    if today_count >= _dl:
        try:
            w = await context.bot.send_message(
                chat_id=user.id,
                text=f"⛔ سهمیه گزارش روزانه شما ({_dl} مورد) تمام شده است."
            )
            context.job_queue.run_once(_auto_del, 8, chat_id=user.id, data=w.message_id,
                                        name=f"rlim_{w.message_id}")
        except Exception:
            pass
        raise ApplicationHandlerStop
    
    rmsg = msg.reply_to_message
    ruser = rmsg.from_user
    rtext = rmsg.text or rmsg.caption or "[بدون متن]"
    
    if ruser and ruser.id == user.id:
        try:
            w = await context.bot.send_message(chat_id=user.id, text="⚠️ نمی‌توانید پیام خودتان را گزارش کنید.")
            context.job_queue.run_once(_auto_del, 5, chat_id=user.id, data=w.message_id,
                                        name=f"rself_{w.message_id}")
        except Exception:
            pass
        raise ApplicationHandlerStop
    
    rid = add_report(chat.id, chat.title or str(chat.id),
                     user.id, user.full_name or "-", user.username or "-",
                     ruser.id if ruser else 0,
                     ruser.full_name if ruser else "-",
                     ruser.username if ruser else "-",
                     rmsg.message_id, rtext[:500])
    
    _REPORT_COOLDOWN[key] = now
    if not rid:
        raise ApplicationHandlerStop
    
    try:
        conn = sqlite3.connect('data/groupbot.db')
        c = conn.cursor()
        c.execute("SELECT user_id FROM group_owners WHERE chat_id=?", (chat.id,))
        owners = [r[0] for r in c.fetchall()]
        conn.close()
    except Exception:
        owners = []
    
    pending = count_pending_reports(chat.id)
    for oid in owners:
        try:
            kb = InlineKeyboardMarkup([[
                InlineKeyboardButton(f"📬 مشاهده گزارش‌ها ({pending})",
                                     callback_data=f"rep_view:{chat.id}:0")
            ]])
            await context.bot.send_message(
                chat_id=oid,
                text=f"🔔 گزارش جدید در گروه «{chat.title}»\\n\\n📊 تعداد: {pending}",
                reply_markup=kb,
                disable_notification=True
            )
        except Exception as e:
            print(f"[NOTIFY ERR] {e}")
    
    print(f"[REPORT] id={rid} group={chat.id} by={user.id}")
    raise ApplicationHandlerStop


async def _build_view(gid, offset):
    reports = get_pending_reports(gid, limit=100)
    if not reports:
        return None, None
    if offset >= len(reports):
        offset = len(reports) - 1
    if offset < 0:
        offset = 0
    r = reports[offset]
    (rid, _, gtitle, rep_id, rep_name, rep_user, ru_id, ru_name, ru_user, rmsg_id, rtext, created) = r
    total = len(reports)
    text = (
        f"🚨 گزارش #{rid}  ({offset+1} از {total})\\n"
        f"━━━━━━━━━━━━━━━━━━━━\\n"
        f"🏠 گروه: {gtitle}\\n"
        f"📅 تاریخ: {created}\\n\\n"
        f"👮 گزارش‌دهنده:\\n"
        f"   نام: {rep_name}\\n"
        f"   یوزرنیم: @{rep_user}\\n"
        f"   آیدی: {rep_id}\\n\\n"
        f"👤 فرستنده پیام:\\n"
        f"   نام: {ru_name}\\n"
        f"   یوزرنیم: @{ru_user}\\n"
        f"   آیدی: {ru_id}\\n\\n"
        f"📝 متن پیام:\\n{rtext}"
    )
    nav = []
    if offset > 0:
        nav.append(InlineKeyboardButton("⬅️ قبلی", callback_data=f"rep_view:{gid}:{offset-1}"))
    if offset < total - 1:
        nav.append(InlineKeyboardButton("➡️ بعدی", callback_data=f"rep_view:{gid}:{offset+1}"))
    rows = [
        [InlineKeyboardButton("🗑 حذف پیام", callback_data=f"rep_del:{gid}:{rid}:{rmsg_id}:{offset}"),
         InlineKeyboardButton("🚫 سکوت 1ساعت", callback_data=f"rep_mute:{gid}:{rid}:{ru_id}:{offset}")],
        [InlineKeyboardButton("🔨 بن", callback_data=f"rep_ban:{gid}:{rid}:{ru_id}:{offset}")],
        [InlineKeyboardButton("✅ رسیدگی", callback_data=f"rep_done:{gid}:{rid}:{offset}"),
         InlineKeyboardButton("❌ نادیده", callback_data=f"rep_ign:{gid}:{rid}:{offset}")],
    ]
    if nav:
        rows.append(nav)
    rows.append([InlineKeyboardButton("🔙 بستن", callback_data=f"rep_close:{gid}:0")])
    return text, InlineKeyboardMarkup(rows)


async def handle_report_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    data = query.data
    parts = data.split(":")
    action = parts[0]
    await query.answer()
    
    if action == "rep_close":
        try:
            await query.edit_message_text("📪 بسته شد.")
        except Exception:
            pass
        return
    
    if action == "rep_view":
        gid = int(parts[1])
        offset = int(parts[2])
        if not is_group_owner(gid, user.id) and user.id != OWNER_ID:
            await query.answer("⛔ فقط مالک گروه.", show_alert=True)
            return
        text, kb = await _build_view(gid, offset)
        if not text:
            try:
                await query.edit_message_text("✅ گزارش رسیدگی‌نشده‌ای نیست.")
            except Exception:
                pass
            return
        try:
            await query.edit_message_text(text, reply_markup=kb)
        except Exception:
            pass
        return
    
    if len(parts) < 4:
        return
    gid = int(parts[1])
    rid = int(parts[2])
    if not is_group_owner(gid, user.id) and user.id != OWNER_ID:
        await query.answer("⛔ فقط مالک گروه.", show_alert=True)
        return
    
    offset = 0
    
    if action == "rep_del":
        msg_id = int(parts[3])
        offset = int(parts[4]) if len(parts) > 4 else 0
        try:
            await context.bot.delete_message(chat_id=gid, message_id=msg_id)
            await query.answer("✅ حذف شد.", show_alert=True)
        except Exception as e:
            await query.answer(f"⚠️ {str(e)[:50]}", show_alert=True)
    elif action == "rep_mute":
        uid = int(parts[3])
        offset = int(parts[4]) if len(parts) > 4 else 0
        import datetime as _dt
        try:
            await context.bot.restrict_chat_member(
                chat_id=gid, user_id=uid,
                permissions=ChatPermissions(can_send_messages=False),
                until_date=_dt.datetime.now() + _dt.timedelta(hours=1)
            )
            await query.answer("✅ 1ساعت سکوت شد.", show_alert=True)
        except Exception as e:
            await query.answer(f"⚠️ {str(e)[:50]}", show_alert=True)
    elif action == "rep_ban":
        uid = int(parts[3])
        offset = int(parts[4]) if len(parts) > 4 else 0
        try:
            await context.bot.ban_chat_member(chat_id=gid, user_id=uid)
            await query.answer("✅ بن شد.", show_alert=True)
        except Exception as e:
            await query.answer(f"⚠️ {str(e)[:50]}", show_alert=True)
    elif action == "rep_done":
        offset = int(parts[3]) if len(parts) > 3 else 0
        await query.answer("✅ رسیدگی شد.")
    elif action == "rep_ign":
        offset = int(parts[3]) if len(parts) > 3 else 0
        await query.answer("❌ نادیده گرفته شد.")
    
    update_report_status(rid, 'resolved' if action != "rep_ign" else 'ignored')
    text, kb = await _build_view(gid, offset)
    if text:
        try:
            await query.edit_message_text(text, reply_markup=kb)
        except Exception:
            pass
    else:
        try:
            await query.edit_message_text("✅ همه گزارش‌ها رسیدگی شدند.")
        except Exception:
            pass


def register(app):
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_report, block=False),
        group=-45
    )
    app.add_handler(
        CallbackQueryHandler(handle_report_callback, pattern=r"^rep_"),
        group=-44
    )
    print("OK module reports loaded")
'''
with open('modules/reports.py', 'w', encoding='utf-8') as f:
    f.write(reports_code)
py_compile.compile('modules/reports.py', doraise=True)
print("✅ modules/reports.py ساخته شد.")

# ==== 4. اتصال به start.py ====
print("\n=== 4. اتصال به start.py ===")
try:
    with open('modules/start.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    reg_idx = None
    for i, line in enumerate(lines):
        if line.startswith('def register(app):'):
            reg_idx = i
            break
    
    if reg_idx is None:
        print("❌ def register(app) پیدا نشد!")
        raise Exception("register not found")
    
    end_idx = len(lines)
    for j in range(reg_idx + 1, len(lines)):
        if lines[j] and not lines[j][0].isspace() and lines[j].strip():
            end_idx = j
            break
    
    already = any('register_reports' in lines[k] for k in range(reg_idx, end_idx))
    if not already:
        insert = [
            '    # Reports System\n',
            '    try:\n',
            '        from modules.reports import register as register_reports\n',
            '        register_reports(app)\n',
            '    except Exception as _re:\n',
            '        print("[REPORTS REG ERR] " + str(_re))\n',
        ]
        lines = lines[:end_idx] + insert + lines[end_idx:]
        print(f"✅ register_reports اضافه شد (خط {end_idx+1}).")
    else:
        print("⚠️ از قبل اضافه شده.")
    
    with open('modules/start.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    py_compile.compile('modules/start.py', doraise=True)
    print("✅ start.py کامپایل شد.")
except Exception as e:
    print(f"❌ {e}")
    shutil.copy(bak_db, 'database.py')
    shutil.copy(bak_start, 'modules/start.py')
    if os.path.exists('modules/reports.py'):
        os.remove('modules/reports.py')
    exit(1)

# ==== 5. اضافه کردن تنظیمات به owner_set_group.py ====
print("\n=== 5. اضافه کردن تنظیمات گزارش به پنل ===")
try:
    with open('modules/owner_set_group.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # --- 5.1: ایمپورت ---
    if 'get_report_settings' not in content.split('def ')[0]:
        # اضافه کردن به انتهای اولین بلوک import
        imp_match = re.search(r'(from database import [^\n]*(?:\n\s+[^\n]*)*\n)', content)
        if imp_match and 'get_report_settings' not in imp_match.group(1):
            old_imp = imp_match.group(1)
            new_imp = old_imp.rstrip() + ',\n    get_report_settings, set_report_daily_limit, set_report_cooldown, fmt_rep_cd, REP_LIMIT_OPTS, REP_CD_OPTS\n'
            content = content.replace(old_imp, new_imp, 1)
            print("✅ ایمپورت اضافه شد.")
    
    # --- 5.2: دکمه‌ها ---
    back_btn_pattern = r'([ \t]*\[InlineKeyboardButton\("🔙 بازگشت", callback_data=f"timer_back:(\{uid\}):(\{chat_id\})"\)\],)'
    m = re.search(back_btn_pattern, content)
    if m and 'owner_rep_dl' not in content.split('def ')[0]:
        indent = ' ' * (len(m.group(1)) - len(m.group(1).lstrip()))
        new_btns = (
            f'{indent}[InlineKeyboardButton(f"📊 سهمیه روزانه گزارش: {{get_report_settings(chat_id)[0]}}", callback_data=f"owner_rep_dl:{{uid}}:{{chat_id}}")],\n'
            f'{indent}[InlineKeyboardButton(f"⏱ فاصله بین گزارش‌ها: {{fmt_rep_cd(get_report_settings(chat_id)[1])}}", callback_data=f"owner_rep_cd:{{uid}}:{{chat_id}}")],\n'
        )
        content = content.replace(m.group(1), new_btns + m.group(1), 1)
        print("✅ ۲ دکمه به منو اضافه شد.")
    else:
        print("⚠️ دکمه‌ها از قبل یا الگو پیدا نشد.")
    
    # --- 5.3: هندلرها ---
    anchor = 'if action == "timer_back":'
    if anchor in content and 'action == "owner_rep_dl"' not in content:
        anchor_idx = content.find(anchor)
        # indent از anchor
        line_start = content.rfind('\n', 0, anchor_idx) + 1
        indent = content[line_start:anchor_idx]
        hi = indent
        hib = indent + '    '
        
        handlers = (
            f'{hi}if action == "owner_rep_dl":\n'
            f'{hib}try:\n'
            f'{hib}    cur = get_report_settings(chat_id)[0]\n'
            f'{hib}    try:\n'
            f'{hib}        i = REP_LIMIT_OPTS.index(cur)\n'
            f'{hib}    except ValueError:\n'
            f'{hib}        i = 0\n'
            f'{hib}    new = REP_LIMIT_OPTS[(i + 1) % len(REP_LIMIT_OPTS)]\n'
            f'{hib}    set_report_daily_limit(chat_id, new)\n'
            f'{hib}    try:\n'
            f'{hib}        await _safe_edit(query, "⚙️ تنظیمات این گروه", reply_markup=_build_menu(uid, chat_id))\n'
            f'{hib}    except Exception:\n'
            f'{hib}        pass\n'
            f'{hib}    await query.answer(f"✅ سهمیه: {{new}} گزارش")\n'
            f'{hib}except Exception as e:\n'
            f'{hib}    print("[REP_DL ERR] " + str(e))\n'
            f'{hib}return\n\n'
            f'{hi}if action == "owner_rep_cd":\n'
            f'{hib}try:\n'
            f'{hib}    cur = get_report_settings(chat_id)[1]\n'
            f'{hib}    try:\n'
            f'{hib}        i = REP_CD_OPTS.index(cur)\n'
            f'{hib}    except ValueError:\n'
            f'{hib}        i = 0\n'
            f'{hib}    new = REP_CD_OPTS[(i + 1) % len(REP_CD_OPTS)]\n'
            f'{hib}    set_report_cooldown(chat_id, new)\n'
            f'{hib}    try:\n'
            f'{hib}        await _safe_edit(query, "⚙️ تنظیمات این گروه", reply_markup=_build_menu(uid, chat_id))\n'
            f'{hib}    except Exception:\n'
            f'{hib}        pass\n'
            f'{hib}    await query.answer(f"✅ فاصله: {{fmt_rep_cd(new)}}")\n'
            f'{hib}except Exception as e:\n'
            f'{hib}    print("[REP_CD ERR] " + str(e))\n'
            f'{hib}return\n\n'
        )
        content = content.replace(anchor, handlers + anchor, 1)
        print("✅ ۲ هندلر اضافه شد.")
    
    with open('modules/owner_set_group.py', 'w', encoding='utf-8') as f:
        f.write(content)
    py_compile.compile('modules/owner_set_group.py', doraise=True)
    print("✅ owner_set_group.py کامپایل شد.")
except Exception as e:
    print(f"❌ {e}")
    import traceback
    traceback.print_exc()
    shutil.copy(bak_osg, 'modules/owner_set_group.py')
    exit(1)

# ==== 6. ری‌استارت ====
print("\n=== 6. ری‌استارت ربات ===")
os.system('pkill -9 -f "main.py"')
time.sleep(3)
os.system('cd ~/groupbot && bash -c "source venv/bin/activate && nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 &"')
time.sleep(8)
os.system('tail -n 12 ~/groupbot_bot.log')

print("\n" + "="*80)
print("✅ نصب کامل شد!")
print("="*80)
print("""
📌 نحوه استفاده:
   ۱. کاربر روی پیام → ریپلای → report یا گزارش
   ۲. پیامش فوراً پاک میشه (مخفی)
   ۳. به پیوی مالک: «🔔 گزارش جدید»
   ۴. مالک روی «📬 مشاهده گزارش‌ها» می‌زنه
   ۵. دکمه‌ها: 🗑 حذف / 🚫 سکوت / 🔨 بن / ✅ رسیدگی / ❌ نادیده

📌 تنظیمات (منوی مالک گروه → تنظیمات این گروه):
   • 📊 سهمیه روزانه گزارش (1-100)
   • ⏱ فاصله بین گزارش‌ها (30s تا 24h)
""")
