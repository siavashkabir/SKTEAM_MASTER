import os, glob, re, time, datetime

print("="*80)
print("🔍 گزارش تشخیصی جامع ربات (فقط خواندنی - هیچ تغییری اعمال نمی‌شود)")
print("="*80)

# ===== بخش 1: لیست تمام فایل‌های پایتون در پوشه modules =====
print("\n" + "="*80)
print("📁 بخش 1: لیست تمام فایل‌های ماژول (بدون بکاپ)")
print("="*80)
modules = sorted([f for f in os.listdir('modules') if f.endswith('.py') and '.bak' not in f and 'crash' not in f])
for m in modules:
    size = os.path.getsize(f'modules/{m}')
    print(f"   📄 {m} ({size} bytes)")

# ===== بخش 2: تمام هندلرهای ثبت شده در start.py =====
print("\n" + "="*80)
print("🔗 بخش 2: هندلرهای ثبت شده در start.py (به ترتیب خط)")
print("="*80)
if os.path.exists('modules/start.py'):
    with open('modules/start.py', 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if 'add_handler' in line:
                print(f"   خط {i+1}: {line.strip()[:120]}")

# ===== بخش 3: تمام Actionهای تعریف شده =====
print("\n" + "="*80)
print("⚡ بخش 3: تمام Actionهای تعریف شده (if action == ...)")
print("="*80)
actions = {}
for m in modules + ['start.py']:
    file_path = f'modules/{m}' if m != 'start.py' else 'start.py'
    if not os.path.exists(file_path): continue
    with open(file_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            match = re.search(r'action\s*==\s*["\']([^"\']+)["\']', line)
            if match:
                action = match.group(1)
                if action not in actions:
                    actions[action] = []
                actions[action].append(f"{file_path}:{i+1}")

print(f"   📊 مجموع Actionهای یکتا: {len(actions)}")
# فقط اکشن‌های مربوط به پنل و تنظیمات را نمایش می‌دهیم
relevant = {k:v for k,v in actions.items() if any(x in k.lower() for x in ['owner', 'panel', 'op_', 'set_', 'dep', 'sudo', 'menu', 'sub'])}
for action, locs in sorted(relevant.items()):
    print(f"   🔹 '{action}' -> {', '.join(locs[:3])}{' ...' if len(locs) > 3 else ''}")

# ===== بخش 4: تمام الگوهای callback_data =====
print("\n" + "="*80)
print("🔘 بخش 4: الگوهای callback_data در دکمه‌ها")
print("="*80)
callbacks = set()
for m in modules + ['start.py']:
    file_path = f'modules/{m}' if m != 'start.py' else 'start.py'
    if not os.path.exists(file_path): continue
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            match = re.search(r'callback_data\s*=\s*["\']([^"\']+)["\']', line)
            if match:
                callbacks.add(match.group(1).split(':')[0].split('_')[0])

# ===== بخش 5: توابع گمشده (مقایسه با بکاپ‌های قدیمی) =====
print("\n" + "="*80)
print("🕳️ بخش 5: توابع گمشده (در بکاپ‌های قدیمی هستند اما در فایل فعلی نیستند)")
print("="*80)

key_files = ['start.py', 'owner_panel_trigger.py', 'owner_settings.py', 'pv_main.py']
for key_file in key_files:
    current_path = f'modules/{key_file}'
    if not os.path.exists(current_path):
        print(f"\n   ❌ فایل {key_file} وجود ندارد!")
        continue
    
    with open(current_path, 'r', encoding='utf-8') as f:
        current_code = f.read()
    
    # پیدا کردن بکاپ‌های این فایل
    baks = sorted(glob.glob(f'modules/{key_file}.bak_*'), key=os.path.getctime, reverse=True)
    if not baks:
        print(f"\n   📄 {key_file}: هیچ بکاپی پیدا نشد.")
        continue
    
    # پیدا کردن توابع در جدیدترین بکاپ
    with open(baks[0], 'r', encoding='utf-8') as f:
        old_code = f.read()
    
    current_funcs = set(re.findall(r'(?:async )?def ([a-zA-Z_][a-zA-Z0-9_]*)\(', current_code))
    old_funcs = set(re.findall(r'(?:async )?def ([a-zA-Z_][a-zA-Z0-9_]*)\(', old_code))
    
    missing = old_funcs - current_funcs
    if missing:
        print(f"\n   📄 {key_file} (مقایسه با {os.path.basename(baks[0])}):")
        for func in sorted(missing):
            print(f"      ❌ تابع گمشده: {func}")
    else:
        print(f"\n   ✅ {key_file}: همه توابع موجود هستند.")

# ===== بخش 6: وضعیت دیتابیس =====
print("\n" + "="*80)
print("💾 بخش 6: وضعیت دیتابیس‌ها")
print("="*80)
for db in glob.glob('*.db') + glob.glob('data/*.db'):
    size = os.path.getsize(db) / 1024
    mtime = datetime.datetime.fromtimestamp(os.path.getmtime(db))
    print(f"   🗄️ {db}: {size:.1f} KB | آخرین تغییر: {mtime.strftime('%Y-%m-%d %H:%M')}")

# ===== بخش 7: 10 خط آخر لاگ =====
print("\n" + "="*80)
print("📜 بخش 7: 10 خط آخر لاگ ربات")
print("="*80)
os.system('tail -n 10 ~/groupbot_bot.log')

print("\n" + "="*80)
print("✅ پایان گزارش. هیچ تغییری اعمال نشد.")
print("="*80)
