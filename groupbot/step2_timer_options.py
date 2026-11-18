import os, shutil, py_compile, time, re, subprocess

print("="*80)
print("🔧 قدم ۲: تغییر گزینه‌های تایمر به 30s/1m/3m/5m")
print("="*80)

# ===== 1. بکاپ =====
ts = time.strftime("%H%M%S")
bak1 = f'modules/owner_set_group.py.bak_step2_{ts}'
bak2 = f'modules/system_management.py.bak_step2_{ts}'

try:
    shutil.copy('modules/owner_set_group.py', bak1)
    shutil.copy('modules/system_management.py', bak2)
    print(f"✅ بکاپ 1: {bak1}")
    print(f"✅ بکاپ 2: {bak2}")
except Exception as e:
    print(f"❌ خطا در بکاپ: {e}")
    exit(1)

# ===== 2. اصلاح owner_set_group.py =====
print("\n=== اصلاح owner_set_group.py ===")
try:
    with open('modules/owner_set_group.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    old = "opts = [60, 120, 180, 300, 600, 900, 1800]"
    new = "opts = [30, 60, 180, 300]"
    
    if old in content:
        content = content.replace(old, new)
        with open('modules/owner_set_group.py', 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ گزینه‌های owner_set_pt تغییر کرد.")
    else:
        # تلاش با regex
        pattern = r'opts\s*=\s*\[60,\s*120,\s*180,\s*300,\s*600,\s*900,\s*1800\]'
        if re.search(pattern, content):
            content = re.sub(pattern, new, content)
            with open('modules/owner_set_group.py', 'w', encoding='utf-8') as f:
                f.write(content)
            print("✅ گزینه‌های owner_set_pt با regex تغییر کرد.")
        else:
            print("⚠️ الگوی opts در owner_set_group.py پیدا نشد.")
    
    py_compile.compile('modules/owner_set_group.py', doraise=True)
    print("✅ کامپایل owner_set_group.py موفق.")

except Exception as e:
    print(f"❌ خطا: {e}")
    shutil.copy(bak1, 'modules/owner_set_group.py')
    print("⚠️ بکاپ 1 ریستور شد.")
    exit(1)

# ===== 3. اصلاح system_management.py =====
print("\n=== اصلاح system_management.py ===")
try:
    with open('modules/system_management.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    old = 'opts = ["60", "120", "180", "300", "600", "900", "1800"]'
    new = 'opts = ["30", "60", "180", "300"]'
    
    if old in content:
        content = content.replace(old, new)
        with open('modules/system_management.py', 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ گزینه‌های sys_set_pt تغییر کرد.")
    else:
        pattern = r'opts\s*=\s*\["60",\s*"120",\s*"180",\s*"300",\s*"600",\s*"900",\s*"1800"\]'
        if re.search(pattern, content):
            content = re.sub(pattern, new, content)
            with open('modules/system_management.py', 'w', encoding='utf-8') as f:
                f.write(content)
            print("✅ گزینه‌های sys_set_pt با regex تغییر کرد.")
        else:
            print("⚠️ الگوی opts در system_management.py پیدا نشد.")
    
    py_compile.compile('modules/system_management.py', doraise=True)
    print("✅ کامپایل system_management.py موفق.")

except Exception as e:
    print(f"❌ خطا: {e}")
    shutil.copy(bak2, 'modules/system_management.py')
    print("⚠️ بکاپ 2 ریستور شد.")
    exit(1)

# ===== 4. تأیید نهایی =====
print("\n=== تأیید نهایی ===")
r1 = subprocess.run(['grep', '-n', 'opts = ', 'modules/owner_set_group.py'], capture_output=True, text=True)
print("owner_set_group.py:")
for line in r1.stdout.split('\n'):
    if line.strip():
        print(f"   {line.strip()[:100]}")

r2 = subprocess.run(['grep', '-n', 'opts = ', 'modules/system_management.py'], capture_output=True, text=True)
print("\nsystem_management.py:")
for line in r2.stdout.split('\n'):
    if line.strip() and 'opt' in line.lower():
        print(f"   {line.strip()[:100]}")

# ===== 5. ری‌استارت =====
print("\n=== ری‌استارت ربات ===")
os.system('pkill -9 -f "main.py"')
time.sleep(3)
os.system('cd ~/groupbot && bash -c "source venv/bin/activate && nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 &"')
time.sleep(5)
print("✅ ربات ری‌استارت شد.")

print("\n=== 10 خط آخر لاگ ===")
os.system('tail -n 10 ~/groupbot_bot.log')

print("\n" + "="*80)
print("✅ قدم ۲ کامل شد!")
print("="*80)
print("\n📌 گزینه‌های جدید تایمر: 30s / 1m / 3m / 5m")
print("📌 محل تنظیم: منوی «تنظیمات این گروه» یا «منوی سیستم»")
