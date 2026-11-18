import os, shutil, py_compile, time

print("="*80)
print("🔧 درج مستقیم Guard + Register در owner_panel_trigger.py")
print("="*80)

ts = time.strftime("%H%M%S")
bak = f'modules/owner_panel_trigger.py.bak_dir_{ts}'
shutil.copy('modules/owner_panel_trigger.py', bak)
print(f"✅ بکاپ: {bak}")

with open('modules/owner_panel_trigger.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"📊 تعداد خطوط: {len(lines)}")

# === پیدا کردن خطوط دقیق ===
# STEP 1: if t not in
check_idx = None
for i, line in enumerate(lines):
    if "if t not in" in line and "پنل" in line:
        check_idx = i
        break

# STEP 2: sent = await msg.reply_text
sent_idx = None
for i, line in enumerate(lines):
    if "sent = await msg.reply_text" in line:
        sent_idx = i
        break

# STEP 3: reset_timer - با روش دقیق‌تر
reset_idx = None
for i, line in enumerate(lines):
    if "reset_timer(" in line and "sent." in line:
        reset_idx = i
        break

print(f"\n📍 check_idx (if t not in): {check_idx}")
print(f"📍 sent_idx: {sent_idx}")
print(f"📍 reset_idx: {reset_idx}")

if check_idx is None or sent_idx is None or reset_idx is None:
    print("❌ یکی از خطوط پیدا نشد!")
    if reset_idx is None:
        print("\n📌 خطوطی که 'reset_timer' دارن:")
        for i, line in enumerate(lines):
            if 'reset_timer' in line:
                print(f"   خط {i+1}: {repr(line)}")
    shutil.copy(bak, 'modules/owner_panel_trigger.py')
    exit(1)

print(f"\n📌 خط reset_timer: {repr(lines[reset_idx])}")

# === STEP 4: Guard قبل از check_idx ===
# indent از check_idx
indent_c = len(lines[check_idx]) - len(lines[check_idx].lstrip())
i_c = ' ' * indent_c
i_cb = ' ' * (indent_c + 4)

guard = [
    f'{i_c}# [OWNER PANEL GUARD] چک پنل فعال\n',
    f'{i_c}try:\n',
    f'{i_cb}from modules.start import ACTIVE_PANELS as _AP\n',
    f'{i_cb}_key = (user.id, chat.id)\n',
    f'{i_cb}if _key in _AP:\n',
    f'{i_cb}    print(f"[OWNER PANEL GUARD] User {{user.id}} has active panel. Ignoring.")\n',
    f'{i_cb}    try:\n',
    f'{i_cb}        await msg.delete()\n',
    f'{i_cb}    except Exception:\n',
    f'{i_cb}        pass\n',
    f'{i_cb}    return\n',
    f'{i_c}except Exception as _e:\n',
    f'{i_cb}print("[OWNER PANEL GUARD ERR] " + str(_e))\n',
    f'\n',
]

# درج Guard
lines = lines[:check_idx] + guard + lines[check_idx:]
print(f"\n✅ Guard درج شد ({len(guard)} خط).")

# دوباره پیدا کردن reset_idx (چون خطوط جابجا شد)
reset_idx = None
for i, line in enumerate(lines):
    if "reset_timer(" in line and "sent." in line:
        reset_idx = i
        break

# indent reset_timer
indent_r = len(lines[reset_idx]) - len(lines[reset_idx].lstrip())
i_r = ' ' * indent_r
i_rb = ' ' * (indent_r + 4)

reg = [
    f'\n{i_r}# [OWNER PANEL GUARD] ثبت پنل\n',
    f'{i_r}try:\n',
    f'{i_rb}from modules.start import ACTIVE_PANELS as _AP2\n',
    f'{i_rb}_AP2[(user.id, chat.id)] = sent.message_id\n',
    f'{i_rb}print(f"[OWNER PANEL GUARD] Registered msg={{sent.message_id}}")\n',
    f'{i_r}except Exception as _e2:\n',
    f'{i_rb}print("[OWNER PANEL GUARD REG ERR] " + str(_e2))\n',
]

lines = lines[:reset_idx+1] + reg + lines[reset_idx+1:]
print(f"✅ Register درج شد ({len(reg)} خط).")

with open('modules/owner_panel_trigger.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

# === تأیید ===
print("\n=== تأیید Guard ===")
with open('modules/owner_panel_trigger.py', 'r', encoding='utf-8') as f:
    nl = f.readlines()
for i, line in enumerate(nl):
    if 'OWNER PANEL GUARD] User' in line:
        for j in range(max(0, i-5), min(len(nl), i+5)):
            print(f"   {j+1}: {nl[j].rstrip()}")
        break

print("\n=== تأیید Register ===")
for i, line in enumerate(nl):
    if 'OWNER PANEL GUARD] Registered' in line:
        for j in range(max(0, i-3), min(len(nl), i+4)):
            print(f"   {j+1}: {nl[j].rstrip()}")
        break

# === کامپایل ===
print("\n=== کامپایل ===")
try:
    py_compile.compile('modules/owner_panel_trigger.py', doraise=True)
    print("✅ کامپایل موفق.")
except Exception as e:
    print(f"❌ خطای کامپایل: {e}")
    shutil.copy(bak, 'modules/owner_panel_trigger.py')
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
