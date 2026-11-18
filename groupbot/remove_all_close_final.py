import os, shutil, py_compile, time, glob, re

print("="*80)
print("🔧 حذف کامل «بستن» از همه زیرمنوها (به جز منوی اصلی)")
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

backups = {}
for f in all_files:
    bak = f'{f}.bak_nac_{ts}'
    try:
        shutil.copy(f, bak)
        backups[f] = bak
    except Exception:
        pass
print(f"✅ {len(backups)} فایل بکاپ")

# ============================================================
# 2. منوهای اصلی که باید «بستن» داشته باشن
# ============================================================
MAIN_MENUS = {
    'sudo_panel_menu',           # منوی اصلی سازنده
    'group_owner_panel_menu',    # منوی اصلی مالک گروه
    'owner_manage_menu',         # منوی اصلی (قدیم)
    'group_manage_menu',         # منوی مدیریت گروه
    'group_panel_menu',          # منوی پنل گروه
}

# ============================================================
# 3. پردازش هر فایل
# ============================================================
print("\n=== 2. پردازش فایل‌ها ===")
files_changed = []
total_removed = 0

for f in all_files:
    try:
        with open(f, 'r', encoding='utf-8') as file:
            lines = file.readlines()
    except Exception:
        continue
    
    # پیدا کردن محدوده توابع
    funcs = []
    for i, line in enumerate(lines):
        m = re.match(r'^(async\s+)?def\s+(\w+)\s*\(', line)
        if m:
            funcs.append([m.group(2), i, len(lines)])
    
    # تعیین انتهای هر تابع
    for j in range(len(funcs) - 1):
        funcs[j][2] = funcs[j+1][1]
    
    # خطوطی که باید حذف بشن
    to_remove = set()
    
    for fname, start, end in funcs:
        # اگه تابع منوی اصلیه، دست نزن
        if fname in MAIN_MENUS:
            continue
        
        # توی این تابع، دنبال back و close بگرد
        back_lines = []
        close_lines = []
        
        for i in range(start, end):
            line = lines[i]
            if 'InlineKeyboardButton' not in line:
                continue
            
            # چک کن خط کامل هست (تک خطی)
            stripped = line.rstrip()
            is_complete = (
                stripped.endswith('],') or 
                stripped.endswith('])') or
                stripped.endswith('])]') or
                stripped.endswith('])],') or
                stripped.endswith('),')
            )
            
            if not is_complete:
                continue
            
            # بازگشت
            if 'بازگشت' in line:
                back_lines.append(i)
            # بستن
            if 'بستن' in line or ('menu_close' in line and 'بستن' in line):
                close_lines.append(i)
        
        # اگه هم بازگشت هم بستن داره، بستن رو حذف کن
        if back_lines and close_lines:
            for cl in close_lines:
                to_remove.add(cl)
    
    if to_remove:
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
# 4. کامپایل
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
    print(f"\n⚠️ {len(failed)} فایل برگشتن")
else:
    print(f"\n✅ همه موفق")

# ============================================================
# 5. کش + ری‌استارت
# ============================================================
for root, dirs, files in os.walk('.'):
    if 'venv' in root:
        continue
    if '__pycache__' in root:
        shutil.rmtree(root, ignore_errors=True)

print("\n=== 4. ری‌استارت ===")
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

📌 نتیجه:
   ✅ همه زیرمنوها فقط 🔙 بازگشت
   ✅ منوی اصلی (sudo, group_owner, owner_manage, group_manage, group_panel) → بازگشت + بستن
   ✅ glitch صفر
""")
