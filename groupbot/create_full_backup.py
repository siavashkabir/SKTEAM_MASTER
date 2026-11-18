import os, shutil, time, subprocess
from datetime import datetime

print("="*80)
print("💾 ایجاد بکاپ کامل از پروژه")
print("="*80)

# === تنظیمات ===
ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
backup_name = f"groupbot_full_backup_{ts}"
backup_dir = os.path.expanduser(f"~/backups/{backup_name}")
os.makedirs(os.path.expanduser("~/backups"), exist_ok=True)

print(f"📁 محل بکاپ: {backup_dir}")

# === 1. ساخت پوشه بکاپ ===
if os.path.exists(backup_dir):
    print(f"⚠️ پوشه {backup_dir} از قبل وجود دارد!")
    exit(1)

os.makedirs(backup_dir)
print(f"✅ پوشه ساخته شد.")

# === 2. کپی فایل‌های اصلی (بدون venv, __pycache__, .bak) ===
print("\n=== 1. کپی فایل‌های کد ===")

IGNORE_PATTERNS = shutil.ignore_patterns(
    'venv', '__pycache__', '*.pyc', '*.pyo',
    '*.bak_*', '*.broken', '*.temp', '*.crash*',
    'node_modules', '.git'
)

src = os.path.expanduser("~/groupbot")
dst = os.path.join(backup_dir, "groupbot")

try:
    shutil.copytree(src, dst, ignore=IGNORE_PATTERNS, symlinks=False)
    print(f"✅ پروژه کپی شد.")
    
    # شمارش فایل‌ها
    file_count = sum(len(files) for _, _, files in os.walk(dst))
    print(f"📊 تعداد فایل‌ها: {file_count}")
except Exception as e:
    print(f"❌ خطا: {e}")
    exit(1)

# === 3. کپی دیتابیس‌ها ===
print("\n=== 2. کپی دیتابیس‌ها ===")
db_files = [
    os.path.expanduser("~/groupbot/data/groupbot.db"),
    os.path.expanduser("~/groupbot/database.db"),
]

dbs_dst = os.path.join(backup_dir, "databases")
os.makedirs(dbs_dst, exist_ok=True)

for db in db_files:
    if os.path.exists(db):
        fname = os.path.basename(db)
        shutil.copy(db, os.path.join(dbs_dst, fname))
        size = os.path.getsize(db) / 1024
        print(f"   ✅ {fname} ({size:.1f} KB)")
    else:
        print(f"   ⚠️ {db} پیدا نشد.")

# === 4. کپی crontab ===
print("\n=== 3. بکاپ crontab ===")
try:
    result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
    if result.stdout.strip():
        with open(os.path.join(backup_dir, "crontab.txt"), 'w') as f:
            f.write(result.stdout)
        print(f"✅ crontab ذخیره شد.")
    else:
        print(f"⚠️ crontab خالی است.")
except Exception as e:
    print(f"⚠️ خطا در بکاپ crontab: {e}")

# === 5. کپی .bashrc ===
print("\n=== 4. بکاپ .bashrc ===")
bashrc = os.path.expanduser("~/.bashrc")
if os.path.exists(bashrc):
    shutil.copy(bashrc, os.path.join(backup_dir, ".bashrc"))
    print(f"✅ .bashrc ذخیره شد.")

# === 6. کپی فایل‌های اسکریپت راه‌اندازی ===
print("\n=== 5. کپی اسکریپت‌های اجرایی ===")
scripts = ['run_bot.sh', 'bot_watchdog.sh', 'start.sh', 'connection_monitor.py', 'main.py', 'config.py', 'database.py']
for s in scripts:
    src_path = os.path.expanduser(f"~/groupbot/{s}")
    if os.path.exists(src_path):
        shutil.copy(src_path, os.path.join(backup_dir, s))
        print(f"   ✅ {s}")

# === 7. ساخت فایل خلاصه ===
print("\n=== 6. ساخت فایل اطلاعات بکاپ ===")
info = f"""📦 بکاپ کامل پروژه GroupBot
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 تاریخ: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
📁 محل: {backup_dir}

📊 محتویات:
   ├── groupbot/          ← کل پروژه (کدها)
   ├── databases/         ← دیتابیس‌ها
   │   ├── groupbot.db    ← دیتابیس اصلی
   │   └── database.db    ← دیتابیس قدیمی
   ├── crontab.txt        ← کرون‌جاب فعلی
   ├── .bashrc            ← تنظیمات شل
   ├── run_bot.sh         ← اسکریپت اجرا
   ├── bot_watchdog.sh    ← نگهبان
   ├── main.py            ← فایل اصلی
   ├── config.py          ← تنظیمات
   └── database.py        ← توابع دیتابیس

🔧 قابلیت‌های فعال در این نسخه:
   ✅ سیستم تایمر پنل (30s/1m/3m/5m)
   ✅ هشدار بسته شدن پنل
   ✅ Guard پنل تک‌کاربر (per-user)
   ✅ سیستم تمدید اشتراک با فاکتور
   ✅ Cooldown کوتاه برای «پنل» (3s)
   ✅ سیستم Auto-Start و Watchdog
   ✅ حذف خودکار پیام‌ها (10s)
   ✅ سیستم اشتراک‌ها (مدیر/NSFW/ویس‌کال/موزیک)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔄 برای بازگردانی از این بکاپ:
   1. ربات را متوقف کن: pkill -9 -f "main.py"
   2. کدها را برگردان: cp -r {backup_dir}/groupbot/* ~/groupbot/
   3. دیتابیس را برگردان: cp {backup_dir}/databases/*.db ~/groupbot/data/
   4. کامپایل: python3 -m py_compile ~/groupbot/modules/start.py
   5. ربات را روشن کن
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
with open(os.path.join(backup_dir, "BACKUP_INFO.txt"), 'w', encoding='utf-8') as f:
    f.write(info)
print("✅ فایل BACKUP_INFO.txt ساخته شد.")

# === 8. ساخت آرشیو tar.gz ===
print("\n=== 7. ساخت آرشیو فشرده ===")
archive_path = os.path.expanduser(f"~/backups/{backup_name}.tar.gz")
os.system(f'cd ~/backups && tar -czf "{archive_path}" "{backup_name}" 2>&1')
if os.path.exists(archive_path):
    size = os.path.getsize(archive_path) / (1024 * 1024)
    print(f"✅ آرشیو ساخته شد: {archive_path}")
    print(f"📊 حجم: {size:.2f} MB")
else:
    print("⚠️ خطا در ساخت آرشیو")

# === 9. پاک کردن پوشه temp (اختیاری) ===
# shutil.rmtree(backup_dir)  # اگر می‌خواهید فقط tar.gz بماند، این را از کامنت خارج کنید

# === 10. نمایش نهایی ===
print("\n" + "="*80)
print("✅ بکاپ کامل انجام شد!")
print("="*80)
print(f"\n📁 پوشه بکاپ: {backup_dir}")
print(f"📦 آرشیو فشرده: {archive_path}")
print(f"\n📌 محتویات:")
os.system(f'ls -lh {os.path.expanduser("~/backups/")} | tail -5')
print(f"\n📌 فایل‌های بکاپ شده:")
os.system(f'find {backup_dir} -type f | head -20')
