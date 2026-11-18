import os, shutil, py_compile, time, re

print("="*80)
print("🔧 اسکریپت جامع: بازسازی کامل owner_manage_menu")
print("="*80)

# ============ 1. نمایش وضعیت فعلی ============
print("\n=== 1. نمایش وضعیت فعلی ===")

with open('modules/start.py', 'r', encoding='utf-8') as f:
    content = f.read()
    lines = content.split('\n')

# پیدا کردن owner_manage_menu
start_idx = None
for i, line in enumerate(lines):
    if line.startswith('def owner_manage_menu('):
        start_idx = i
        break

if start_idx is None:
    print("❌ owner_manage_menu پیدا نشد!")
    exit(1)

# پیدا کردن انتها
end_idx = None
for j in range(start_idx + 1, len(lines)):
    if lines[j].startswith('def ') or lines[j].startswith('async def '):
        end_idx = j
        break

print(f"📍 owner_manage_menu: خطوط {start_idx+1} تا {end_idx}")
print("\nمحتوای فعلی:")
for i in range(start_idx, end_idx):
    print(f"   {i+1}: {lines[i]}")

# ============ 2. بازسازی owner_manage_menu ============
print("\n=== 2. بازسازی owner_manage_menu ===")

# منوی جدید تمیز
new_func = '''def owner_manage_menu(uid, chat_id=0):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💎 مدیریت اشتراک‌ها", callback_data="menu_status:" + str(uid))],
        [InlineKeyboardButton("🔧 بخش سازنده", callback_data="owner_section_menu:" + str(uid) + ":" + str(chat_id))],
        [InlineKeyboardButton("👥 ورود به پنل گروه", callback_data="g_back_panel:" + str(uid) + ":" + str(chat_id))],
        [InlineKeyboardButton("📖 راهنمای کامل", callback_data="menu_help:" + str(uid))],
        [InlineKeyboardButton("❌ بستن منو", callback_data="menu_close:" + str(uid))],
    ])
'''

# بکاپ
ts = time.strftime("%H%M%S")
bak = f'modules/start.py.bak_comp_{ts}'
shutil.copy('modules/start.py', bak)
print(f"✅ بکاپ: {bak}")

# جایگزینی
new_lines = lines[:start_idx] + new_func.split('\n') + lines[end_idx:]

with open('modules/start.py', 'w', encoding='utf-8') as f:
    f.write('\n'.join(new_lines))

print("✅ owner_manage_menu بازسازی شد.")

# ============ 3. تأیید ============
print("\n=== 3. نمایش تابع جدید ===")
with open('modules/start.py', 'r', encoding='utf-8') as f:
    nl = f.readlines()

for i, line in enumerate(nl):
    if line.startswith('def owner_manage_menu('):
        for j in range(i, min(i+15, len(nl))):
            print(f"   {j+1}: {nl[j].rstrip()}")
        break

# ============ 4. کامپایل ============
print("\n=== 4. کامپایل ===")
try:
    py_compile.compile('modules/start.py', doraise=True)
    print("✅ کامپایل موفق.")
except Exception as e:
    print(f"❌ خطای کامپایل: {e}")
    shutil.copy(bak, 'modules/start.py')
    print("⚠️ Auto-Rollback انجام شد.")
    exit(1)

# ============ 5. پاک کردن کش ============
print("\n=== 5. پاک کردن کش ===")
for root, dirs, files in os.walk('.'):
    if 'venv' in root:
        continue
    if '__pycache__' in root:
        shutil.rmtree(root, ignore_errors=True)
        print(f"   🗑 حذف: {root}")

# ============ 6. ری‌استارت ============
print("\n=== 6. ری‌استارت ربات ===")
os.system('pkill -9 -f "main.py"')
os.system('pkill -9 -f "connection_monitor.py"')
time.sleep(4)
os.system('cd ~/groupbot && nohup bash bot_watchdog.sh > ~/groupbot_watchdog.log 2>&1 &')
time.sleep(12)

os.system('tail -n 8 ~/groupbot_bot.log')

print("\n" + "="*80)
print("✅ تمام شد!")
print("="*80)
print("""
📌 منوی جدید owner_manage_menu:
   1. 💎 مدیریت اشتراک‌ها
   2. 🔧 بخش سازنده  ← زیرمنو با ۵ دکمه
   3. 👥 ورود به پنل گروه
   4. 📖 راهنمای کامل
   5. ❌ بستن منو
""")
