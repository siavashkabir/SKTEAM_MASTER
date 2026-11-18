import os, shutil, py_compile, time

print("="*80)
print("🔒 افزودن چک دسترسی (روش خط به خط، امن)")
print("="*80)

ts = time.strftime("%H%M%S")
bak = f'modules/start.py.bak_permsafe_{ts}'
shutil.copy('modules/start.py', bak)
print(f"✅ بکاپ: {bak}")

# ============================================================
# 1. بررسی سلامت فایل فعلی
# ============================================================
try:
    py_compile.compile('modules/start.py', doraise=True)
    print("✅ فایل فعلی سالم است")
except Exception as e:
    print(f"❌ فایل خراب است: {e}")
    exit(1)

# ============================================================
# 2. خواندن خطوط
# ============================================================
with open('modules/start.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# ============================================================
# 3. پیدا کردن handlerهایی که چک دسترسی ندارن
# ============================================================
# ما 4 تا رو باید چک کنیم: rmt_groups, s_fj_menu, s_op_sudo_stats, s_op_group_stats
targets = ['rmt_groups', 's_fj_menu', 's_op_sudo_stats', 's_op_group_stats']

# ساخت بلوک چک دسترسی (indent = 8 spaces)
perm_check = '''            # [PERM CHECK] only owner/sudo
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
                    await query.answer("\u26d4 \u0641\u0642\u0637 \u0633\u0627\u0632\u0646\u062f\u0647 \u0648 \u0633\u0648\u062f\u0648 \u062f\u0633\u062a\u0631\u0633\u06cc \u062f\u0627\u0631\u0646\u062f.", show_alert=True)
                    return
            except Exception as _pe:
                print("[PERM CHECK ERR] " + str(_pe))
                return
'''

changes = 0

for target in targets:
    # پیدا کردن handler
    handler_idx = None
    for i, line in enumerate(lines):
        # باید دقیقاً اگر با 4 فاصله شروع بشه
        if line.rstrip() == f'    if action == "{target}":':
            handler_idx = i
            break
    
    if handler_idx is None:
        print(f"⚠️ {target}: handler پیدا نشد")
        continue
    
    # چک کن که از قبل اضافه نشده
    already = False
    for j in range(handler_idx, min(handler_idx + 20, len(lines))):
        if '[PERM CHECK]' in lines[j]:
            already = True
            break
        if j > handler_idx and lines[j].startswith('    if '):
            break
    
    if already:
        print(f"ℹ️ {target}: از قبل چک داره")
        continue
    
    # پیدا کردن خط try: که بعد از handler_idx هست
    try_idx = None
    for j in range(handler_idx + 1, min(handler_idx + 5, len(lines))):
        if lines[j].strip() == 'try:':
            try_idx = j
            break
        if lines[j].startswith('    if '):  # handler بعدی رسید
            break
    
    if try_idx is None:
        # شاید بلوک try نباشه، مستقیم کد داره
        # بعد از handler_idx درج می‌کنیم
        insert_idx = handler_idx + 1
        print(f"   ℹ️ {target}: بدون try، درج بعد از handler")
    else:
        # درج داخل try (بعد از try_idx)
        insert_idx = try_idx + 1
        print(f"   ✅ {target}: درج داخل try (خط {try_idx+1})")
    
    # درج خطوط چک
    perm_lines = [l + '\n' for l in perm_check.split('\n') if l or l == '']
    # حذف خط آخر اگر خالیه
    while perm_lines and perm_lines[-1].strip() == '':
        perm_lines.pop()
    perm_lines.append('\n')  # یک خط خالی آخر
    
    lines[insert_idx:insert_idx] = perm_lines
    changes += 1
    print(f"   ✅ {target}: چک دسترسی اضافه شد")

print(f"\n📊 مجموع: {changes} handler اصلاح شد")

# ============================================================
# 4. نوشتن
# ============================================================
with open('modules/start.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

# ============================================================
# 5. کامپایل
# ============================================================
print("\n=== کامپایل ===")
try:
    py_compile.compile('modules/start.py', doraise=True)
    print("✅ کامپایل موفق")
except Exception as e:
    print(f"❌ خطای کامپایل: {e}")
    shutil.copy(bak, 'modules/start.py')
    print("⚠️ Auto-Rollback انجام شد")
    exit(1)

# ============================================================
# 6. پاک کردن کش
# ============================================================
print("\n=== پاک کردن __pycache__ ===")
for root, dirs, files in os.walk('.'):
    if 'venv' in root:
        continue
    if '__pycache__' in root:
        shutil.rmtree(root, ignore_errors=True)

# ============================================================
# 7. ری‌استارت
# ============================================================
print("\n=== ری‌استارت ربات ===")
os.system('pkill -9 -f "main.py"')
os.system('pkill -9 -f "connection_monitor.py"')
time.sleep(4)
os.system('cd ~/groupbot && nohup bash bot_watchdog.sh > ~/groupbot_watchdog.log 2>&1 &')
time.sleep(10)
os.system('tail -n 6 ~/groupbot_bot.log')

print("\n" + "="*80)
print("✅ تمام! الان فقط سازنده و سودو می‌تونن به 4 handler دسترسی داشته باشن.")
print("="*80)
