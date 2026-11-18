import os, shutil, py_compile, time, re

print("="*80)
print("🔧 اصلاح انعطاف‌پذیر (تشخیص خودکار)")
print("="*80)

ts = time.strftime("%H%M%S")
bak = f'modules/reply.py.bak_smart_{ts}'
shutil.copy('modules/reply.py', bak)
print(f"✅ بکاپ: {bak}")

with open('modules/reply.py', 'r', encoding='utf-8') as f:
    content = f.read()

# === FIX 1: Guard ===
print("\n=== FIX 1: Guard ===")
# پیدا کردن بلوک if _old_panel: با regex انعطاف‌پذیر
guard_pattern = r'if _old_panel:\s*\n(?:\s+print\([^\n]*\n)?(?:\s+try:\s*\n\s+await context\.bot\.delete_message[^\n]*\n\s+except Exception:\s*\n\s+pass\s*\n)?(?:\s+try:\s*\n\s+del ACTIVE_PANELS\[_key\]\s*\n\s+except Exception:\s*\n\s+pass)'

new_guard = '''if _old_panel:
            print(f"[PANEL GUARD] User {user.id} has active panel. Ignoring new request.")
            try:
                await msg.delete()
            except Exception:
                pass
            return'''

if re.search(guard_pattern, content, re.DOTALL):
    content = re.sub(guard_pattern, new_guard, content, count=1, flags=re.DOTALL)
    print("✅ Guard اصلاح شد.")
else:
    print("⚠️ الگوی Guard پیدا نشد. تلاش برای پیدا کردن if _old_panel:")
    idx = content.find('if _old_panel:')
    if idx != -1:
        print(f"   if _old_panel: در موقعیت {idx}")
        # پیدا کردن پایان بلوک
        # پایان = اولین خط با indent کمتر از "        if _old_panel:"
        snippet = content[idx:idx+500]
        print("   نمایش 30 خط بعدی از این نقطه:")
        for i, l in enumerate(snippet.split('\n')[:30]):
            print(f"      {i+1}: {repr(l)}")

# === FIX 2: Register after reset_timer ===
print("\n=== FIX 2: Register ===")
# الگوی انعطاف‌پذیر
reset_pattern = r'(\n(\s+)reset_timer\(context,\s*sent\.chat\.id,\s*sent\.message_id\))'

m = re.search(reset_pattern, content)
if m:
    full_match = m.group(1)
    indent = m.group(2)
    print(f"✅ reset_timer پیدا شد (indent={len(indent)} chars)")
    
    new_block = full_match + f'''
{indent}# [PER-USER PANEL GUARD] Register
{indent}try:
{indent}    from modules.start import ACTIVE_PANELS
{indent}    ACTIVE_PANELS[(user.id, chat.id)] = sent.message_id
{indent}    print(f"[PANEL GUARD] Registered msg={{sent.message_id}} for user={{user.id}}")
{indent}except Exception as _re:
{indent}    print("[PANEL GUARD ERR] " + str(_re))'''
    
    content = content.replace(full_match, new_block, 1)
    print("✅ Register اضافه شد.")
else:
    print("❌ reset_timer پیدا نشد!")
    # جستجوی مستقیم
    for kw in ['reset_timer(context', 'reset_timer(', 'sent.message_id']:
        if kw in content:
            print(f"   '{kw}' پیدا شد")
        else:
            print(f"   '{kw}' پیدا نشد")

with open('modules/reply.py', 'w', encoding='utf-8') as f:
    f.write(content)

# === نمایش نتیجه نهایی ===
print("\n=== تأیید نهایی ===")
with open('modules/reply.py', 'r', encoding='utf-8') as f:
    new_lines = f.readlines()

print("\n[1] Guard نهایی:")
for i, line in enumerate(new_lines):
    if 'PANEL GUARD] User' in line:
        for j in range(max(0, i-2), min(len(new_lines), i+8)):
            print(f"   {j+1}: {new_lines[j].rstrip()}")
        break

print("\n[2] Register نهایی:")
for i, line in enumerate(new_lines):
    if 'PANEL GUARD] Registered' in line:
        for j in range(max(0, i-3), min(len(new_lines), i+5)):
            print(f"   {j+1}: {new_lines[j].rstrip()}")
        break

# === کامپایل ===
print("\n=== کامپایل ===")
try:
    py_compile.compile('modules/reply.py', doraise=True)
    print("✅ کامپایل موفق.")
except Exception as e:
    print(f"❌ خطای کامپایل: {e}")
    shutil.copy(bak, 'modules/reply.py')
    exit(1)

# === ری‌استارت ===
print("\n=== ری‌استارت ===")
os.system('pkill -9 -f "main.py"')
time.sleep(3)
os.system('cd ~/groupbot && bash -c "source venv/bin/activate && nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 &"')
time.sleep(8)
os.system('tail -n 6 ~/groupbot_bot.log')

print("\n" + "="*80)
print("✅ تمام!")
print("="*80)
