import os, shutil, py_compile, time, re

print("="*80)
print("🚨 حذف «بخش سازنده» از منوی مالک گروه")
print("="*80)

ts = time.strftime("%H%M%S")
bak = f'modules/start.py.bak_rmsec_{ts}'
shutil.copy('modules/start.py', bak)
print(f"✅ بکاپ: {bak}")

with open('modules/start.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# ============================================================
# 1. جستجوی دکمه «بخش سازنده» در همه توابع مالک گروه
# ============================================================
print("\n=== جستجوی owner_section_menu در تمام فایل ===")

to_remove = []
for i, line in enumerate(lines):
    if 'owner_section_menu:' in line and 'InlineKeyboardButton' in line:
        # تابع بالاتر رو پیدا کن
        func_name = '?'
        for j in range(i, -1, -1):
            if lines[j].startswith('def ') or lines[j].startswith('async def '):
                func_name = lines[j].strip()[:60]
                break
        print(f"  خط {i+1} در {func_name}")
        print(f"     {line.strip()[:120]}")
        to_remove.append(i)

print(f"\n📊 تعداد دکمه‌های پیدا شده: {len(to_remove)}")

# ============================================================
# 2. حذف دکمه‌ها (فقط در توابع مالک گروه)
# ============================================================
# توابع مالک گروه
owner_group_funcs = ['group_owner_panel_menu', 'group_panel_menu', 'group_manage_menu']

removed = 0
new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    
    # چک کن که در تابع مالک گروه باشیم
    in_owner_group = False
    for j in range(i, -1, -1):
        if lines[j].startswith('def ') or lines[j].startswith('async def '):
            fname = lines[j].strip()
            for og in owner_group_funcs:
                if f'def {og}(' in fname:
                    in_owner_group = True
                    break
            break
    
    # چک کن که این خط دکمه بخش سازنده باشه
    if in_owner_group and 'owner_section_menu:' in line and 'InlineKeyboardButton' in line:
        print(f"  🗑 حذف خط {i+1}: {line.strip()[:80]}")
        removed += 1
        i += 1
        continue
    
    new_lines.append(line)
    i += 1

lines = new_lines
print(f"\n✅ {removed} دکمه حذف شد")

# ============================================================
# 3. اگه بخش سازنده در هیچ تابع مالک گروه نبود، بگو
# ============================================================
content = ''.join(lines)
has_section_in_owner = False

# پیدا کردن هر تابع مالک گروه و بررسی وجود owner_section_menu
for og in owner_group_funcs:
    # پیدا کردن تابع
    pattern = rf'def {og}\(.*?(?=\ndef |\nasync def |\Z)'
    m = re.search(pattern, content, re.DOTALL)
    if m:
        if 'owner_section_menu:' in m.group(0):
            has_section_in_owner = True
            print(f"  ⚠️ هنوز بخش سازنده در {og} هست!")

if not has_section_in_owner:
    print("  ✅ هیچ‌کدام از توابع مالک گروه، بخش سازنده ندارن")

# ============================================================
# 4. بررسی back buttons در گروه مالک
# ============================================================
print("\n=== چک دکمه‌های بازگشت در گروه مالک ===")
for og in owner_group_funcs:
    pattern = rf'def {og}\(.*?(?=\ndef |\nasync def |\Z)'
    m = re.search(pattern, content, re.DOTALL)
    if m:
        body = m.group(0)
        for i2, ln in enumerate(body.split('\n')):
            if 'بازگشت' in ln and 'callback_data' in ln:
                print(f"  {og}: {ln.strip()[:100]}")

with open('modules/start.py', 'w', encoding='utf-8') as f:
    f.write(content)

# ============================================================
# 5. کامپایل
# ============================================================
print("\n=== کامپایل ===")
try:
    py_compile.compile('modules/start.py', doraise=True)
    print("✅ کامپایل موفق")
except Exception as e:
    print(f"❌ خطا: {e}")
    shutil.copy(bak, 'modules/start.py')
    exit(1)

# ============================================================
# 6. کش + ری‌استارت
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
os.system('tail -n 6 ~/groupbot_bot.log')

print("\n" + "="*80)
print("✅ تمام شد!")
print("="*80)
