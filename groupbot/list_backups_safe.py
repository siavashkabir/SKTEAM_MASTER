import os, glob, datetime, time

print("=== 1. توقف کامل ربات و پردازش‌های پایتون ===")
os.system('pkill -9 -f "python3"')
time.sleep(1)
print("✅ ربات و پردازش‌های پایتون متوقف شدند.")

print("\n=== 2. غیرفعال‌سازی موقت کرون‌جاب (اتو استارت) ===")
os.system('crontab -l > ~/crontab_backup.txt 2>/dev/null; crontab -r 2>/dev/null')
print("✅ کرون‌جاب غیرفعال شد. ربات دیگر خودش را ری‌استارت نمی‌کند.")

print("\n=== 3. جستجوی تمام بکاپ‌های admin.py و start.py ===")
backups = []
for root, dirs, files in os.walk(os.path.expanduser('~/groupbot')):
    if 'venv' in root or '.git' in root or '__pycache__' in root: continue
    for f in files:
        if (f.startswith('admin.py.bak') or f.startswith('start.py.bak')):
            path = os.path.join(root, f)
            mtime = os.path.getmtime(path)
            dt = datetime.datetime.fromtimestamp(mtime)
            backups.append((f, dt, path))

backups.sort(key=lambda x: x[1], reverse=True)

if not backups:
    print("❌ هیچ بکاپی برای admin.py یا start.py پیدا نشد!")
else:
    print(f"\n{'='*65}")
    print(f"{'تاریخ و ساعت بکاپ':<25} | {'نام فایل':<35}")
    print(f"{'='*65}")
    for b in backups:
        print(f"🕒 {b[1].strftime('%Y-%m-%d %H:%M:%S')}  |  {b[0]}")
    print(f"{'='*65}")
    print("\n⚠️ لطفاً تاریخ و ساعت دقیق بکاپی که می‌خواهید را برای من بفرستید.")
    print("منتظر می‌مانم تا با هم بهترین بکاپ را انتخاب کنیم و سپس اسکریپت بازگردانی مخصوص آن را می‌فرستم.")
