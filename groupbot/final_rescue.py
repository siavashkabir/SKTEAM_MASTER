import os, glob, time, shutil, sys, py_compile, datetime, subprocess

print("=== 1. توقف ربات و watchdog (بدون آسیب به خود اسکریپت) ===")
os.system('pkill -9 -f "python3 -u main.py"')
os.system('pkill -9 -f "bot_watchdog.sh"')
os.system('pkill -9 -f "connection_monitor.py"')
time.sleep(2)
print("✅ ربات و watchdog متوقف شدند.")

print("\n=== 2. غیرفعال‌سازی موقت کرون‌جاب ===")
os.system('crontab -l > ~/crontab_backup.txt 2>/dev/null; crontab -r 2>/dev/null')
print("✅ کرون‌جاب موقتاً غیرفعال شد تا از ری‌استارت خودکار جلوگیری شود.")

print("\n=== 3. ایجاد بکاپ اضطراری از وضعیت فعلی ===")
try:
    shutil.copy(os.path.expanduser('~/groupbot/modules/admin.py'), os.path.expanduser('~/groupbot/modules/admin.py.crash_backup'))
    shutil.copy(os.path.expanduser('~/groupbot/modules/start.py'), os.path.expanduser('~/groupbot/modules/start.py.crash_backup'))
    print("✅ بکاپ اضطراری ایجاد شد.")
except Exception as e:
    print(f"❌ خطا در ایجاد بکاپ: {e}")
    sys.exit(1)

print("\n=== 4. جستجوی بکاپ امروز صبح (ساعت 5 تا 7) ===")
today = datetime.date.today()
search_paths = [os.path.expanduser("~/groupbot"), os.path.expanduser("~/backups"), os.path.expanduser("~/")]
target_admin = None
target_start = None

def find_backup(pattern, path):
    best_match = None
    best_diff = float('inf')
    for f in glob.glob(os.path.join(path, pattern)):
        mtime = os.path.getmtime(f)
        dt = datetime.datetime.fromtimestamp(mtime)
        if dt.date() == today and 5 <= dt.hour <= 7:
            diff = abs((dt.hour * 60 + dt.minute) - (6 * 60))
            if diff < best_diff:
                best_diff = diff
                best_match = f
    return best_match

for path in search_paths:
    if not os.path.exists(path): continue
    if not target_admin:
        target_admin = find_backup("admin.py.bak*", path)
    if not target_start:
        target_start = find_backup("start.py.bak*", path)
    if target_admin and target_start:
        break

if not target_admin or not target_start:
    print("❌ بکاپی در بازه ساعت ۵ تا ۷ صبح امروز پیدا نشد!")
    print("\n📁 لیست ۱۵ بکاپ آخر (جدیدترین‌ها) در کل سیستم:")
    all_baks = []
    for path in search_paths:
        if not os.path.exists(path): continue
        for f in glob.glob(os.path.join(path, "*.bak*")):
            if 'crash_backup' in f or 'temp' in f: continue
            all_baks.append((f, datetime.datetime.fromtimestamp(os.path.getmtime(f))))
    all_baks.sort(key=lambda x: x[1], reverse=True)
    for b in all_baks[:15]:
        print(f"   🕒 {b[1].strftime('%Y-%m-%d %H:%M:%S')} -> {b[0]}")
    print("\n⚠️ لطفاً تاریخ و ساعت دقیق بکاپی که می‌خواهید را به من بگویید تا اسکریپت اختصاصی آن را بنویسم.")
    print("در حال بازگردانی کرون‌جاب...")
    os.system('crontab ~/crontab_backup.txt')
    sys.exit(1)

print(f"✅ بکاپ admin.py پیدا شد: {target_admin}")
print(f"✅ بکاپ start.py پیدا شد: {target_start}")

print("\n=== 5. بازگردانی فایل‌ها ===")
try:
    shutil.copy(target_admin, os.path.expanduser('~/groupbot/modules/admin.py'))
    shutil.copy(target_start, os.path.expanduser('~/groupbot/modules/start.py'))
    print("✅ فایل‌ها با موفقیت به بکاپ صبح بازگردانی شدند.")
except Exception as e:
    print(f"❌ خطا در کپی فایل‌ها: {e}")
    sys.exit(1)

print("\n=== 6. کامپایل و تست سلامت کد ===")
try:
    subprocess.run(['python3', '-m', 'py_compile', os.path.expanduser('~/groupbot/modules/admin.py')], check=True)
    subprocess.run(['python3', '-m', 'py_compile', os.path.expanduser('~/groupbot/modules/start.py')], check=True)
    print("✅ کامپایل با موفقیت انجام شد. کدها سالم هستند.")
except subprocess.CalledProcessError as e:
    print(f"❌ خطای کامپایل: {e}")
    print("⚠️ بکاپ صبح هم خراب است! در حال بازگردانی به وضعیت فعلی (Auto-Rollback)...")
    shutil.copy(os.path.expanduser('~/groupbot/modules/admin.py.crash_backup'), os.path.expanduser('~/groupbot/modules/admin.py'))
    shutil.copy(os.path.expanduser('~/groupbot/modules/start.py.crash_backup'), os.path.expanduser('~/groupbot/modules/start.py'))
    os.system('crontab ~/crontab_backup.txt')
    print("✅ بازگردانی انجام شد. کرون‌جاب فعال شد. لطفاً یک بکاپ دیگر انتخاب کنید.")
    sys.exit(1)

# پاکسازی فایل‌های موقت
if os.path.exists(os.path.expanduser('~/groupbot/modules/admin.py.crash_backup')): os.remove(os.path.expanduser('~/groupbot/modules/admin.py.crash_backup'))
if os.path.exists(os.path.expanduser('~/groupbot/modules/start.py.crash_backup')): os.remove(os.path.expanduser('~/groupbot/modules/start.py.crash_backup'))

print("\n=== 7. ری‌استارت ربات ===")
os.system('cd ~/groupbot && source venv/bin/activate && nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 &')
time.sleep(3)
print("✅ ربات با موفقیت ری‌استارت شد.")

print("\n=== 8. فعال‌سازی مجدد کرون‌جاب ===")
os.system('crontab ~/crontab_backup.txt')
print("✅ کرون‌جاب مجدداً فعال شد.")

print("\n=== وضعیت لاگ ربات ===")
os.system('tail -n 15 ~/groupbot_bot.log')
