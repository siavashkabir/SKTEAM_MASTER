#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""افزودن پشتیبانی چند FJ"""
import os, shutil, py_compile, time, re

ts = time.strftime("%H%M%S")
DB = "database.py"
FJ = "modules/force_join.py"
ST = "modules/start.py"
baks = {}

print("="*70)
print("🔧 Multi-FJ: افزودن پشتیبانی چند لینک FJ")
print("="*70)

for f in [DB, FJ, ST]:
    bak = f + ".bak_multifj_" + ts
    shutil.copy(f, bak)
    baks[f] = bak
    print(f"✅ بکاپ: {bak}")

# ═══════════════════════════════════════════════════════════
# ۱. database.py — افزودن توابع
# ═══════════════════════════════════════════════════════════
print("\n" + "─"*70)
print("📄 فایل ۱: database.py")
print("─"*70)

with open(DB, 'r', encoding='utf-8') as f:
    db_content = f.read()

# حذف نسخه قبلی
if "# [MULTI-FJ-START]" in db_content:
    db_content = re.sub(r'# \[MULTI-FJ-START\].*?# \[MULTI-FJ-END\]\s*', '', db_content, flags=re.DOTALL)
    print("ℹ️ نسخه قبلی حذف شد")

new_db_funcs = '''
# [MULTI-FJ-START]
def get_all_global_force_joins():
    """همه لینک‌های FJ سراسری"""
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    try:
        c.execute("SELECT id, target_id, target_link, target_name FROM force_join WHERE chat_id=0 ORDER BY id")
        rows = c.fetchall()
        conn.close()
        return rows
    except Exception as e:
        conn.close()
        print("[GET ALL FJ ERR] " + str(e))
        return []

def add_global_force_join(target_id, target_link, target_name):
    """افزودن لینک FJ جدید (بدون حذف قبلی‌ها)"""
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO force_join (chat_id, force_type, target_id, target_link, target_name) VALUES (0, 'global', ?, ?, ?)",
                  (target_id, target_link, target_name))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print("[ADD FJ ERR] " + str(e))
        conn.close()
        return False

def remove_global_force_join_by_id(fid):
    """حذف یه FJ با ID"""
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    try:
        c.execute("DELETE FROM force_join WHERE id=? AND chat_id=0", (fid,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print("[DEL FJ ID ERR] " + str(e))
        conn.close()
        return False
# [MULTI-FJ-END]

'''

# درج قبل از آخرین خط یا هرجا که مناسب باشه
if "[MULTI-FJ-START]" not in db_content:
    # درج قبل از آخرین تابع یا آخر فایل
    db_content = db_content.rstrip() + "\n\n" + new_db_funcs
    print("✅ توابع multi-FJ اضافه شدند")

with open(DB, 'w', encoding='utf-8') as f:
    f.write(db_content)

# ═══════════════════════════════════════════════════════════
# ۲. force_join.py — middleware + handler
# ═══════════════════════════════════════════════════════════
print("\n" + "─"*70)
print("📄 فایل ۲: force_join.py")
print("─"*70)

with open(FJ, 'r', encoding='utf-8') as f:
    fj_content = f.read()

# حذف نسخه قبلی
if "# [MULTI-FJ-MW-START]" in fj_content:
    fj_content = re.sub(r'# \[MULTI-FJ-MW-START\].*?# \[MULTI-FJ-MW-END\]\s*', '', fj_content, flags=re.DOTALL)

new_mw = '''
# [MULTI-FJ-MW-START]
async def fj_middleware(update, context):
    """چک عضویت در همه FJ ها (چند لینک)"""
    if not update.effective_user:
        return
    user = update.effective_user
    if user.is_bot:
        return
    if update.effective_message and update.effective_message.text and update.effective_message.text.startswith("VCSTAT:"):
        return
    try:
        from database import is_fj_enabled
        if not is_fj_enabled():
            return
    except Exception:
        return
    try:
        from config import OWNER_ID
        if user.id == OWNER_ID:
            return
    except Exception:
        pass
    try:
        from database import is_bot_owner_or_sudo
        if is_bot_owner_or_sudo(user.id):
            return
    except Exception:
        pass
    try:
        from database import is_fj_exempt
        if is_fj_exempt(user.id):
            return
    except Exception:
        pass
    # گرفتن همه FJ ها
    try:
        from database import get_all_global_force_joins
        all_fjs = get_all_global_force_joins()
    except Exception as e:
        print("[FJ MW GET ERR] " + str(e))
        return
    if not all_fjs:
        return
    # چک عضویت در همه
    missing = []
    for fid, tid, tlink, tname in all_fjs:
        try:
            member = await context.bot.get_chat_member(tid, user.id)
            if member.status in ("left", "kicked"):
                missing.append((fid, tid, tlink, tname))
        except Exception as e:
            print("[FJ MW CHK ERR] fid=" + str(fid) + " " + str(e))
            # اگه نمی‌تونیم چک کنیم، skip می‌کنیم
    if not missing:
        return
    # ساخت پیام
    text = ("🔔 برای استفاده از ربات، باید تو این کانال/گروه‌ها عضو بشی:" + NL + NL)
    btns = []
    for fid, tid, tlink, tname in missing:
        text += "• " + (tname or str(tid)) + NL
        if tlink:
            btns.append([InlineKeyboardButton("📢 " + (tname or "عضویت")[:30], url=tlink)])
    btns.append([InlineKeyboardButton("✅ عضو شدم", callback_data="fj_check")])
    try:
        if update.effective_message:
            await update.effective_message.reply_text(text, reply_markup=InlineKeyboardMarkup(btns), disable_web_page_preview=True)
    except Exception as e:
        print("[FJ MW SEND ERR] " + str(e))
    raise ApplicationHandlerStop

async def fj_check_callback(update, context):
    """چک عضویت بعد از کلیک"""
    query = update.callback_query
    user = query.from_user
    try:
        from database import get_all_global_force_joins
        all_fjs = get_all_global_force_joins()
    except Exception as e:
        print("[FJ CB GET ERR] " + str(e))
        await query.answer("خطا", show_alert=True)
        return
    if not all_fjs:
        await query.answer("✅ جوین اجباری تنظیم نشده", show_alert=True)
        return
    missing = []
    for fid, tid, tlink, tname in all_fjs:
        try:
            member = await context.bot.get_chat_member(tid, user.id)
            if member.status in ("left", "kicked"):
                missing.append(tname or str(tid))
        except Exception:
            pass
    if missing:
        await query.answer("❌ هنوز تو اینا عضو نشدی: " + ", ".join(missing), show_alert=True)
        return
    try:
        await query.message.delete()
    except Exception:
        pass
    await query.answer("✅ تایید شد! حالا می‌تونی از ربات استفاده کنی", show_alert=True)
# [MULTI-FJ-MW-END]

'''

# جایگزینی: حذف توابع قدیمی fj_middleware و fj_check_callback
patterns = [
    r'async def fj_middleware\(.*?\n(?=async def|\Z)',
    r'async def fj_check_callback\(.*?\n(?=async def|\Z)',
]
for pat in patterns:
    fj_content = re.sub(pat, '', fj_content, count=1, flags=re.DOTALL)

# اضافه کردن توابع جدید قبل از def register
fj_content = fj_content.replace("def register(app):", new_mw + "def register(app):", 1)
print("✅ fj_middleware و fj_check_callback جایگزین شدند")

# اصلاح fj_link_handler: استفاده از add_global_force_join
old_link = 'set_global_force_join(-1, 0, link, "fj_group")'
new_link = 'add_global_force_join(-1, link, "fj_group")'
if old_link in fj_content:
    fj_content = fj_content.replace(old_link, new_link, 1)
    print("✅ fj_link_handler اصلاح شد")

# اصلاح fallback در fj_link_handler
old_fb = 'set_setting(0, "fj_link", link)\n                set_setting(0, "fj_enabled", "1")'
new_fb = 'from database import add_global_force_join as _agfj\n                _agfj(-1, link, "fj_group")\n                set_setting(0, "fj_enabled", "1")'
if old_fb in fj_content:
    fj_content = fj_content.replace(old_fb, new_fb, 1)
    print("✅ fallback اصلاح شد")

with open(FJ, 'w', encoding='utf-8') as f:
    f.write(fj_content)

# ═══════════════════════════════════════════════════════════
# ۳. start.py — s_fj_menu handler (لیست FJ ها)
# ═══════════════════════════════════════════════════════════
print("\n" + "─"*70)
print("📄 فایل ۳: start.py (s_fj_menu)")
print("─"*70)

with open(ST, 'r', encoding='utf-8') as f:
    st_lines = f.readlines()

# پیدا کردن بلاک s_fj_menu
start = None
for i, l in enumerate(st_lines):
    if l.strip() == 'if action == "s_fj_menu":':
        start = i
        break

if start is None:
    print("⚠️ s_fj_menu پیدا نشد — skip")
else:
    print(f"🎯 s_fj_menu در خط {start+1}")
    # انتهای بلاک
    end = None
    for k in range(start+1, min(start+80, len(st_lines))):
        if st_lines[k].startswith('    if action') and k > start+5:
            end = k
            break
    if end is None:
        end = start + 40
    print(f"🎯 انتهای بلاک: خط {end}")

    # بلاک جدید
    new_block = '''    if action == "s_fj_menu":
        # [MULTI-FJ] نمایش لیست FJ ها
        try:
            from config import OWNER_ID
            from database import is_bot_admin, get_all_global_force_joins, is_fj_enabled
            _o = (query.from_user.id == OWNER_ID)
            _s = False if _o else is_bot_admin(query.from_user.id)
            if not (_o or _s):
                await query.answer("⛔ فقط سازنده و سودو", show_alert=True)
                return
            _en = is_fj_enabled()
            _status = "✅ فعال" if _en else "❌ غیرفعال"
            _fjs = get_all_global_force_joins()
            _txt = "🔒 جوین اجباری" + NL + NL
            _txt += "وضعیت کلی: " + _status + NL
            _txt += "تعداد لینک‌ها: " + str(len(_fjs)) + NL + NL
            _kb = []
            if _fjs:
                _txt += "لینک‌های فعلی:" + NL
                for fid, tid, tlink, tname in _fjs:
                    _nm = (tname or str(tid))[:30]
                    _txt += "• " + _nm + NL
                    _kb.append([InlineKeyboardButton("🗑 " + _nm, callback_data="s_fj_del:" + str(uid) + ":" + str(fid))])
            else:
                _txt += "❌ هیچ لینکی تنظیم نشده" + NL
            _kb.append([InlineKeyboardButton("➕ افزودن لینک جدید", callback_data="s_fj_set:" + str(uid) + ":" + str(chat_id))])
            if _en:
                _kb.append([InlineKeyboardButton("🔴 غیرفعال کردن", callback_data="s_fj_toggle:" + str(uid) + ":" + str(chat_id))])
            else:
                _kb.append([InlineKeyboardButton("🟢 فعال کردن", callback_data="s_fj_toggle:" + str(uid) + ":" + str(chat_id))])
            _kb.append([InlineKeyboardButton("🔙 بازگشت", callback_data="owner_section_back:" + str(uid) + ":" + str(chat_id))])
            await query.edit_message_text(_txt, reply_markup=InlineKeyboardMarkup(_kb))
            reset_timer(context, chat_id, msg_id)
        except Exception as e:
            print("[FJ MENU MULTI ERR] " + str(e))
            try:
                await query.answer("خطا", show_alert=True)
            except Exception:
                pass
        return

'''
    st_lines = st_lines[:start] + [new_block] + st_lines[end:]
    print("✅ s_fj_menu جایگزین شد")

    with open(ST, 'w', encoding='utf-8') as f:
        f.writelines(st_lines)

# ═══════════════════════════════════════════════════════════
# ۴. py_compile هر سه
# ═══════════════════════════════════════════════════════════
print("\n" + "─"*70)
print("🔍 py_compile...")
print("─"*70)
for f in [DB, FJ, ST]:
    try:
        py_compile.compile(f, doraise=True)
        print(f"✅ {f} OK")
    except Exception as e:
        print(f"❌ {f}: {e}")
        for ff, bb in baks.items():
            shutil.copy(bb, ff)
        print("🔄 همه rollback شدند")
        exit(1)

for root, dirs, files in os.walk('.'):
    if 'venv' in root: continue
    if '__pycache__' in root:
        shutil.rmtree(root, ignore_errors=True)

print("\n🔄 ری‌استارت...")
os.system('pkill -9 -f "main.py"')
time.sleep(3)
os.system('cd ~/groupbot && nohup bash bot_watchdog.sh > ~/groupbot_watchdog.log 2>&1 &')
time.sleep(12)
os.system('tail -n 8 ~/groupbot_bot.log')

print("\n" + "="*70)
print("✅ Multi-FJ اضافه شد")
print("="*70)
print(f"""
📌 تست:
   ۱. PV ربات: /setfj https://t.me/chan1
   ۲. PV ربات: /setfj https://t.me/chan2
   ۳. PV ربات: /setfj https://t.me/chan3
   ۴. برو پنل سازنده → 🔒 جوین اجباری
      🟢 باید ۳ لینک با دکمه‌های حذف ببینی
      🟢 دکمه «➕ افزودن لینک جدید» هم هست

🔙 rollback همه:
   cp {baks[DB]} {DB}
   cp {baks[FJ]} {FJ}
   cp {baks[ST]} {ST}
   pkill -9 -f main.py && sleep 3 && nohup bash bot_watchdog.sh > ~/groupbot_watchdog.log 2>&1 &
""")
os.system('tail -F ~/groupbot_bot.log')
