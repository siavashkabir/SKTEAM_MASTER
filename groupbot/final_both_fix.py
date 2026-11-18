import os, shutil, py_compile, time

print("="*80)
print("🔧 اصلاح نهایی: Guard + Register (یک اسکریپت، خط به خط)")
print("="*80)

ts = time.strftime("%H%M%S")
bak = f'modules/reply.py.bak_both_{ts}'
shutil.copy('modules/reply.py', bak)
print(f"✅ بکاپ: {bak}")

# === خواندن فایل ===
with open('modules/reply.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# === مرحله 1: اصلاح Guard ===
print("\n=== مرحله 1: اصلاح Guard ===")

# پیدا کردن if _old_panel:
if_idx = None
for i, line in enumerate(lines):
    if 'if _old_panel:' in line:
        if_idx = i
        break

if if_idx is None:
    print("❌ if _old_panel پیدا نشد!")
    shutil.copy(bak, 'modules/reply.py')
    exit(1)

indent_if = len(lines[if_idx]) - len(lines[if_idx].lstrip())
print(f"📍 if _old_panel در خط {if_idx+1} (indent={indent_if})")

# پیدا کردن انتهای بلوک
end_idx = None
for j in range(if_idx + 1, len(lines)):
    stripped = lines[j].rstrip()
    if stripped == '':
        continue
    cur_indent = len(lines[j]) - len(lines[j].lstrip())
    if cur_indent <= indent_if:
        end_idx = j
        break

if end_idx is None:
    print("❌ انتهای بلوک پیدا نشد!")
    shutil.copy(bak, 'modules/reply.py')
    exit(1)

print(f"📍 انتهای بلوک در خط {end_idx}")

# ساخت بلوک جدید
i_if = ' ' * indent_if
i_bd = ' ' * (indent_if + 4)

new_guard = [
    f'{i_if}if _old_panel:\n',
    f'{i_bd}print(f"[PANEL GUARD] User {{user.id}} has active panel. Ignoring new request.")\n',
    f'{i_bd}try:\n',
    f'{i_bd}    await msg.delete()\n',
    f'{i_bd}except Exception:\n',
    f'{i_bd}    pass\n',
    f'{i_bd}return\n',
]

lines = lines[:if_idx] + new_guard + lines[end_idx:]
print(f"✅ Guard اصلاح شد ({len(new_guard)} خط).")

# === مرحله 2: اضافه کردن Register ===
print("\n=== مرحله 2: اضافه کردن Register ===")

reset_idx = None
for i, line in enumerate(lines):
    if 'reset_timer(context, sent.chat.id, sent.message_id)' in line:
        reset_idx = i
        break

if reset_idx is None:
    print("❌ reset_timer پیدا نشد!")
    shutil.copy(bak, 'modules/reply.py')
    exit(1)

indent_r = len(lines[reset_idx]) - len(lines[reset_idx].lstrip())
i_r = ' ' * indent_r
i_rb = ' ' * (indent_r + 4)

print(f"📍 reset_timer در خط {reset_idx+1} (indent={indent_r})")

reg_block = [
    f'{i_r}# [PER-USER PANEL GUARD] Register\n',
    f'{i_r}try:\n',
    f'{i_rb}from modules.start import ACTIVE_PANELS\n',
    f'{i_rb}ACTIVE_PANELS[(user.id, chat.id)] = sent.message_id\n',
    f'{i_rb}print(f"[PANEL GUARD] Registered msg={{sent.message_id}}")\n',
    f'{i_r}except Exception as _re:\n',
    f'{i_rb}print("[PANEL GUARD REG ERR] " + str(_re))\n',
]

lines = lines[:reset_idx+1] + reg_block + lines[reset_idx+1:]
print(f"✅ Register اضافه شد ({len(reg_block)} خط).")

# === نوشتن فایل ===
with open('modules/reply.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

# === تأیید نهایی ===
print("\n=== تأیید Guard ===")
with open('modules/reply.py', 'r', encoding='utf-8') as f:
    nl = f.readlines()
for i, line in enumerate(nl):
    if 'PANEL GUARD] User' in line:
        for j in range(max(0, i-1), min(len(nl), i+7)):
            print(f"   {j+1}: {nl[j].rstrip()}")
        break

print("\n=== تأیید Register ===")
for i, line in enumerate(nl):
    if 'PANEL GUARD] Registered' in line:
        for j in range(max(0, i-4), min(len(nl), i+4)):
            print(f"   {j+1}: {nl[j].rstrip()}")
        break

# === کامپایل یک‌بار ===
print("\n=== کامپایل ===")
try:
    py_compile.compile('modules/reply.py', doraise=True)
    print("✅ کامپایل موفق.")
except Exception as e:
    print(f"❌ خطای کامپایل: {e}")
    shutil.copy(bak, 'modules/reply.py')
    print("⚠️ Auto-Rollback انجام شد.")
    exit(1)

# === ری‌استارت ===
print("\n=== ری‌استارت ===")
os.system('pkill -9 -f "main.py"')
time.sleep(3)
os.system('cd ~/groupbot && bash -c "source venv/bin/activate && nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 &"')
time.sleep(8)
os.system('tail -n 6 ~/groupbot_bot.log')

print("\n" + "="*80)
print("✅ تمام شد! حالا تست کن.")
print("="*80)
