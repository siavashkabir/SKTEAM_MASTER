import os, shutil, py_compile, time, re

print("="*80)
print("🔧 هماهنگ‌سازی owner_manage_menu با sudo_panel_menu")
print("="*80)

ts = time.strftime("%H%M%S")
bak = f'modules/start.py.bak_syncmenu_{ts}'
shutil.copy('modules/start.py', bak)
print(f"✅ بکاپ: {bak}")

with open('modules/start.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# ==== 1. پیدا کردن owner_manage_menu ====
start_idx = None
for i, line in enumerate(lines):
    if line.startswith('def owner_manage_menu('):
        start_idx = i
        break

if start_idx is None:
    print("❌ owner_manage_menu پیدا نشد!")
    exit(1)

end_idx = len(lines)
for j in range(start_idx + 1, len(lines)):
    if lines[j].startswith('def ') or lines[j].startswith('async def '):
        end_idx = j
        break

print(f"📍 owner_manage_menu: خطوط {start_idx+1} تا {end_idx}")
print("\n=== محتوای قبلی ===")
for i in range(start_idx, end_idx):
    print(f"   {i+1}: {lines[i].rstrip()}")

# ==== 2. بازنویسی به شکل تمیز (همون sudo_panel_menu) ====
new_func = '''def owner_manage_menu(uid, chat_id=0):
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

lines = lines[:start_idx] + new_func.split('\n') + lines[end_idx:]

print("\n✅ owner_manage_menu بازنویسی شد (بدون ۵ دکمه قدیمی).")

with open('modules/start.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

# ==== 3. تأیید ====
print("\n=== تأیید ===")
with open('modules/start.py', 'r', encoding='utf-8') as f:
    nl = f.readlines()

for i, line in enumerate(nl):
    if line.startswith('def owner_manage_menu('):
        for j in range(i, min(i+15, len(nl))):
            print(f"   {j+1}: {nl[j].rstrip()}")
        break

# ==== 4. کامپایل ====
print("\n=== کامپایل ===")
try:
    py_compile.compile('modules/start.py', doraise=True)
    print("✅ کامپایل موفق.")
except Exception as e:
    print(f"❌ خطای کامپایل: {e}")
    shutil.copy(bak, 'modules/start.py')
    exit(1)

# ==== 5. پاک کردن کش ====
print("\n=== پاک کردن __pycache__ ===")
for root, dirs, files in os.walk('.'):
    if 'venv' in root:
        continue
    if '__pycache__' in root:
        shutil.rmtree(root, ignore_errors=True)

# ==== 6. ری‌استارت ====
print("\n=== ری‌استارت ===")
os.system('pkill -9 -f "main.py"')
os.system('pkill -9 -f "connection_monitor.py"')
time.sleep(4)
os.system('cd ~/groupbot && nohup bash bot_watchdog.sh > ~/groupbot_watchdog.log 2>&1 &')
time.sleep(10)
os.system('tail -n 6 ~/groupbot_bot.log')

print("\n" + "="*80)
print("✅ تمام شد! حالا در PV ربات 'پنل' یا 'start' بزن.")
print("="*80)
