import os, shutil, py_compile, time

print("="*80)
print("🔧 برگرداندن از بکاپ و اصلاح صحیح")
print("="*80)

# === 1. برگردوندن از بکاپ ===
latest_bak = 'modules/reply.py.bak_smart_193000'
if os.path.exists(latest_bak):
    shutil.copy(latest_bak, 'modules/reply.py')
    print(f"✅ از بکاپ برگشت: {latest_bak}")
else:
    print("❌ بکاپ پیدا نشد!")
    exit(1)

# === 2. خواندن با خطوط ===
with open('modules/reply.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# === پیدا کردن if _old_panel ===
if_idx = None
for i, line in enumerate(lines):
    if 'if _old_panel:' in line:
        if_idx = i
        break

if if_idx is None:
    print("❌ if _old_panel پیدا نشد!")
    exit(1)

# indent خط if
indent_if = len(lines[if_idx]) - len(lines[if_idx].lstrip())
indent_body = indent_if + 4
print(f"📍 if _old_panel در خط {if_idx+1} (indent={indent_if})")

# === پیدا کردن انتهای بلوک if _old_panel ===
# بلوک بعدی: اولین خطی که indentش <= indent_if و خالی نیست
end_idx = if_idx + 1
for j in range(if_idx + 1, len(lines)):
    stripped = lines[j].rstrip()
    if stripped == '':
        continue
    cur_indent = len(lines[j]) - len(lines[j].lstrip())
    if cur_indent <= indent_if:
        end_idx = j
        break

print(f"📍 انتهای بلوک: خط {end_idx}")
print("\n=== محتوای بلوک قدیمی ===")
for j in range(if_idx, end_idx):
    print(f"   {j+1}: {repr(lines[j])}")

# === ساخت بلوک جدید ===
i_if = ' ' * indent_if
i_bd = ' ' * indent_body

new_block = [
    f'{i_if}if _old_panel:\n',
    f'{i_bd}print(f"[PANEL GUARD] User {{user.id}} has active panel. Ignoring.")\n',
    f'{i_bd}try:\n',
    f'{i_bd}    await msg.delete()\n',
    f'{i_bd}except Exception:\n',
    f'{i_bd}    pass\n',
    f'{i_bd}return\n',
]

lines = lines[:if_idx] + new_block + lines[end_idx:]
print(f"\n✅ بلوک Guard اصلاح شد (با {len(new_block)} خط).")

# === FIX 2: Register after reset_timer ===
reset_idx = None
for i, line in enumerate(lines):
    if 'reset_timer(context, sent.chat.id, sent.message_id)' in line:
        reset_idx = i
        break

if reset_idx is None:
    print("❌ reset_timer پیدا نشد!")
    shutil.copy(latest_bak, 'modules/reply.py')
    exit(1)

# indent خط reset_timer
indent_r = len(lines[reset_idx]) - len(lines[reset_idx].lstrip())
i_r = ' ' * indent_r
i_r_body = ' ' * (indent_r + 4)

print(f"\n📍 reset_timer در خط {reset_idx+1} (indent={indent_r})")

reg_block = [
    f'{i_r}# [PER-USER PANEL GUARD] Register\n',
    f'{i_r}try:\n',
    f'{i_r_body}from modules.start import ACTIVE_PANELS\n',
    f'{i_r_body}ACTIVE_PANELS[(user.id, chat.id)] = sent.message_id\n',
    f'{i_r_body}print(f"[PANEL GUARD] Registered msg={{sent.message_id}}")\n',
    f'{i_r}except Exception as _re:\n',
    f'{i_r_body}print("[PANEL GUARD REG ERR] " + str(_re))\n',
]

lines = lines[:reset_idx+1] + reg_block + lines[reset_idx+1:]
print("✅ Register اضافه شد.")

with open('modules/reply.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

# === نمایش نهایی ===
print("\n=== تأیید Guard ===")
with open('modules/reply.py', 'r', encoding='utf-8') as f:
    new_lines = f.readlines()
for i, line in enumerate(new_lines):
    if 'PANEL GUARD] User' in line:
        for j in range(max(0, i-2), min(len(new_lines), i+8)):
            print(f"   {j+1}: {new_lines[j].rstrip()}")
        break

print("\n=== تأیید Register ===")
for i, line in enumerate(new_lines):
    if 'PANEL GUARD] Registered' in line:
        for j in range(max(0, i-4), min(len(new_lines), i+4)):
            print(f"   {j+1}: {new_lines[j].rstrip()}")
        break

# === کامپایل ===
print("\n=== کامپایل ===")
try:
    py_compile.compile('modules/reply.py', doraise=True)
    print("✅ کامپایل موفق.")
except Exception as e:
    print(f"❌ خطای کامپایل: {e}")
    shutil.copy(latest_bak, 'modules/reply.py')
    exit(1)

# === ری‌استارت ===
print("\n=== ری‌استارت ===")
os.system('pkill -9 -f "main.py"')
time.sleep(3)
os.system('cd ~/groupbot && bash -c "source venv/bin/activate && nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 &"')
time.sleep(8)
os.system('tail -n 6 ~/groupbot_bot.log')

print("\n" + "="*80)
print("✅ تمام! تست کن.")
print("="*80)
