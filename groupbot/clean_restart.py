import os, shutil, time

print("="*80)
print("🔧 ری‌استارت تمیز + پاک کردن کش")
print("="*80)

# ==== 1. کشتن همه نسخه‌ها ====
print("\n=== 1. کشتن همه پردازش‌ها ===")
for p in ["main.py", "connection_monitor.py", "bot_watchdog.sh", "run_bot.sh"]:
    os.system(f'pkill -9 -f "{p}"')
    print(f"   ✅ کشته شد: {p}")
time.sleep(4)

# ==== 2. پاک کردن کش .pyc ====
print("\n=== 2. پاک کردن __pycache__ ===")
for root, dirs, files in os.walk('.'):
    if 'venv' in root:
        continue
    if '__pycache__' in root:
        try:
            shutil.rmtree(root, ignore_errors=True)
            print(f"   🗑 حذف: {root}")
        except Exception as e:
            print(f"   ⚠️ {e}")

# ==== 3. بکاپ اضطراری ====
ts = time.strftime("%H%M%S")
shutil.copy('modules/start.py', f'modules/start.py.bak_clean_{ts}')
print(f"\n✅ بکاپ اضطراری: modules/start.py.bak_clean_{ts}")

# ==== 4. تأیید وضعیت کد ====
print("\n=== 3. تأیید وضعیت کد ===")
with open('modules/start.py', 'r', encoding='utf-8') as f:
    content = f.read()

# چک دکمه جدید
if 'owner_section_menu:' in content:
    print("   ✅ دکمه «بخش سازنده» در کد هست.")
else:
    print("   ❌ دکمه «بخش سازنده» پیدا نشد!")

# چک دکمه‌های قدیمی حذف شدن (در owner_manage_menu)
import re
# پیدا کردن تابع owner_manage_menu
m = re.search(r'def owner_manage_menu\(.*?(?=\ndef |\nasync def |\Z)', content, re.DOTALL)
if m:
    func_body = m.group(0)
    old_btns_found = []
    for btn in ['menu_owners:', 'menu_admins:', 'menu_vip:', 'menu_deputies:', 'menu_admin_perms:']:
        if btn in func_body:
            old_btns_found.append(btn)
    
    if old_btns_found:
        print(f"   ❌ دکمه‌های قدیمی هنوز در owner_manage_menu: {old_btns_found}")
    else:
        print("   ✅ همه ۵ دکمه قدیمی حذف شدن.")
else:
    print("   ❌ owner_manage_menu پیدا نشد!")

# ==== 5. راه‌اندازی مجدد watchdog ====
print("\n=== 4. راه‌اندازی مجدد ===")
os.system('cd ~/groupbot && nohup bash bot_watchdog.sh > ~/groupbot_watchdog.log 2>&1 &')
time.sleep(12)

# ==== 6. بررسی نهایی ====
print("\n=== 5. بررسی نهایی ===")
result = os.popen('ps aux | grep -E "main.py|connection_monitor" | grep -v grep').read()
print(result if result.strip() else "❌ هیچی نیست!")

main_count = result.count('python3 -u main.py')
mon_count = result.count('connection_monitor.py')
print(f"\n🎯 ربات: {main_count} | مانیتور: {mon_count}")

print("\n=== 6. 10 خط آخر لاگ ===")
os.system('tail -n 10 ~/groupbot_bot.log')

print("\n" + "="*80)
print("✅ تمام! حالا در تلگرام 'پنل' بزن.")
print("="*80)
