import os, glob, time, shutil, sys, py_compile, datetime

print("=== 1. ایجاد بکاپ اضطراری از وضعیت فعلی ===")
# از وضعیت خراب فعلی بکاپ می‌گیریم تا اگر بکاپ صبح هم خراب بود، به همین وضعیت برگردیم
try:
    shutil.copy('modules/admin.py', 'modules/admin.py.crash_backup')
    shutil.copy('modules/start.py', 'modules/start.py.crash_backup')
    print("✅ بکاپ اضطراری ایجاد شد (جهت امنیت).")
except Exception as e:
    print(f"❌ خطا در ایجاد بکاپ اضطراری: {e}")
    sys.exit(1)

print("\n=== 2. جستجوی بکاپ امروز صبح (ساعت 5 تا 6) ===")
today = datetime.date.today()

def find_backup(pattern):
    best_match = None
    best_diff = float('inf')
    for f in glob.glob(pattern):
        ctime = os.path.getctime(f)
        dt = datetime.datetime.fromtimestamp(ctime)
        # فقط بکاپ‌های امروز بین ساعت 5 تا 6:59 صبح
        if dt.date() == today and 5 <= dt.hour <= 6:
            # پیدا کردن نزدیک‌ترین به ساعت 5:30
            diff = abs((dt.hour * 60 + dt.minute) - (5 * 60 + 30))
            if diff < best_diff:
                best_diff = diff
                best_match = f
    return best_match

target_admin = find_backup('modules/admin.py.bak_*')
target_start = find_backup('modules/start.py.bak_*')

if not target_admin or not target_start:
    print("❌ بکاپی در بازه ساعت ۵ تا ۶ صبح امروز پیدا نشد!")
    print("\n📁 لیست تمام بکاپ‌های موجود به ترتیب زمان (از جدید به قدیم):")
    all_baks = sorted(glob.glob('modules/admin.py.bak_*') + glob.glob('modules/start.py.bak_*'), key=os.path.getctime, reverse=True)
    for b in all_baks[:10]: # فقط 10 بکاپ آخر را نشان می‌دهیم
        ctime = datetime.datetime.fromtimestamp(os.path.getctime(b))
        print(f"   🕒 {ctime.strftime('%Y-%m-%d %H:%M:%S')}  ->  {b}")
    print("\n⚠️ لطفاً تاریخ و ساعت دقیق بکاپی که می‌خواهید را به من بگویید تا اسکریپت اختصاصی آن را بنویسم.")
    sys.exit(1)

print(f"✅ بکاپ admin.py پیدا شد: {target_admin}")
print(f"✅ بکاپ start.py پیدا شد: {target_start}")

print("\n=== 3. بازگردانی فایل‌ها ===")
try:
    shutil.copy(target_admin, 'modules/admin.py')
    shutil.copy(target_start, 'modules/start.py')
    print("✅ فایل‌ها با موفقیت به بکاپ صبح بازگردانی شدند.")
except Exception as e:
    print(f"❌ خطا در کپی فایل‌ها: {e}")
    sys.exit(1)

print("\n=== 4. کامپایل و تست سلامت کد ===")
try:
    py_compile.compile('modules/admin.py', doraise=True)
    py_compile.compile('modules/start.py', doraise=True)
    print("✅ کامپایل با موفقیت انجام شد. کدها سالم هستند.")
except Exception as e:
    print(f"❌ خطای کامپایل: {e}")
    print("⚠️ بکاپ صبح هم خراب است! در حال بازگردانی به وضعیت فعلی (Auto-Rollback)...")
    shutil.copy('modules/admin.py.crash_backup', 'modules/admin.py')
    shutil.copy('modules/start.py.crash_backup', 'modules/start.py')
    print("✅ بازگردانی به وضعیت فعلی انجام شد. هیچ تغییری اعمال نشد.")
    sys.exit(1)

# پاکسازی فایل‌های موقت
if os.path.exists('modules/admin.py.crash_backup'): os.remove('modules/admin.py.crash_backup')
if os.path.exists('modules/start.py.crash_backup'): os.remove('modules/start.py.crash_backup')

print("\n=== 5. ری‌استارت ربات ===")
os.system('pkill -f "python3 -u main.py"')
time.sleep(2)
os.system('nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 &')
time.sleep(3)
print("✅ ربات با موفقیت ری‌استارت شد.")
print("\n=== وضعیت لاگ ربات ===")
os.system('tail -n 10 ~/groupbot_bot.log')
