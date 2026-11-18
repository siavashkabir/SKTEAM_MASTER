import os, shutil, py_compile, time, glob, re, tempfile

print("="*80)
print("🔧 حذف امن «بستن» از زیرمنوها (تست قبل از ذخیره)")
print("="*80)

ts = time.strftime("%H%M%S")

# ============================================================
# 1. منوهای اصلی (باید «بستن» داشته باشن)
# ============================================================
MAIN_MENUS = {
    'sudo_panel_menu',
    'group_owner_panel_menu',
    'owner_manage_menu',
    'group_manage_menu',
    'group_panel_menu',
    'start_cmd',  # منوی PV
    'main_menu_kb',
}

# ============================================================
# 2. بکاپ
# ============================================================
all_files = []
for f in glob.glob('modules/*.py'):
    if '.bak' in f or 'crash' in f:
        continue
    all_files.append(f)

backups = {}
for f in all_files:
    bak = f'{f}.bak_safe_{ts}'
    shutil.copy(f, bak)
    backups[f] = bak

print(f"✅ {len(backups)} فایل بکاپ")

# ============================================================
# 3. پردازش با تست قبل از ذخیره
# ============================================================
files_changed = []
files_skipped = []
total_removed = 0

for f in all_files:
    with open(f, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    # پیدا کردن توابع
    funcs = []
    for i, line in enumerate(lines):
        m = re.match(r'^(async\s+)?def\s+(\w+)\s*\(', line)
        if m:
            funcs.append([m.group(2), i, len(lines)])
    
    for j in range(len(funcs) - 1):
        funcs[j][2] = funcs[j+1][1]
    
    # پیدا کردن خطوط حذفی
    to_remove = set()
    
    for fname, start, end in funcs:
        if fname in MAIN_MENUS:
            continue
        
        # پیدا کردن ردیف‌های کاملاً مستقل «بستن» (نه ترکیبی با بازگشت)
        for i in range(start, end):
            line = lines[i]
            stripped = line.strip()
            
            # شرط: خط باید کامل باشه، فقط با [InlineKeyboardButton شروع شه
            is_self_contained = (
                stripped.startswith('[InlineKeyboardButton') and
                (stripped.endswith('],') or stripped.endswith('])],') or stripped.endswith('])]'))
            )
            
            # شرط: فقط «بستن» داشته باشه (نه بازگشت)
            has_only_close = (
                'بستن' in line and
                'بازگشت' not in line
            )
            
            if is_self_contained and has_only_close:
                # چک: داخل تابع، حتماً یک «بازگشت» هم هست
                has_back = any('بازگشت' in lines[k] for k in range(start, end))
                if has_back:
                    to_remove.add(i)
    
    if not to_remove:
        continue
    
    # ساخت نسخه جدید
    new_lines = [l for i, l in enumerate(lines) if i not in to_remove]
    
    # ============================================================
    # تست کامپایل با فایل موقت
    # ============================================================
    temp_path = f + '.test_compile'
    try:
        with open(temp_path, 'w', encoding='utf-8') as file:
            file.writelines(new_lines)
        
        try:
            py_compile.compile(temp_path, doraise=True)
            # ✅ کامپایل موفق، ذخیره کن
            with open(f, 'w', encoding='utf-8') as file:
                file.writelines(new_lines)
            files_changed.append(f)
            total_removed += len(to_remove)
            print(f"   ✅ {f}: {len(to_remove)} حذف")
        except py_compile.PyCompileError:
            # ❌ کامپایل شکست، فایل اصلی رو دست نزن
            print(f"   ⚠️ {f}: کامپایل شکست → رد شد")
            files_skipped.append(f)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    except Exception as e:
        print(f"   ❌ {f}: {e}")
        if os.path.exists(temp_path):
            os.remove(temp_path)

print(f"\n📊 خلاصه:")
print(f"   • تغییر یافته: {len(files_changed)}")
print(f"   • رد شده: {len(files_skipped)}")
print(f"   • حذف: {total_removed}")

# ============================================================
# 4. کامپایل نهایی همه فایل‌ها
# ============================================================
print("\n=== کامپایل نهایی ===")
failed = []
for f in glob.glob('modules/*.py'):
    if '.bak' in f or '.test_compile' in f:
        continue
    try:
        py_compile.compile(f, doraise=True)
    except Exception as e:
        failed.append(f)
        print(f"   ❌ {f}: {e}")

if not failed:
    print("   ✅ همه فایل‌ها سالمن")
else:
    print(f"   ⚠️ {len(failed)} فایل خطا داره!")

# ============================================================
# 5. کش + ری‌استارت
# ============================================================
for root, dirs, files in os.walk('.'):
    if 'venv' in root:
        continue
    if '__pycache__' in root:
        shutil.rmtree(root, ignore_errors=True)

print("\n=== ری‌استارت ===")
os.system('pkill -9 -f "main.py"')
os.system('pkill -9 -f "connection_monitor.py"')
time.sleep(4)
os.system('cd ~/groupbot && nohup bash bot_watchdog.sh > ~/groupbot_watchdog.log 2>&1 &')
time.sleep(10)
os.system('tail -n 5 ~/groupbot_bot.log')

print("\n" + "="*80)
print("✅ تمام!")
print("="*80)
