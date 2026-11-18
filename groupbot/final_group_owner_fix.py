import os, shutil, py_compile, time, re

print("="*80)
print("🔧 اصلاح نهایی پنل مالک گروه - همه بازگشت‌ها")
print("="*80)

ts = time.strftime("%H%M%S")
bak = f'modules/start.py.bak_gof_{ts}'
shutil.copy('modules/start.py', bak)
print(f"✅ بکاپ: {bak}")

with open('modules/start.py', 'r', encoding='utf-8') as f:
    content = f.read()

# ============================================================
# 1. menu_back → group_manage_menu
# ============================================================
print("\n=== 1. menu_back ===")
pattern = re.compile(
    r'(    if action == "menu_back":\s*\n)(.*?)(?=\n    if action |\n    # =====|\Z)',
    re.DOTALL
)
m = pattern.search(content)
if m:
    new_body = '''        # [FIX] بازگشت به منوی مدیریت گروه
        try:
            await query.edit_message_text(
                "👥 مدیریت گروه\\n\\nبرای مدیریت گروه، از دکمه‌های زیر استفاده کنید:",
                reply_markup=group_manage_menu(uid)
            )
            reset_timer(context, chat_id, msg_id)
        except Exception as e:
            print("[MENU_BACK ERR] " + str(e))
        return
'''
    content = content[:m.start(2)] + new_body + content[m.end(2):]
    print("   ✅ menu_back → group_manage_menu")

# ============================================================
# 2. g_back_panel → group_owner_panel_menu (یا sudo_panel_menu)
# ============================================================
print("\n=== 2. g_back_panel ===")
pattern = re.compile(
    r'(    if action == "g_back_panel":\s*\n)(.*?)(?=\n    if action |\n    # =====|\Z)',
    re.DOTALL
)
m = pattern.search(content)
if m:
    new_body = '''        # [FIX] بازگشت از تنظیمات گروه
        try:
            from config import OWNER_ID
            from database import is_bot_admin
            _is_owner = (query.from_user.id == OWNER_ID)
            _is_sudo = False
            if not _is_owner:
                try:
                    _is_sudo = is_bot_admin(query.from_user.id)
                except Exception:
                    pass
            if _is_owner or _is_sudo:
                # سازنده/سودو → منوی اصلی سازنده
                await query.edit_message_text(
                    "👑 منوی اصلی - بخش مورد نظر:",
                    reply_markup=sudo_panel_menu(query.from_user.id, chat_id)
                )
            else:
                # مالک گروه → منوی مدیریت گروه
                await query.edit_message_text(
                    "👥 مدیریت گروه\\n\\nبرای مدیریت گروه، از دکمه‌های زیر استفاده کنید:",
                    reply_markup=group_manage_menu(query.from_user.id)
                )
            reset_timer(context, chat_id, msg_id)
        except Exception as e:
            print("[G_BACK_PANEL ERR] " + str(e))
        return
'''
    content = content[:m.start(2)] + new_body + content[m.end(2):]
    print("   ✅ g_back_panel → group_manage_menu / sudo_panel_menu")

# ============================================================
# 3. بررسی و اصلاح g_op_manage و g_op_settings
# ============================================================
print("\n=== 3. g_op_manage و g_op_settings ===")
# g_op_manage
pattern = re.compile(
    r'(    if action == "g_op_manage":\s*\n)(.*?)(?=\n    if action |\n    # =====|\Z)',
    re.DOTALL
)
m = pattern.search(content)
if m:
    new_body = '''        # [FIX] g_op_manage → group_manage_menu
        try:
            await query.edit_message_text(
                "👥 مدیریت گروه\\n\\nبرای مدیریت گروه، از دکمه‌های زیر استفاده کنید:",
                reply_markup=group_manage_menu(query.from_user.id)
            )
        except Exception as e:
            print("[G_OP_MANAGE ERR] " + str(e))
        return
'''
    content = content[:m.start(2)] + new_body + content[m.end(2):]
    print("   ✅ g_op_manage → group_manage_menu")

# g_op_settings
pattern = re.compile(
    r'(    if action == "g_op_settings":\s*\n)(.*?)(?=\n    if action |\n    # =====|\Z)',
    re.DOTALL
)
m = pattern.search(content)
if m:
    new_body = '''        # [FIX] g_op_settings → owner_settings_menu
        try:
            await query.edit_message_text(
                "⚙️ تنظیمات این گروه:",
                reply_markup=owner_settings_menu(query.from_user.id, chat_id)
            )
        except Exception as e:
            print("[G_OP_SETTINGS ERR] " + str(e))
        return
'''
    content = content[:m.start(2)] + new_body + content[m.end(2):]
    print("   ✅ g_op_settings → owner_settings_menu")

# ============================================================
# 4. چک handlerهای داخلی (menu_locks, menu_media و ...)
# ============================================================
print("\n=== 4. چک handlerهای داخلی ===")
internal_handlers = ['menu_locks', 'menu_media', 'menu_modes', 'welcome_menu',
                      'nsfw_menu', 'warnset_menu', 'purge_menu', 'link_menu',
                      'nphoto_panel', 'vague_panel', 'raid_panel', 'abot_panel',
                      'invite_unban_toggle', 'games_toggle']

for target in internal_handlers:
    if f'action == "{target}"' in content:
        # چک می‌کنیم که back button داخلش کار می‌کنه
        pattern = re.compile(
            rf'(    if action == "{target}":\s*\n)(.*?)(?=\n    if action |\n    # =====|\Z)',
            re.DOTALL
        )
        m = pattern.search(content)
        if m:
            body = m.group(2)
            # چک کن که return داره
            if not body.rstrip().endswith('return'):
                # اضافه کن
                indent = ' ' * 8
                new_body = m.group(2) + f'{indent}return\n'
                content = content[:m.start(2)] + new_body + content[m.end(2):]
                print(f"   ✅ {target}: return اضافه شد")
            else:
                print(f"   ℹ️ {target}: OK")
    else:
        print(f"   ⚠️ {target}: handler در start.py نیست (در ماژول جداگانه)")

with open('modules/start.py', 'w', encoding='utf-8') as f:
    f.write(content)

# ============================================================
# 5. کامپایل
# ============================================================
print("\n=== 5. کامپایل ===")
try:
    py_compile.compile('modules/start.py', doraise=True)
    print("   ✅ کامپایل موفق")
except Exception as e:
    print(f"   ❌ خطا: {e}")
    shutil.copy(bak, 'modules/start.py')
    print("   ⚠️ Auto-Rollback")
    exit(1)

# ============================================================
# 6. کش + ری‌استارت
# ============================================================
for root, dirs, files in os.walk('.'):
    if 'venv' in root:
        continue
    if '__pycache__' in root:
        shutil.rmtree(root, ignore_errors=True)

print("\n=== 6. ری‌استارت ===")
os.system('pkill -9 -f "main.py"')
os.system('pkill -9 -f "connection_monitor.py"')
time.sleep(4)
os.system('cd ~/groupbot && nohup bash bot_watchdog.sh > ~/groupbot_watchdog.log 2>&1 &')
time.sleep(10)
os.system('tail -n 6 ~/groupbot_bot.log')

print("\n" + "="*80)
print("✅ تمام! حالا این تست‌ها رو انجام بده:")
print("="*80)
print("""
1️⃣ تست ۱ (مدیریت گروه):
   پنل → 👥 مدیریت گروه → روی وضعیت گروه بزن → 🔙 بازگشت
   انتظار: برگرده به مدیریت گروه (نه منوی اصلی)

2️⃣ تست ۲ (تنظیمات گروه):
   پنل → ⚙️ تنظیمات گروه → روی قفل‌های اصلی بزن → 🔙 بازگشت
   انتظار: برگرده به تنظیمات گروه (نه منوی اصلی)

3️⃣ تست ۳ (بازگشت از تنظیمات گروه):
   پنل → ⚙️ تنظیمات گروه → 🔙 بازگشت
   انتظار: برگرده به منوی اصلی مالک گروه
""")
