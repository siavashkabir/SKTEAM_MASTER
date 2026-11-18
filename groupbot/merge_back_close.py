import os, shutil, py_compile, time, glob

print("="*80)
print("🔧 ادغام بازگشت + بستن در یک ردیف (در همه منوها)")
print("="*80)

ts = time.strftime("%H%M%S")

# ============================================================
# 1. بکاپ از همه فایل‌های .py در modules
# ============================================================
print("\n=== 1. بکاپ‌گیری ===")
all_files = []
for f in glob.glob('modules/*.py'):
    if '.bak' in f or 'crash' in f or '__pycache__' in f:
        continue
    all_files.append(f)

# فایل‌های اصلی
for f in ['main.py', 'config.py', 'database.py']:
    if os.path.exists(f):
        all_files.append(f)

backups = {}
for f in all_files:
    bak = f'{f}.bak_merge_{ts}'
    try:
        shutil.copy(f, bak)
        backups[f] = bak
    except Exception:
        pass

print(f"✅ {len(backups)} فایل بکاپ گرفته شد")

# ============================================================
# 2. اسکن و ادغام
# ============================================================
print("\n=== 2. ادغام بازگشت + بستن ===")
files_changed = []
total_merges = 0

for f in all_files:
    try:
        with open(f, 'r', encoding='utf-8') as file:
            lines = file.readlines()
    except Exception:
        continue
    
    changes = 0
    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # چک: خط فعلی، دکمه بازگشت در یک ردیف جدا
        is_back_row = (
            'بازگشت' in line and
            'InlineKeyboardButton' in line and
            line.rstrip().endswith('],') and
            line.lstrip().startswith('[InlineKeyboardButton')
        )
        
        if is_back_row and i + 1 < len(lines):
            next_line = lines[i + 1]
            
            # چک: خط بعدی، دکمه بستن در یک ردیف جدا
            is_close_row = (
                'بستن' in next_line and
                'InlineKeyboardButton' in next_line and
                next_line.rstrip().endswith('],') and
                next_line.lstrip().startswith('[InlineKeyboardButton')
            )
            
            if is_close_row:
                # ادغام
                indent = ' ' * (len(line) - len(line.lstrip()))
                back_content = line.strip()[:-2].rstrip()   # حذف '],'
                close_content = next_line.strip()[1:-2].rstrip()  # حذف '[' و '],'
                
                merged_line = f"{indent}{back_content},\n{indent} {close_content}],\n"
                new_lines.append(merged_line)
                changes += 1
                i += 2
                continue
        
        new_lines.append(line)
        i += 1
    
    if changes > 0:
        try:
            with open(f, 'w', encoding='utf-8') as file:
                file.writelines(new_lines)
            files_changed.append(f)
            total_merges += changes
            print(f"   ✅ {f}: {changes} مورد")
        except Exception as e:
            print(f"   ❌ {f}: {e}")
            if f in backups:
                shutil.copy(backups[f], f)

print(f"\n📊 مجموع ادغام‌ها: {total_merges} در {len(files_changed)} فایل")

# ============================================================
# 3. کامپایل همه فایل‌های تغییر یافته
# ============================================================
print("\n=== 3. کامپایل ===")
failed = []
for f in files_changed:
    try:
        py_compile.compile(f, doraise=True)
        print(f"   ✅ {f}")
    except Exception as e:
        print(f"   ❌ {f}: {e}")
        # فقط این فایل رو برگردون
        if f in backups:
            shutil.copy(backups[f], f)
            failed.append(f)
            print(f"   ⚠️ از بکاپ برگشت")

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
   • فایل‌های تغییر یافته: {len(files_changed)}
   • ادغام‌ها: {total_merges}
   • فایل‌های برگردانده: {len(failed)}

📌 تست:
   1. پنل → تنظیمات گروه → Anti-Raid → 🔙 بازگشت
      → باید به تنظیمات برگرده، حالا Back و Close کنار هم هستن
   2. مدیریت گروه → 🔙 بازگشت → Back و Close کنار هم
   3. همه منوها → Back و Close کنار هم
""")
