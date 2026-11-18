import os, shutil, py_compile, time, re

print("="*80)
print("🔧 معاف کردن «پنل» از cooldown")
print("="*80)

ts = time.strftime("%H%M%S")
bak = f'modules/global_cooldown.py.bak_exempt_{ts}'
shutil.copy('modules/global_cooldown.py', bak)
print(f"✅ بکاپ: {bak}")

with open('modules/global_cooldown.py', 'r', encoding='utf-8') as f:
    content = f.read()

fixed = False

# === روش ۱: اضافه کردن «پنل» به EXEMPT_COMMANDS ===
m = re.search(r'EXEMPT_COMMANDS\s*=\s*\{([^}]*)\}', content, re.DOTALL)
if m:
    old_set = m.group(1)
    if '"پنل"' not in old_set and "'پنل'" not in old_set:
        # اضافه کردن "پنل" و "panel"
        new_set = old_set.rstrip().rstrip(',') + ', "پنل", "panel"\n'
        content = content.replace(m.group(0), f'EXEMPT_COMMANDS = {{{new_set}}}')
        print("✅ «پنل» و «panel» به EXEMPT_COMMANDS اضافه شدند.")
        fixed = True

# === روش ۲: اضافه کردن چک در normalize_trigger ===
if not fixed and 'def normalize_trigger' in content:
    old_norm = '''def normalize_trigger(text):
    """نرمال‌سازی trigger برای مقایسه"""
    if not text:
        return None'''
    
    new_norm = '''def normalize_trigger(text):
    """نرمال‌سازی trigger برای مقایسه"""
    # [FIXED] پنل همیشه معاف از cooldown
    if text and text.strip().lower() in ("پنل", "panel", "PANEL"):
        return None  # None = معاف
    if not text:
        return None'''
    
    if old_norm in content:
        content = content.replace(old_norm, new_norm)
        print("✅ استثنا در normalize_trigger اضافه شد.")
        fixed = True

# === روش ۳: چک در ابتدای هندلر ===
if not fixed:
    # پیدا کردن تابع cooldown handler
    for i, line in enumerate(content.split('\n')):
        if 'async def' in line and ('cooldown' in line.lower() or 'block' in line.lower()):
            indent = ' ' * (len(line) - len(line.lstrip()) + 4)
            lines = content.split('\n')
            skip_code = [
                f'{indent}# [FIXED] پنل معاف از cooldown',
                f'{indent}try:',
                f'{indent}    _mt = msg.text.strip().lower() if (msg and msg.text) else ""',
                f'{indent}    if _mt in ("پنل", "panel"):',
                f'{indent}        return await handler(update, context)',
                f'{indent}except Exception:',
                f'{indent}    pass',
            ]
            for j, sc in enumerate(skip_code):
                lines.insert(i + 1 + j, sc)
            content = '\n'.join(lines)
            fixed = True
            print(f"✅ استثنا در ابتدای {line.strip()[:40]} اضافه شد.")
            break

if not fixed:
    print("❌ هیچ روشی جواب نداد!")
    shutil.copy(bak, 'modules/global_cooldown.py')
    exit(1)

with open('modules/global_cooldown.py', 'w', encoding='utf-8') as f:
    f.write(content)

# === نمایش نتیجه ===
print("\n=== 30 خط اول فایل بعد از تغییر ===")
with open('modules/global_cooldown.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
for i, line in enumerate(lines[:35]):
    print(f"   {i+1}: {line.rstrip()}")

# === کامپایل ===
try:
    py_compile.compile('modules/global_cooldown.py', doraise=True)
    print("\n✅ کامپایل موفق.")
except Exception as e:
    print(f"\n❌ خطای کامپایل: {e}")
    shutil.copy(bak, 'modules/global_cooldown.py')
    exit(1)

print("\n=== ری‌استارت ربات ===")
os.system('pkill -9 -f "main.py"')
time.sleep(3)
os.system('cd ~/groupbot && bash -c "source venv/bin/activate && nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 &"')
time.sleep(8)
os.system('tail -n 8 ~/groupbot_bot.log')

print("\n" + "="*80)
print("✅ حالا «پنل» همیشه کار می‌کند، حتی در زمان ارسال فاکتور!")
print("="*80)
