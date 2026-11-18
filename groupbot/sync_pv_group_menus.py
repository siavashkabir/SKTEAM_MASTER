import os, shutil, py_compile, time, re

print("="*80)
print("🔧 هماهنگ‌سازی منوی PV با منوی گروه (یکجا)")
print("="*80)

ts = time.strftime("%H%M%S")

# ============================================================
# 1. بکاپ هر دو فایل
# ============================================================
bak_pv = f'modules/pv_main.py.bak_sync_{ts}'
bak_st = f'modules/start.py.bak_sync_{ts}'
shutil.copy('modules/pv_main.py', bak_pv)
shutil.copy('modules/start.py', bak_st)
print(f"✅ بکاپ pv_main.py: {bak_pv}")
print(f"✅ بکاپ start.py: {bak_st}")

# ============================================================
# 2. اصلاح pv_main.py
# ============================================================
print("\n=== 1. اصلاح pv_main.py ===")

with open('modules/pv_main.py', 'r', encoding='utf-8') as f:
    pv_content = f.read()

# --- 2.1: هندلر op_back در pv_owner_callbacks ---
# پیدا کردن بلوک کامل op_back
old_op_back_pattern = re.compile(
    r'    if action == "op_back":.*?(?=\n    if action ==|\n    raise ApplicationHandlerStop|\n    return\n)',
    re.DOTALL
)

new_op_back = '''    if action == "op_back":
        try:
            from modules.start import sudo_panel_menu, owner_section_menu, group_owner_panel_menu
            from config import OWNER_ID
            from database import is_bot_admin, is_group_owner
            # چک: آیا کاربر سازنده یا سودو است؟
            is_sudo_user = (user.id == OWNER_ID)
            if not is_sudo_user:
                try:
                    is_sudo_user = is_bot_admin(user.id)
                except Exception:
                    pass
            if is_sudo_user:
                # نمایش منوی اصلی (sudo)
                await query.edit_message_text(
                    "👑 منوی اصلی - بخش مورد نظر:",
                    reply_markup=sudo_panel_menu(user.id, group_chat_id or 0)
                )
            else:
                # نمایش منوی مالک گروه
                from config import DATABASE_PATH
                import sqlite3
                conn = sqlite3.connect(DATABASE_PATH)
                cur = conn.cursor()
                cur.execute("SELECT chat_id FROM groups")
                all_groups = [r[0] for r in cur.fetchall()]
                conn.close()
                target_group = group_chat_id
                if not target_group:
                    for gid in all_groups:
                        try:
                            if is_group_owner(gid, user.id):
                                target_group = gid
                                break
                        except Exception:
                            continue
                await query.edit_message_text(
                    "👑 به پنل مدیریت گروه خود خوش آمدید. روی دکمه‌های زیر کلیک کنید:",
                    reply_markup=group_owner_panel_menu(user.id, target_group)
                )
            _schedule_delete(context, chat.id)
        except Exception as e:
            print("[PV OP_BACK ERR] " + str(e))
            import traceback
            traceback.print_exc()
        return
'''

if 'if action == "op_back"' in pv_content:
    pv_content = old_op_back_pattern.sub(new_op_back, pv_content, count=1)
    print("   ✅ هندلر op_back بازنویسی شد.")

# --- 2.2: اضافه کردن هندلر owner_section_menu ---
if 'if action == "owner_section_menu"' not in pv_content:
    # پیدا کردن `if action == "op_manage":` برای درج قبلش
    anchor = '    if action == "op_manage":'
    if anchor in pv_content:
        section_handler = '''    if action == "owner_section_menu":
        try:
            from modules.start import owner_section_menu
            await query.edit_message_text(
                "🔧 بخش سازنده\\n\\nگزینه مورد نظر را انتخاب کنید:",
                reply_markup=owner_section_menu(user.id, group_chat_id or 0)
            )
            _schedule_delete(context, chat.id)
        except Exception as e:
            print("[PV SECTION ERR] " + str(e))
        return

'''
        pv_content = pv_content.replace(anchor, section_handler + anchor, 1)
        print("   ✅ هندلر owner_section_menu اضافه شد.")

# --- 2.3: اضافه کردن هندلر sudo_panel_back (اختیاری) ---
if 'if action == "sudo_panel_back"' not in pv_content:
    anchor = '    if action == "op_manage":'
    if anchor in pv_content:
        back_handler = '''    if action == "sudo_panel_back":
        try:
            from modules.start import sudo_panel_menu
            await query.edit_message_text(
                "👑 منوی اصلی - بخش مورد نظر:",
                reply_markup=sudo_panel_menu(user.id, group_chat_id or 0)
            )
            _schedule_delete(context, chat.id)
        except Exception as e:
            print("[PV SUDO BACK ERR] " + str(e))
        return

'''
        pv_content = pv_content.replace(anchor, back_handler + anchor, 1)
        print("   ✅ هندلر sudo_panel_back اضافه شد.")

# --- 2.4: به‌روزرسانی pattern pv_owner_callbacks ---
old_pat = 'pattern=r"^(op_back|op_manage|op_settings|op_ownerguide)"'
new_pat = 'pattern=r"^(op_back|op_manage|op_settings|op_ownerguide|owner_section_menu|sudo_panel_back)"'
if old_pat in pv_content:
    pv_content = pv_content.replace(old_pat, new_pat)
    print("   ✅ الگوی pv_owner_callbacks به‌روزرسانی شد.")
else:
    # ممکنه الگو فرق کنه
    m = re.search(r'pattern=r"\^(op_back[^"]*)"', pv_content)
    if m:
        old = m.group(0)
        new = 'pattern=r"^(op_back|op_manage|op_settings|op_ownerguide|owner_section_menu|sudo_panel_back)"'
        pv_content = pv_content.replace(old, new, 1)
        print(f"   ✅ الگو با regex: {old} → {new}")

with open('modules/pv_main.py', 'w', encoding='utf-8') as f:
    f.write(pv_content)

# ============================================================
# 3. بررسی start.py (که owner_section_menu و sudo_panel_back داشته باشه)
# ============================================================
print("\n=== 2. تأیید start.py ===")

with open('modules/start.py', 'r', encoding='utf-8') as f:
    st_content = f.read()

checks = {
    'owner_section_menu def': 'def owner_section_menu(' in st_content,
    'owner_section_menu handler': 'if action == "owner_section_menu"' in st_content,
    'sudo_panel_back handler': 'if action == "sudo_panel_back"' in st_content,
    'sudo_panel_menu def': 'def sudo_panel_menu(' in st_content,
}
for name, ok in checks.items():
    print(f"   {'✅' if ok else '❌'} {name}")

# اگر sudo_panel_back نیست، اضافه کن
if 'if action == "sudo_panel_back"' not in st_content:
    print("   ⚠️ اضافه کردن sudo_panel_back به start.py...")
    anchor = '    if action == "menu_close"'
    if anchor in st_content:
        new_h = '''    if action == "sudo_panel_back":
        try:
            await query.edit_message_text(
                "👑 منوی اصلی - بخش مورد نظر:",
                reply_markup=sudo_panel_menu(query.from_user.id, query.message.chat.id)
            )
        except Exception as e:
            print("[SUDO BACK ERR] " + str(e))
        return

'''
        st_content = st_content.replace(anchor, new_h + anchor, 1)
        print("   ✅ sudo_panel_back اضافه شد.")

# به‌روزرسانی pattern در start.py اگر لازم بود
m = re.search(r'pattern="([^"]*menu_status[^"]*)"', st_content)
if m and 'sudo_panel_back' not in m.group(1):
    old = m.group(1)
    new = old + '|sudo_panel_back'
    st_content = st_content.replace(f'pattern="{old}"', f'pattern="{new}"', 1)
    print("   ✅ pattern start.py به‌روزرسانی شد.")

with open('modules/start.py', 'w', encoding='utf-8') as f:
    f.write(st_content)

# ============================================================
# 4. کامپایل
# ============================================================
print("\n=== 3. کامپایل ===")
for f in ['modules/pv_main.py', 'modules/start.py']:
    try:
        py_compile.compile(f, doraise=True)
        print(f"   ✅ {f}")
    except Exception as e:
        print(f"   ❌ {f}: {e}")
        shutil.copy(bak_pv if 'pv' in f else bak_st, f)
        print(f"   ⚠️ Auto-Rollback انجام شد.")
        exit(1)

# ============================================================
# 5. پاک کردن __pycache__
# ============================================================
print("\n=== 4. پاک کردن __pycache__ ===")
for root, dirs, files in os.walk('.'):
    if 'venv' in root:
        continue
    if '__pycache__' in root:
        shutil.rmtree(root, ignore_errors=True)
        print(f"   🗑 {root}")

# ============================================================
# 6. ری‌استارت
# ============================================================
print("\n=== 5. ری‌استارت ربات ===")
os.system('pkill -9 -f "main.py"')
os.system('pkill -9 -f "connection_monitor.py"')
time.sleep(4)
os.system('cd ~/groupbot && nohup bash bot_watchdog.sh > ~/groupbot_watchdog.log 2>&1 &')
time.sleep(10)
os.system('tail -n 6 ~/groupbot_bot.log')

print("\n" + "="*80)
print("✅ تمام شد!")
print("="*80)
print("""
📌 بعد از اجرا:
   1. در گروه: پنل → 🔧 بخش سازنده → هر دکمه → 🔙 بازگشت
      باید برگرده به «بخش سازنده» ✅
   2. در PV ربات: پنل → 🔧 بخش سازنده → هر دکمه → 🔙 بازگشت
      باید برگرده به «بخش سازنده» ✅
""")
