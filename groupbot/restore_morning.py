import os, glob, time, shutil, sys, py_compile, datetime

print("=== 1. جستجوی بکاپ‌های امروز صبح (بین ساعت 5 تا 7) ===")
today = datetime.date.today()
target_admin = None
target_start = None

def find_backup(pattern):
    best_match = None
    best_diff = float('inf')
    for f in glob.glob(pattern):
        ctime = os.path.getctime(f)
        dt = datetime.datetime.fromtimestamp(ctime)
        if dt.date() == today and 5 <= dt.hour <= 6:
            diff = abs((dt.hour * 60 + dt.minute) - (5 * 60 + 30))
            if diff < best_diff:
                best_diff = diff
                best_match = f
    return best_match

target_admin = find_backup('modules/admin.py.bak_*')
target_start = find_backup('modules/start.py.bak_*')

if not target_admin or not target_start:
    print("❌ بکاپی در بازه ساعت 5 تا 7 صبح امروز پیدا نشد!")
    print("\n📁 لیست تمام بکاپ‌های موجود به ترتیب زمان (از قدیمی به جدید):")
    all_baks = sorted(glob.glob('modules/admin.py.bak_*') + glob.glob('modules/start.py.bak_*'), key=os.path.getctime)
    for b in all_baks:
        ctime = datetime.datetime.fromtimestamp(os.path.getctime(b))
        print(f"   🕒 {ctime.strftime('%Y-%m-%d %H:%M:%S')}  ->  {b}")
    sys.exit(1)

print(f"✅ بکاپ admin.py پیدا شد: {target_admin}")
print(f"✅ بکاپ start.py پیدا شد: {target_start}")

print("\n=== 2. بازگردانی فایل‌ها ===")
try:
    shutil.copy(target_admin, 'modules/admin.py')
    shutil.copy(target_start, 'modules/start.py')
    print("✅ فایل‌ها با موفقیت بازگردانی شدند.")
except Exception as e:
    print(f"❌ خطا در کپی فایل‌ها: {e}")
    sys.exit(1)

print("\n=== 3. کامپایل کد ===")
try:
    py_compile.compile('modules/admin.py', doraise=True)
    py_compile.compile('modules/start.py', doraise=True)
    print("✅ کامپایل با موفقیت انجام شد.")
except Exception as e:
    print(f"❌ خطای کامپایل: {e}")
    sys.exit(1)

print("\n=== 4. ری‌استارت ربات ===")
os.system('pkill -f "python3 -u main.py"')
time.sleep(2)
os.system('nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 &')
time.sleep(3)
print("✅ ربات با موفقیت ری‌استارت شد.")
os.system('tail -n 10 ~/groupbot_bot.log')
