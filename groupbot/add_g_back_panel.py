import os, shutil, py_compile, time, re

print("="*80)
print("🔧 اضافه کردن handler g_back_panel (بازگشت تنظیمات گروه)")
print("="*80)

ts = time.strftime("%H%M%S")
bak = f'modules/start.py.bak_gbp_{ts}'
shutil.copy('modules/start.py', bak)
print(f"✅ بکاپ: {bak}")

with open('modules/start.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# پیدا کردن محل درج: قبل از handler menu_back
anchor_idx = None
for i, line in enumerate(lines):
    if line.rstrip() == '    if action == "menu_back":':
        anchor_idx = i
        break

if anchor_idx is None:
    print("❌ menu_back پیدا نشد!")
    exit(1)

print(f"📍 anchor (menu_back) در خط {anchor_idx+1}")

# indent
indent = ' ' * (len(lines[anchor_idx]) - len(lines[anchor_idx].lstrip()))
ib = indent + '    '

# کد جدید
new_handler = (
    indent + 'if action == "g_back_panel":\n'
    + ib + '# [FIX] بازگشت از تنظیمات گروه\n'
    + ib + 'try:\n'
    + ib + '    from config import OWNER_ID\n'
    + ib + '    from database import is_bot_admin\n'
    + ib + '    _is_owner = (query.from_user.id == OWNER_ID)\n'
    + ib + '    _is_sudo = False\n'
    + ib + '    if not _is_owner:\n'
    + ib + '        try:\n'
    + ib + '            _is_sudo = is_bot_admin(query.from_user.id)\n'
    + ib + '        except Exception:\n'
    + ib + '            pass\n'
    + ib + '    if _is_owner or _is_sudo:\n'
    + ib + '        # سازنده/سودو → منوی اصلی سازنده\n'
    + ib + '        await query.edit_message_text(\n'
    + ib + '            "👑 منوی اصلی - بخش مورد نظر:",\n'
    + ib + '            reply_markup=sudo_panel_menu(query.from_user.id, chat_id)\n'
    + ib + '        )\n'
    + ib + '    else:\n'
    + ib + '        # مالک گروه → منوی مدیریت گروه\n'
    + ib + '        await query.edit_message_text(\n'
    + ib + '            "👑 منوی مدیریت گروه:\\n\\nبرای مدیریت گروه، از دکمه‌های زیر استفاده کنید:",\n'
    + ib + '            reply_markup=group_manage_menu(query.from_user.id)\n'
    + ib + '        )\n'
    + ib + '    reset_timer(context, chat_id, msg_id)\n'
    + ib + 'except Exception as e:\n'
    + ib + '    print("[G_BACK_PANEL ERR] " + str(e))\n'
    + ib + 'return\n'
    + '\n'
)

lines.insert(anchor_idx, new_handler)
print("✅ handler g_back_panel اضافه شد")

with open('modules/start.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

# ============================================================
# اضافه کردن به pattern
# ============================================================
with open('modules/start.py', 'r', encoding='utf-8') as f:
    content = f.read()

if 'g_back_panel' not in re.findall(r'pattern="([^"]*)"', content)[0] if re.findall(r'pattern="([^"]*)"', content) else True:
    m = re.search(r'pattern="([^"]*menu_status[^"]*)"', content)
    if m and 'g_back_panel' not in m.group(1):
        old = m.group(1)
        new = old + '|g_back_panel'
        content = content.replace(f'pattern="{old}"', f'pattern="{new}"', 1)
        with open('modules/start.py', 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ g_back_panel به pattern اضافه شد")

# ============================================================
# کامپایل
# ============================================================
print("\n=== کامپایل ===")
try:
    py_compile.compile('modules/start.py', doraise=True)
    print("✅ کامپایل موفق")
except Exception as e:
    print(f"❌ خطا: {e}")
    shutil.copy(bak, 'modules/start.py')
    exit(1)

# کش + ری‌استارت
for root, dirs, files in os.walk('.'):
    if 'venv' in root:
        continue
    if '__pycache__' in root:
        shutil.rmtree(root, ignore_errors=True)

print("\n=== ری‌استارت ===")
os.system('pkill -9 -f "main.py"')
os.system('pkill -9 -f "connection_monitor.py"')
time.sleep(4)
os.system('cd ~/groupbot && nohup bash bot_watchdog.sh > ~/groupbot_watchdog.log 2>&1 &')
time.sleep(10)
os.system('tail -n 6 ~/groupbot_bot.log')

print("\n" + "="*80)
print("✅ تمام!")
print("="*80)
