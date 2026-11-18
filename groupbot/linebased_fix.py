import os, shutil, py_compile, time

print("="*80)
print("🔧 اصلاح خط به خط (بر اساس شماره خط)")
print("="*80)

ts = time.strftime("%H%M%S")
bak = f'modules/reply.py.bak_linefix_{ts}'
shutil.copy('modules/reply.py', bak)
print(f"✅ بکاپ: {bak}")

with open('modules/reply.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# === پیدا کردن خطوط کلیدی ===
guard_start = None
guard_end = None
reset_line = None

for i, line in enumerate(lines):
    if 'if t_norm in' in line and 'پنل' in line:
        guard_start = i
    if '[PER-USER PANEL GUARD]' in line:
        guard_start = i
    if 'if _old_panel:' in line:
        guard_end = i
    if 'reset_timer(context, sent.chat.id, sent.message_id)' in line:
        reset_line = i

print(f"📍 Guard start: خط {guard_start+1 if guard_start is not None else '?'}")
print(f"📍 if _old_panel: خط {guard_end+1 if guard_end is not None else '?'}")
print(f"📍 reset_timer: خط {reset_line+1 if reset_line is not None else '?'}")

if reset_line is None:
    print("❌ reset_timer پیدا نشد!")
    exit(1)

# === نمایش دقیق خطوط Guard ===
print("\n=== نمایش دقیق Guard (با repr) ===")
if guard_start is not None:
    for j in range(guard_start, min(guard_start + 20, len(lines))):
        print(f"   {j+1}: {repr(lines[j])}")

# === 1. پیدا کردن انتهای بلوک if _old_panel (پیدا کردن خط خالی بعد از آن) ===
# روش بهتر: پیدا کردن اولین خطی که indentش کمتر از indent _old_panel هست
if guard_end is not None:
    old_indent = len(lines[guard_end]) - len(lines[guard_end].lstrip())
    
    # پیدا کردن انتهای بلوک if _old_panel
    block_end = guard_end + 1
    for j in range(guard_end + 1, len(lines)):
        stripped = lines[j].lstrip()
        if stripped == '':  # خط خالی
            continue
        cur_indent = len(lines[j]) - len(lines[j].lstrip())
        if cur_indent <= old_indent:
            block_end = j
            break
    
    print(f"\n📍 انتهای بلوک if _old_panel: خط {block_end}")
    print(f"   محتوای خط: {repr(lines[block_end])}")
    
    # جایگزینی بلوک _old_panel
    indent_str = ' ' * old_indent
    new_block = [
        f'{indent_str}if _old_panel:\n',
        f'{indent_str}    # کاربر پنل باز داره → پیام "پنل" رو پاک کن و خارج شو\n',
        f'{indent_str}    print(f"[PANEL GUARD] User {{user.id}} has active panel. Ignoring.")\n',
        f'{indent_str}    try:\n',
        f'{indent_str}        await msg.delete()\n',
        f'{indent_str}    except Exception:\n',
        f'{indent_str}        pass\n',
        f'{indent_str}    return\n',
    ]
    
    lines = lines[:guard_end] + new_block + lines[block_end:]
    print("✅ بلوک Guard اصلاح شد (حالا return می‌ده).")

# === 2. اضافه کردن Register بعد از reset_timer ===
# بعد از تغییر بالا، خط reset_line جابجا شده - پیدا کردن مجدد
for i, line in enumerate(lines):
    if 'reset_timer(context, sent.chat.id, sent.message_id)' in line:
        reset_line = i
        break

if reset_line is not None:
    # تشخیص indent
    reset_indent = len(lines[reset_line]) - len(lines[reset_line].lstrip())
    indent_str = ' ' * reset_indent
    
    register_block = [
        f'{indent_str}# [PER-USER PANEL GUARD] ثبت پنل باز شده\n',
        f'{indent_str}try:\n',
        f'{indent_str}    from modules.start import ACTIVE_PANELS\n',
        f'{indent_str}    ACTIVE_PANELS[(user.id, chat.id)] = sent.message_id\n',
        f'{indent_str}    print(f"[PANEL GUARD] Registered msg={{sent.message_id}} for user={{user.id}}")\n',
        f'{indent_str}except Exception as _re:\n',
        f'{indent_str}    print("[PANEL GUARD REG ERR] " + str(_re))\n',
    ]
    lines = lines[:reset_line+1] + register_block + lines[reset_line+1:]
    print(f"✅ Register بعد از خط {reset_line+1} اضافه شد.")

with open('modules/reply.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

# === 3. نمایش ناحیه نهایی ===
print("\n=== ناحیه نهایی Guard ===")
content = ''.join(lines)
for i, line in enumerate(lines):
    if 'PANEL GUARD] User' in line:
        for j in range(max(0, i-3), min(len(lines), i+10)):
            print(f"   {j+1}: {lines[j].rstrip()}")
        break

print("\n=== ناحیه نهایی Register ===")
for i, line in enumerate(lines):
    if 'PANEL GUARD] Registered' in line:
        for j in range(max(0, i-3), min(len(lines), i+6)):
            print(f"   {j+1}: {lines[j].rstrip()}")
        break

# === 4. کامپایل ===
print("\n=== کامپایل ===")
try:
    py_compile.compile('modules/reply.py', doraise=True)
    print("✅ کامپایل موفق.")
except Exception as e:
    print(f"❌ خطای کامپایل: {e}")
    shutil.copy(bak, 'modules/reply.py')
    exit(1)

# === 5. ری‌استارت ===
print("\n=== ری‌استارت ربات ===")
os.system('pkill -9 -f "main.py"')
time.sleep(3)
os.system('cd ~/groupbot && bash -c "source venv/bin/activate && nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 &"')
time.sleep(8)
os.system('tail -n 8 ~/groupbot_bot.log')

print("\n" + "="*80)
print("✅ حالا باید درست کار کند!")
print("="*80)
