import os, glob, shutil, py_compile, time, re, difflib

print("=== 1. ایجاد بکاپ امنیتی از وضعیت فعلی ===")
try:
    timestamp = time.strftime("%H%M%S")
    shutil.copy('modules/start.py', f'modules/start.py.bak_{timestamp}')
    shutil.copy('modules/owner_panel_trigger.py', f'modules/owner_panel_trigger.py.bak_{timestamp}')
    print(f"✅ بکاپ امنیتی با تاریخ {timestamp} ایجاد شد.")
except Exception as e:
    print(f"❌ خطا در بکاپ: {e}")
    exit(1)

print("\n=== 2. پیدا کردن آخرین بکاپ‌های قدیمی (که قابلیت‌ها را دارند) ===")
# پیدا کردن آخرین بکاپ start.py و owner_panel_trigger.py (به جز بکاپ‌های امروز)
old_start_baks = [f for f in glob.glob('modules/start.py.bak_*') if 'crash' not in f and '.broken' not in f]
old_trigger_baks = [f for f in glob.glob('modules/owner_panel_trigger.py.bak_*') if 'crash' not in f and '.broken' not in f]

# مرتب‌سازی بر اساس زمان
old_start_baks.sort(key=os.path.getctime, reverse=True)
old_trigger_baks.sort(key=os.path.getctime, reverse=True)

# انتخاب بکاپ هدف (دومین بکاپ جدید، چون جدیدترین ممکن است همان بکاپ 10:35 باشد که خراب است)
target_start_backup = old_start_baks[1] if len(old_start_baks) > 1 else old_start_baks[0]
target_trigger_backup = old_trigger_baks[1] if len(old_trigger_baks) > 1 else old_trigger_baks[0]

print(f"🎯 بکاپ هدف برای start.py: {target_start_backup}")
print(f"🎯 بکاپ هدف برای owner_panel_trigger.py: {target_trigger_backup}")

print("\n=== 3. استخراج بخش‌های گمشده از بکاپ‌های قدیمی ===")

# 3.1. استخراج توابع گمشده از start.py
with open('modules/start.py', 'r', encoding='utf-8') as f:
    current_start = f.read()
with open(target_start_backup, 'r', encoding='utf-8') as f:
    old_start = f.read()

# پیدا کردن تمام توابعی که در بکاپ قدیمی هستند اما در فایل فعلی وجود ندارند
old_functions = re.findall(r'(async def [a-zA-Z_]+\(.*?\):.*?)(?=\nasync def |\ndef |\Z)', old_start, re.DOTALL)
missing_functions = []
for func in old_functions:
    func_name = re.search(r'async def ([a-zA-Z_]+)', func)
    if func_name and f'async def {func_name.group(1)}' not in current_start:
        # فقط توابعی که مربوط به تنظیمات و پنل مالکیت هستند را بردار
        if any(keyword in func.lower() for keyword in ['owner', 'panel', 'setting', 'delete', 'timer']):
            missing_functions.append(func)

if missing_functions:
    print(f"🔍 {len(missing_functions)} تابع گمشده مربوط به تنظیمات مالکیت پیدا شد.")
    # اضافه کردن توابع گمشده به انتهای فایل فعلی
    with open('modules/start.py', 'a', encoding='utf-8') as f:
        f.write("\n\n# ==== [MERGED FROM OLD BACKUP] ====\n")
        for func in missing_functions:
            f.write(func + "\n\n")
    print("✅ توابع گمشده به start.py اضافه شدند.")
else:
    print("⚠️ تابع گمشده‌ای در start.py پیدا نشد (شاید در owner_panel_trigger.py باشد).")

# 3.2. استخراج توابع گمشده از owner_panel_trigger.py
with open('modules/owner_panel_trigger.py', 'r', encoding='utf-8') as f:
    current_trigger = f.read()
with open(target_trigger_backup, 'r', encoding='utf-8') as f:
    old_trigger = f.read()

old_trigger_funcs = re.findall(r'(async def [a-zA-Z_]+\(.*?\):.*?)(?=\nasync def |\ndef |\Z)', old_trigger, re.DOTALL)
missing_trigger_funcs = []
for func in old_trigger_funcs:
    func_name = re.search(r'async def ([a-zA-Z_]+)', func)
    if func_name and f'async def {func_name.group(1)}' not in current_trigger:
        if any(keyword in func.lower() for keyword in ['owner', 'panel', 'setting', 'delete', 'timer']):
            missing_trigger_funcs.append(func)

if missing_trigger_funcs:
    print(f"🔍 {len(missing_trigger_funcs)} تابع گمشده در owner_panel_trigger.py پیدا شد.")
    with open('modules/owner_panel_trigger.py', 'a', encoding='utf-8') as f:
        f.write("\n\n# ==== [MERGED FROM OLD BACKUP] ====\n")
        for func in missing_trigger_funcs:
            f.write(func + "\n\n")
    print("✅ توابع گمشده به owner_panel_trigger.py اضافه شدند.")

print("\n=== 4. کامپایل فایل‌ها ===")
try:
    py_compile.compile('modules/start.py', doraise=True)
    py_compile.compile('modules/owner_panel_trigger.py', doraise=True)
    print("✅ کامپایل با موفقیت انجام شد.")
except Exception as e:
    print(f"❌ خطای کامپایل: {e}")
    print("⚠️ در حال بازگردانی بکاپ (Auto-Rollback)...")
    shutil.copy(f'modules/start.py.bak_{timestamp}', 'modules/start.py')
    shutil.copy(f'modules/owner_panel_trigger.py.bak_{timestamp}', 'modules/owner_panel_trigger.py')
    print("✅ بکاپ با موفقیت ریستور شد. هیچ تغییری اعمال نشد.")
    exit(1)

print("\n=== 5. ری‌استارت ربات ===")
os.system('pkill -9 -f "main.py"')
time.sleep(2)
os.system('cd ~/groupbot && bash -c "source venv/bin/activate && nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 &"')
time.sleep(4)
print("✅ ربات با موفقیت ری‌استارت شد.")
os.system('tail -n 15 ~/groupbot_bot.log')
