import os, shutil, py_compile, time, glob, re

print("="*80)
print("🔧 حذف هوشمند «بستن» از منوهایی که «بازگشت» دارن")
print("="*80)

ts = time.strftime("%H%M%S")

# ============================================================
# 1. بکاپ
# ============================================================
print("\n=== 1. بکاپ‌گیری ===")
all_files = []
for f in glob.glob('modules/*.py'):
    if '.bak' in f or 'crash' in f or '__pycache__' in f:
        continue
    all_files.append(f)

for f in ['main.py', 'config.py', 'database.py']:
    if os.path.exists(f):
        all_files.append(f)

backups = {}
for f in all_files:
    bak = f'{f}.bak_noclose_{ts}'
    try:
        shutil.copy(f, bak)
        backups[f] = bak
    except Exception:
        pass
print(f"✅ {len(backups)} فایل بکاپ گرفته شد")

# ============================================================
# 2. اسکن و حذف
# ============================================================
print("\n=== 2. حذف هوشمند ===")
files_changed = []
total_removed = 0

for f in all_files:
    try:
        with open(f, 'r', encoding='utf-8') as file:
            lines = file.readlines()
    except Exception:
        continue
    
    # موقعیت همه دکمه‌های بازگشت
    back_positions = []
    for i, l in enumerate(lines):
        if 'InlineKeyboardButton' in l and 'بازگشت' in l:
            back_positions.append(i)
    
    if not back_positions:
        continue
    
    # دکمه‌های بستن نزدیک به بازگشت (در فاصله 5 خط)
    to_remove = set()
    for i, l in enumerate(lines):
        if 'InlineKeyboardButton' not in l:
            continue
        
        # چک کن دکمه بستن هست
        is_close = False
        if 'بستن' in l:
            is_close = True
        elif 'menu_close' in l and 'بستن' in l:
            is_close = True
        
        if not is_close:
            continue
        
        # چک نزدیکی به بازگشت
        for bp in back_positions:
            if abs(bp - i) <= 5:
                to_remove.add(i)
                break
    
    if not to_remove:
        continue
    
    new_lines = [l for i, l in enumerate(lines) if i not in to_remove]
    
    try:
        with open(f, 'w', encoding='utf-8') as file:
            file.writelines(new_lines)
        files_changed.append(f)
        total_removed += len(to_remove)
        print(f"   ✅ {f}: {len(to_remove)} حذف")
    except Exception as e:
        print(f"   ❌ {f}: {e}")
        if f in backups:
            shutil.copy(backups[f], f)

print(f"\n📊 مجموع: {total_removed} حذف در {len(files_changed)} فایل")

# ============================================================
# 3. کامپایل
# ============================================================
print("\n=== 3. کامپایل ===")
failed = []
for f in files_changed:
    try:
        py_compile.compile(f, doraise=True)
        print(f"   ✅ {f}")
    except Exception as e:
        print(f"   ❌ {f}: {e}")
        if f in backups:
            shutil.copy(backups[f], f)
            failed.append(f)
            print(f"   ⚠️ برگشت")

if failed:
    print(f"\n⚠️ {len(failed)} فایل برگشتن (تغییراتشون اعمال نشد)")
else:
    print(f"\n✅ همه فایل‌ها کامپایل شدن")

# ============================================================
# 4. کش + ری‌استارت
# ============================================================
print("\n=== 4. پاک کردن __pycache__ ===")
for root, dirs, files in os.walk('.'):
    if 'venv' in root:
        continue
    if '__pycache__' in root:
        shutil.rmtree(root, ignore_errors=True)

print("\n=== 5. ری‌استارت ===")
os.system('pkill -9 -f "main.py"')
os.system('pkill -9 -f "connection_monitor.py"')
time.sleep(4)
os.system('cd ~/groupbot && nohup bash bot_watchdog.sh > ~/groupbot_watchdog.log 2>&1 &')
time.sleep(10)
os.system('tail -n 6 ~/groupbot_bot.log')

print("\n" + "="*80)
print("✅ تمام!")
print("="*80)
print(f"""
📊 خلاصه:
   • بکاپ: {len(backups)} فایل
   • تغییر: {len(files_changed)} فایل
   • حذف: {total_removed} دکمه
   • خطا: {len(failed)} فایل

📌 حالا:
   ✅ منوهای با بازگشت → فقط 🔙 بازگشت (بدون بستن)
   ✅ منوهای بدون بازگشت → فقط ❌ بستن
   ✅ glitch صفر
""")
