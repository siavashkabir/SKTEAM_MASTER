import os, shutil, py_compile, time, re

print("="*80)
print("🔒 افزودن چک دسترسی به ۵ handler بخش سازنده")
print("="*80)

ts = time.strftime("%H%M%S")
bak = f'modules/start.py.bak_perm_{ts}'
shutil.copy('modules/start.py', bak)
print(f"✅ بکاپ: {bak}")

with open('modules/start.py', 'r', encoding='utf-8') as f:
    content = f.read()

# ۵ handler بخش سازنده
handlers = [
    ('op_botadmins', 'در مدیریت ادمین‌های ربات'),
    ('rmt_groups', 'در مدیریت گروه‌ها'),
    ('s_fj_menu', 'در جوین اجباری'),
    ('s_op_sudo_stats', 'در آمار سودوها'),
    ('s_op_group_stats', 'در آمار گروه‌ها'),
]

# بررسی که از قبل اضافه نشده
if '# [PERM CHECK]' in content:
    print("⚠️ از قبل اضافه شده!")
    exit(0)

# پیدا کردن هر handler و اضافه کردن چک
for action, desc in handlers:
    # الگوی: if action == "X":\n        try:
    pattern = rf'(    if action == "{action}":\s*\n)(\s*try:)'
    match = re.search(pattern, content)
    
    if match:
        indent = ' ' * (len(match.group(1)) - len(match.group(1).lstrip()) + 4)
        perm_check = f'''        # [PERM CHECK] فقط سازنده/سودو
        try:
            from config import OWNER_ID
            from database import is_bot_admin
            _is_owner = (query.from_user.id == OWNER_ID)
            _is_sudo = False
            if not _is_owner:
                try:
                    _is_sudo = is_bot_admin(query.from_user.id)
                except Exception:
                    pass
            if not (_is_owner or _is_sudo):
                await query.answer("⛔ فقط سازنده و سودو دسترسی دارند.", show_alert=True)
                return
        except Exception as _pe:
            print("[PERM CHECK ERR] " + str(_e if False else _pe))
            return

'''
        # درج چک بعد از try:
        insertion = match.group(2) + '\n' + perm_check
        content = content[:match.start(2)] + insertion + content[match.end(2):]
        print(f"   ✅ {action}: چک دسترسی اضافه شد")
    else:
        print(f"   ⚠️ {action}: handler پیدا نشد")

with open('modules/start.py', 'w', encoding='utf-8') as f:
    f.write(content)

# کامپایل
print("\n=== کامپایل ===")
try:
    py_compile.compile('modules/start.py', doraise=True)
    print("✅ کامپایل موفق")
except Exception as e:
    print(f"❌ خطا: {e}")
    shutil.copy(bak, 'modules/start.py')
    exit(1)

# پاک کردن کش
print("\n=== پاک کردن کش ===")
for root, dirs, files in os.walk('.'):
    if 'venv' in root:
        continue
    if '__pycache__' in root:
        shutil.rmtree(root, ignore_errors=True)

# ری‌استارت
print("\n=== ری‌استارت ===")
os.system('pkill -9 -f "main.py"')
os.system('pkill -9 -f "connection_monitor.py"')
time.sleep(4)
os.system('cd ~/groupbot && nohup bash bot_watchdog.sh > ~/groupbot_watchdog.log 2>&1 &')
time.sleep(10)
os.system('tail -n 6 ~/groupbot_bot.log')

print("\n" + "="*80)
print("✅ چک دسترسی به ۵ handler اضافه شد!")
print("="*80)
