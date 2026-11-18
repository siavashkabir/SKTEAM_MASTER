import os, shutil, py_compile, time, re

print("="*80)
print("🔧 اصلاح نهایی: ویرایش sudo_panel_menu (منوی واقعی سازنده)")
print("="*80)

# ==== 1. بکاپ ====
ts = time.strftime("%H%M%S")
bak = f'modules/start.py.bak_correct_{ts}'
shutil.copy('modules/start.py', bak)
print(f"✅ بکاپ: {bak}")

with open('modules/start.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# ==== 2. پیدا کردن sudo_panel_menu ====
sudo_start = None
for i, line in enumerate(lines):
    if line.startswith('def sudo_panel_menu('):
        sudo_start = i
        break

if sudo_start is None:
    print("❌ sudo_panel_menu پیدا نشد!")
    exit(1)

sudo_end = len(lines)
for j in range(sudo_start + 1, len(lines)):
    if lines[j].startswith('def ') or lines[j].startswith('async def '):
        sudo_end = j
        break

print(f"📍 sudo_panel_menu: خطوط {sudo_start+1} تا {sudo_end}")

# ==== 3. بازسازی sudo_panel_menu (بدون ۵ دکمه + با دکمه بخش سازنده) ====
new_sudo = '''def sudo_panel_menu(uid, chat_id=0):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💎 مدیریت اشتراک‌ها", callback_data="sub_manage:" + str(uid) + ":" + str(chat_id))],
        [InlineKeyboardButton("🔧 بخش سازنده", callback_data="owner_section_menu:" + str(uid) + ":" + str(chat_id))],
        [InlineKeyboardButton("🔗 ورود به پنل گروه", callback_data="s_panel_group:" + str(uid) + ":" + str(chat_id))],
        [InlineKeyboardButton("📖 راهنمای کامل", callback_data="owner_readme:" + str(uid) + ":" + str(chat_id))],
        [InlineKeyboardButton("⚙️ تنظیمات این گروه", callback_data="owner_set_group:" + str(uid) + ":" + str(chat_id))],
        [InlineKeyboardButton("🖥 مدیریت سیستم", callback_data="sys_menu:" + str(uid) + ":" + str(chat_id))],
        [InlineKeyboardButton("❌ بستن منو", callback_data="menu_close:" + str(uid))],
    ])
'''

lines = lines[:sudo_start] + new_sudo.split('\n') + lines[sudo_end:]
print("✅ sudo_panel_menu بازسازی شد (۵ دکمه حذف + دکمه بخش سازنده).")

# ==== 4. پیدا کردن owner_section_menu و بازسازی ====
# دوباره خوندن
content = '\n'.join(lines)
sec_start = None
for i, line in enumerate(lines):
    if line.startswith('def owner_section_menu('):
        sec_start = i
        break

new_section = '''def owner_section_menu(uid, chat_id=0):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👤 مدیریت ادمین‌های ربات", callback_data="op_botadmins:" + str(uid) + ":" + str(chat_id))],
        [InlineKeyboardButton("🌐 مدیریت گروه‌ها", callback_data="rmt_groups:" + str(uid) + ":" + str(chat_id))],
        [InlineKeyboardButton("🔒 جوین اجباری", callback_data="s_fj_menu:" + str(uid) + ":" + str(chat_id))],
        [InlineKeyboardButton("📊 آمار سودوها", callback_data="s_op_sudo_stats:" + str(uid) + ":" + str(chat_id))],
        [InlineKeyboardButton("📈 آمار گروه‌ها", callback_data="s_op_group_stats:" + str(uid) + ":" + str(chat_id))],
        [InlineKeyboardButton("🔙 بازگشت", callback_data="sudo_panel_back:" + str(uid) + ":" + str(chat_id))],
    ])
'''

if sec_start is not None:
    # پیدا کردن انتها
    sec_end = len(lines)
    for j in range(sec_start + 1, len(lines)):
        if lines[j].startswith('def ') or lines[j].startswith('async def '):
            sec_end = j
            break
    lines = lines[:sec_start] + new_section.split('\n') + lines[sec_end:]
    print("✅ owner_section_menu بازنویسی شد.")
else:
    # اضافه کردن قبل از owner_manage_menu
    for i, line in enumerate(lines):
        if line.startswith('def owner_manage_menu('):
            lines = lines[:i] + new_section.split('\n') + ['\n', '\n'] + lines[i:]
            print("✅ owner_section_menu اضافه شد.")
            break

# ==== 5. پیدا کردن هندلرها و اصلاح ====
content = '\n'.join(lines)

# حذف هندلرهای قدیمی owner_section_menu
content = re.sub(
    r'(    if action == "owner_section_menu":.*?return\n)',
    '',
    content,
    count=1,
    flags=re.DOTALL
)

# اضافه کردن هندلرهای جدید قبل از "if action == \"menu_close\""
if 'if action == "sudo_panel_back"' not in content:
    anchor = '    if action == "menu_close"'
    if anchor in content:
        new_handlers = '''    if action == "owner_section_menu":
        try:
            from modules.start import sudo_panel_menu as _spm
            await query.edit_message_text(
                "🔧 بخش سازنده\\n\\nگزینه مورد نظر را انتخاب کنید:",
                reply_markup=owner_section_menu(query.from_user.id, query.message.chat.id)
            )
        except Exception as e:
            print("[SECTION MENU ERR] " + str(e))
        return

    if action == "sudo_panel_back":
        try:
            await query.edit_message_text(
                "👑 منوی اصلی - بخش مورد نظر:",
                reply_markup=sudo_panel_menu(query.from_user.id, query.message.chat.id)
            )
        except Exception as e:
            print("[SUDO BACK ERR] " + str(e))
        return

'''
        content = content.replace(anchor, new_handlers + anchor, 1)
        print("✅ هندلرهای جدید اضافه شدند.")

# ==== 6. اضافه کردن به pattern ====
pattern_match = re.search(r'pattern="([^"]*menu_status[^"]*)"', content)
if pattern_match and 'owner_section_menu' not in pattern_match.group(1):
    old_pat = pattern_match.group(1)
    new_pat = old_pat + '|owner_section_menu|sudo_panel_back'
    content = content.replace(f'pattern="{old_pat}"', f'pattern="{new_pat}"', 1)
    print("✅ به pattern اضافه شد.")

# ==== 7. نوشتن ====
with open('modules/start.py', 'w', encoding='utf-8') as f:
    f.write(content)

# ==== 8. کامپایل ====
print("\n=== کامپایل ===")
try:
    py_compile.compile('modules/start.py', doraise=True)
    print("✅ کامپایل موفق.")
except Exception as e:
    print(f"❌ خطای کامپایل: {e}")
    shutil.copy(bak, 'modules/start.py')
    print("⚠️ Auto-Rollback انجام شد.")
    exit(1)

# ==== 9. پاک کردن کش ====
print("\n=== پاک کردن __pycache__ ===")
for root, dirs, files in os.walk('.'):
    if 'venv' in root:
        continue
    if '__pycache__' in root:
        shutil.rmtree(root, ignore_errors=True)
        print(f"   🗑 {root}")

# ==== 10. ری‌استارت ====
print("\n=== ری‌استارت ===")
os.system('pkill -9 -f "main.py"')
os.system('pkill -9 -f "connection_monitor.py"')
time.sleep(4)
os.system('cd ~/groupbot && nohup bash bot_watchdog.sh > ~/groupbot_watchdog.log 2>&1 &')
time.sleep(12)

os.system('tail -n 6 ~/groupbot_bot.log')

print("\n" + "="*80)
print("✅ تمام شد!")
print("="*80)
