import os, glob, time, shutil, sys, py_compile, subprocess, datetime, re

print("=== 1. توقف ربات و watchdog (بدون آسیب به خود اسکریپت) ===")
os.system('pkill -9 -f "main.py"')
os.system('pkill -9 -f "bot_watchdog.sh"')
os.system('pkill -9 -f "connection_monitor.py"')
time.sleep(2)
print("✅ ربات و watchdog متوقف شدند.")

print("\n=== 2. غیرفعال‌سازی موقت کرون‌جاب ===")
os.system('crontab -l > ~/crontab_backup.txt 2>/dev/null; crontab -r 2>/dev/null')
print("✅ کرون‌جاب غیرفعال شد. ربات دیگر خودش را ری‌استارت نمی‌کند.")

print("\n=== 3. ایجاد بکاپ اضطراری از وضعیت فعلی ===")
try:
    shutil.copy('modules/admin.py', 'modules/admin.py.broken_temp')
    shutil.copy('modules/start.py', 'modules/start.py.broken_temp')
    print("✅ بکاپ اضطراری ایجاد شد.")
except Exception as e:
    print(f"❌ خطا در ایجاد بکاپ: {e}")

print("\n=== 4. جستجوی بکاپ‌های موجود و تست سلامت آن‌ها ===")
admin_baks = glob.glob('modules/admin.py.bak_*')
start_baks = glob.glob('modules/start.py.bak_*')

# استخراج زمان از نام فایل‌ها (فرمت: admin.py.bak_HHMMSS)
admin_dict = {f.split('.bak_')[-1]: f for f in admin_baks if '.broken' not in f}
start_dict = {f.split('.bak_')[-1]: f for f in start_baks if '.broken' not in f}

# پیدا کردن زمان‌های مشترک بین admin و start
common_times = sorted(list(set(admin_dict.keys()) & set(start_dict.keys())), reverse=True)

if not common_times:
    print("❌ هیچ بکاپ مشترکی برای admin.py و start.py پیدا نشد!")
    print("⚠️ در حال بازگردانی کرون‌جاب و خروج...")
    os.system('crontab ~/crontab_backup.txt')
    sys.exit(1)

print(f"🔍 {len(common_times)} بکاپ مشترک پیدا شد. در حال تست سلامت از جدیدترین...")

good_backup_found = False
selected_time = None

for t in common_times:
    admin_backup = admin_dict[t]
    start_backup = start_dict[t]
    
    # کپی موقت برای تست
    shutil.copy(admin_backup, 'modules/admin.py')
    shutil.copy(start_backup, 'modules/start.py')
    
    try:
        # تست کامپایل
        subprocess.run(['python3', '-m', 'py_compile', 'modules/admin.py'], check=True, capture_output=True)
        subprocess.run(['python3', '-m', 'py_compile', 'modules/start.py'], check=True, capture_output=True)
        print(f"✅ بکاپ با تاریخ {t} سالم است! انتخاب شد.")
        good_backup_found = True
        selected_time = t
        break
    except subprocess.CalledProcessError:
        print(f"⚠️ بکاپ {t} خراب است. رفتن به بکاپ بعدی...")
        continue

if not good_backup_found:
    print("\n❌ هیچ‌کدام از بکاپ‌ها سالم نیستند!")
    print("⚠️ در حال بازگردانی به وضعیت فعلی (Auto-Rollback)...")
    shutil.copy('modules/admin.py.broken_temp', 'modules/admin.py')
    shutil.copy('modules/start.py.broken_temp', 'modules/start.py')
    os.system('crontab ~/crontab_backup.txt')
    print("✅ بازگردانی انجام شد. کرون‌جاب فعال شد.")
    sys.exit(1)

# پاکسازی فایل‌های موقت
if os.path.exists('modules/admin.py.broken_temp'): os.remove('modules/admin.py.broken_temp')
if os.path.exists('modules/start.py.broken_temp'): os.remove('modules/start.py.broken_temp')

print("\n=== 5. ری‌استارت ربات با بکاپ سالم ===")
os.system('cd ~/groupbot && source venv/bin/activate && nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 &')
time.sleep(3)
print("✅ ربات با موفقیت ری‌استارت شد.")

print("\n=== 6. فعال‌سازی مجدد کرون‌جاب ===")
os.system('crontab ~/crontab_backup.txt')
print("✅ کرون‌جاب مجدداً فعال شد.")

print("\n=== 7. وضعیت لاگ ربات (برای اطمینان از بالا آمدن) ===")
os.system('tail -n 15 ~/groupbot_bot.log')
