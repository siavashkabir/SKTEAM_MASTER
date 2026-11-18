import os, shutil, py_compile, time

print("="*80)
print("🔧 بازگردانی کالبک‌های تمدید به حالت قبل (greq_)")
print("="*80)

ts = time.strftime("%H%M%S")
bak = f'modules/start.py.bak_revert_{ts}'
shutil.copy('modules/start.py', bak)
print(f"✅ بکاپ: {bak}")

with open('modules/start.py', 'r', encoding='utf-8') as f:
    content = f.read()

# بازگردانی به greq_
revert_list = [
    ('callback_data="osub_manual_manager:"', 'callback_data="greq_manager:"'),
    ('callback_data="osub_manual_nsfw:"', 'callback_data="greq_nsfw:"'),
    ('callback_data="osub_manual_vcall:"', 'callback_data="greq_vcall:"'),
    ('callback_data="osub_manual_music:"', 'callback_data="greq_music:"'),
]

for new, old in revert_list:
    if new in content:
        count = content.count(new)
        content = content.replace(new, old)
        print(f"✅ '{new}' → '{old}' ({count} مورد)")

with open('modules/start.py', 'w', encoding='utf-8') as f:
    f.write(content)

try:
    py_compile.compile('modules/start.py', doraise=True)
    print("✅ کامپایل موفق.")
except Exception as e:
    print(f"❌ خطای کامپایل: {e}")
    shutil.copy(bak, 'modules/start.py')
    exit(1)

print("\n=== ری‌استارت ربات ===")
os.system('pkill -9 -f "main.py"')
time.sleep(3)
os.system('cd ~/groupbot && bash -c "source venv/bin/activate && nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 &"')
time.sleep(5)
print("✅ ربات ری‌استارت شد.")
