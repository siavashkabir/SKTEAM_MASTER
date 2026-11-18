import os, re, glob

print("="*80)
print("🔍 AUDIT کامل پنل سازنده (بدون تغییر)")
print("="*80)

# ============================================================
# 1. لیست توابع منوی پنل سازنده
# ============================================================
CREATOR_MENUS = {
    'sudo_panel_menu': 'منوی اصلی سازنده',
    'owner_manage_menu': 'منوی مدیریت (قدیم)',
    'owner_section_menu': 'بخش سازنده',
    'owner_settings_menu': 'تنظیمات گروه (مشترک)',
    'group_owner_panel_menu': 'پنل مالک گروه',
}

# ============================================================
# 2. جمع‌آوری همه دکمه‌های پنل سازنده
# ============================================================
print("\n" + "="*80)
print("1️⃣  دکمه‌های پنل سازنده (callback_data)")
print("="*80)

with open('modules/start.py', 'r', encoding='utf-8') as f:
    start_lines = f.readlines()
    start_content = ''.join(start_lines)

creator_callbacks = {}  # callback -> list of (func_name, line_num, label)

for menu_func, menu_label in CREATOR_MENUS.items():
    # پیدا کردن تابع
    start = None
    for i, line in enumerate(start_lines):
        if line.startswith(f'def {menu_func}('):
            start = i
            break
    
    if start is None:
        print(f"\n❌ {menu_func}: پیدا نشد")
        continue
    
    end = len(start_lines)
    for j in range(start+1, len(start_lines)):
        if start_lines[j].startswith('def ') or start_lines[j].startswith('async def '):
            end = j
            break
    
    print(f"\n┌─ {menu_label} ({menu_func}) - خطوط {start+1}-{end}")
    
    for i in range(start, end):
        line = start_lines[i]
        if 'InlineKeyboardButton' not in line:
            continue
        
        # استخراج callback
        m = re.search(r'callback_data=["\']([^"\']+)["\']', line)
        cb = None
        if m:
            cb = m.group(1)
        else:
            m = re.search(r'callback_data=f["\']([^"\']+)["\']', line)
            if m:
                cb = m.group(1)
        
        if not cb:
            continue
        
        # استخراج label
        m2 = re.search(r'InlineKeyboardButton\(["\']([^"\']+)["\']', line)
        label = m2.group(1)[:45] if m2 else '?'
        
        # نرمال‌سازی callback (حذف {uid}:{chat_id} و ...)
        cb_normalized = cb.split(':')[0] if ':' in cb else cb
        
        if cb_normalized not in creator_callbacks:
            creator_callbacks[cb_normalized] = []
        creator_callbacks[cb_normalized].append((menu_func, i+1, label))
        print(f"│  🔘 خط {i+1}: {label}")
        print(f"│     callback: {cb[:90]}")

# ============================================================
# 3. جمع‌آوری همه handlerها
# ============================================================
print("\n" + "="*80)
print("2️⃣  تمام handlerهای موجود (action ==)")
print("="*80)

all_handlers = {}  # action -> list of (file, line_num)

# start.py
for i, line in enumerate(start_lines):
    m = re.search(r'action\s*==\s*["\']([^"\']+)["\']', line)
    if m:
        action = m.group(1)
        if action not in all_handlers:
            all_handlers[action] = []
        all_handlers[action].append(('start.py', i+1))
    
    # startswith
    m = re.search(r'action\.startswith\(["\']([^"\']+)["\']', line)
    if m:
        action = m.group(1)
        if action not in all_handlers:
            all_handlers[action] = []
        all_handlers[action].append(('start.py', i+1))

# modules
for mfile in glob.glob('modules/*.py'):
    if '.bak' in mfile or 'crash' in mfile:
        continue
    with open(mfile, 'r', encoding='utf-8') as f:
        mlines = f.readlines()
    for i, line in enumerate(mlines):
        m = re.search(r'action\s*==\s*["\']([^"\']+)["\']', line)
        if m:
            action = m.group(1)
            if action not in all_handlers:
                all_handlers[action] = []
            all_handlers[action].append((mfile, i+1))
        
        m = re.search(r'action\.startswith\(["\']([^"\']+)["\']', line)
        if m:
            action = m.group(1)
            if action not in all_handlers:
                all_handlers[action] = []
            all_handlers[action].append((mfile, i+1))

print(f"\n📊 مجموع handlerهای یگانه: {len(all_handlers)}")

# ============================================================
# 4. تطبیق دکمه‌ها با handlerها
# ============================================================
print("\n" + "="*80)
print("3️⃣  وضعیت دکمه‌های پنل سازنده (کدوم کار می‌کنه، کدوم نه)")
print("="*80)

missing = []
working = []

for cb, locations in sorted(creator_callbacks.items()):
    if cb in all_handlers:
        working.append((cb, locations))
    else:
        missing.append((cb, locations))

print(f"\n✅ {len(working)} دکمه کار می‌کنه:")
for cb, locs in working:
    menu_func, line_num, label = locs[0]
    print(f"   ✅ {cb:35s} | {label}")

print(f"\n❌ {len(missing)} دکمه احتمالاً کار نمی‌کنه:")
for cb, locs in missing:
    for menu_func, line_num, label in locs:
        print(f"   ❌ {cb:35s} | {label}")
        print(f"        در {menu_func} خط {line_num}")

# ============================================================
# 5. پیدا کردن handlerهای بدون کالبک (کد مرده)
# ============================================================
print("\n" + "="*80)
print("4️⃣  هندلرهای بدون کالبک (کد مرده محتمل)")
print("="*80)

# جمع‌آوری همه callback_data های استفاده شده در همه فایل‌ها
all_used_callbacks = set()
for mfile in glob.glob('modules/*.py') + ['main.py']:
    if '.bak' in mfile or 'crash' in mfile or not os.path.exists(mfile):
        continue
    with open(mfile, 'r', encoding='utf-8') as f:
        content = f.read()
    for m in re.finditer(r'callback_data=["\']([^"\']+)["\']', content):
        all_used_callbacks.add(m.group(1).split(':')[0])
    for m in re.finditer(r'callback_data=f["\']([^"\']+)["\']', content):
        all_used_callbacks.add(m.group(1).split(':')[0])

dead_handlers = []
for action, locs in sorted(all_handlers.items()):
    # چک کن که آیا این handler توی کالبک‌ها هست
    if action not in all_used_callbacks:
        dead_handlers.append((action, locs))

print(f"\n⚠️ {len(dead_handlers)} handler کالبک نداره (ممکنه کد مرده باشه):")
for action, locs in dead_handlers[:40]:
    print(f"   ⚠️ {action}")
    for f, ln in locs[:2]:
        print(f"        {f}:{ln}")

# ============================================================
# 6. pattern‌های ثبت شده
# ============================================================
print("\n" + "="*80)
print("5️⃣  patternهای ثبت‌شده در start.py")
print("="*80)

for i, line in enumerate(start_lines):
    if 'add_handler' in line and 'pattern=' in line:
        m = re.search(r'pattern=["\']([^"\']+)["\']', line)
        if m:
            pat = m.group(1)
            parts = pat.replace('^(', '').replace(')$', '').split('|')
            print(f"\n📍 خط {i+1}: {len(parts)} کالبک")
            print(f"   {pat[:120]}")
            
            # چک کن کدوم از creator_callbacks در این pattern هستن
            present = [cb for cb in creator_callbacks if cb in parts]
            if present:
                print(f"   📌 از پنل سازنده: {present}")

# ============================================================
# 7. خلاصه نهایی
# ============================================================
print("\n" + "="*80)
print("📊 خلاصه نهایی")
print("="*80)
print(f"""
🔍 پنل سازنده:
   • دکمه‌های یگانه: {len(creator_callbacks)}
   • کار می‌کنن: {len(working)} ✅
   • کار نمی‌کنن: {len(missing)} ❌

🗂️ کل پروژه:
   • handlerهای یگانه: {len(all_handlers)}
   • کد مرده محتمل: {len(dead_handlers)}
""")

if missing:
    print("\n⚠️ دکمه‌های معیوب پنل سازنده:")
    for cb, locs in missing:
        print(f"   • {cb}")
