import os, time

print("=== 1. کشتن تمام نسخه‌های ربات با 6 الگوی مختلف ===")
patterns = [
    "main.py",
    "python3 -u main.py",
    "bot_watchdog.sh",
    "connection_monitor.py",
    "nohup python3",
    "groupbot/main.py"
]
for p in patterns:
    os.system(f'pkill -9 -f "{p}"')
    print(f"   ✅ الگوی '{p}' کشته شد.")

time.sleep(5)

print("\n=== 2. بررسی اینکه واقعاً همه مرده باشند ===")
result = os.popen('ps aux | grep -E "main.py|watchdog|monitor" | grep -v grep').read()
if result.strip():
    print("⚠️ هنوز این پردازش‌ها زنده هستند:")
    print(result)
    print("در حال تلاش دوم برای کشتن...")
    os.system('killall -9 python3 2>/dev/null')
    time.sleep(3)
else:
    print("✅ همه پردازش‌ها با موفقیت کشته شدند.")

print("\n=== 3. راه‌اندازی فقط یک نسخه از ربات ===")
start_cmd = 'cd ~/groupbot && bash -c "source venv/bin/activate && nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 &"'
os.system(start_cmd)
time.sleep(5)

print("\n=== 4. بررسی نهایی: تعداد پردازش‌های main.py ===")
result = os.popen('ps aux | grep "main.py" | grep -v grep').read()
count = len([l for l in result.split('\n') if 'main.py' in l and 'grep' not in l])
print(f"📊 تعداد پردازش‌های main.py: {count}")
print(result)

if count == 1:
    print("\n✅ عالی! فقط یک نسخه از ربات در حال اجراست.")
elif count > 1:
    print(f"\n⚠️ هنوز {count} نسخه در حال اجراست. لطفاً این خروجی را برای من بفرستید.")
else:
    print("\n❌ ربات بالا نیامد! لاگ را بررسی کنید.")

print("\n=== 5. 10 خط آخر لاگ ربات ===")
os.system('tail -n 10 ~/groupbot_bot.log')
