import os, shutil, py_compile, time

print("="*80)
print("🔧 افزودن تنظیمات گزارش به منوی تنظیمات گروه")
print("="*80)

# ==== 1. بررسی سلامت فایل فعلی ====
print("\n=== 1. بررسی سلامت فایل ===")
try:
    py_compile.compile('modules/owner_set_group.py', doraise=True)
    print("✅ فایل فعلی سالم است.")
except Exception as e:
    print(f"❌ فایل خراب است: {e}")
    print("⚠️ ابتدا باید از بکاپ برگردانی.")
    exit(1)

# ==== 2. بکاپ ====
ts = time.strftime("%H%M%S")
bak = f'modules/owner_set_group.py.bak_repset_{ts}'
shutil.copy('modules/owner_set_group.py', bak)
print(f"✅ بکاپ: {bak}")

# ==== 3. خواندن خطوط ====
with open('modules/owner_set_group.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# ==== 4. چک اینکه از قبل هست ====
if any('owner_rep_dl' in l for l in lines):
    print("⚠️ از قبل اضافه شده! هیچ تغییری لازم نیست.")
    exit(0)

# ==== 5. پیدا کردن دکمه بازگشت ====
btn_idx = None
for i, line in enumerate(lines):
    if 'timer_back:' in line and 'InlineKeyboardButton' in line:
        btn_idx = i
        break

if btn_idx is None:
    print("❌ دکمه بازگشت timer_back پیدا نشد!")
    exit(1)

print(f"📍 دکمه بازگشت در خط {btn_idx+1}")

# ==== 6. پیدا کردن هندلر timer_back ====
hnd_idx = None
for i, line in enumerate(lines):
    if 'if action == "timer_back"' in line:
        hnd_idx = i
        break

if hnd_idx is None:
    print("❌ هندلر timer_back پیدا نشد!")
    exit(1)

print(f"📍 هندلر timer_back در خط {hnd_idx+1}")

# ==== 7. اضافه کردن دکمه‌ها ====
indent_btn = len(lines[btn_idx]) - len(lines[btn_idx].lstrip())
ib = ' ' * indent_btn

new_btns = [
    f'{ib}[InlineKeyboardButton(f"📊 سهمیه روزانه گزارش: {{get_report_settings(chat_id)[0]}}", callback_data=f"owner_rep_dl:{{uid}}:{{chat_id}}")],\n',
    f'{ib}[InlineKeyboardButton(f"⏱ فاصله بین گزارش‌ها: {{fmt_rep_cd(get_report_settings(chat_id)[1])}}", callback_data=f"owner_rep_cd:{{uid}}:{{chat_id}}")],\n',
]

lines = lines[:btn_idx] + new_btns + lines[btn_idx:]
print(f"✅ ۲ دکمه اضافه شد.")

# دوباره پیدا کردن hnd_idx (چون خطوط جابجا شد)
for i, line in enumerate(lines):
    if 'if action == "timer_back"' in line:
        hnd_idx = i
        break

# ==== 8. اضافه کردن هندلرها ====
indent_hnd = len(lines[hnd_idx]) - len(lines[hnd_idx].lstrip())
hi = ' ' * indent_hnd
hib = ' ' * (indent_hnd + 4)

handlers_block = (
    f'{hi}if action == "owner_rep_dl":\n'
    f'{hib}try:\n'
    f'{hib}    cur = get_report_settings(chat_id)[0]\n'
    f'{hib}    try:\n'
    f'{hib}        i = REP_LIMIT_OPTS.index(cur)\n'
    f'{hib}    except ValueError:\n'
    f'{hib}        i = 0\n'
    f'{hib}    new = REP_LIMIT_OPTS[(i + 1) % len(REP_LIMIT_OPTS)]\n'
    f'{hib}    set_report_daily_limit(chat_id, new)\n'
    f'{hib}    try:\n'
    f'{hib}        await _safe_edit(query, "⚙️ تنظیمات این گروه", reply_markup=_build_menu(uid, chat_id))\n'
    f'{hib}    except Exception:\n'
    f'{hib}        pass\n'
    f'{hib}    await query.answer(f"✅ سهمیه: {{new}} گزارش")\n'
    f'{hib}except Exception as e:\n'
    f'{hib}    print("[REP_DL ERR] " + str(e))\n'
    f'{hib}return\n'
    f'\n'
    f'{hi}if action == "owner_rep_cd":\n'
    f'{hib}try:\n'
    f'{hib}    cur = get_report_settings(chat_id)[1]\n'
    f'{hib}    try:\n'
    f'{hib}        i = REP_CD_OPTS.index(cur)\n'
    f'{hib}    except ValueError:\n'
    f'{hib}        i = 0\n'
    f'{hib}    new = REP_CD_OPTS[(i + 1) % len(REP_CD_OPTS)]\n'
    f'{hib}    set_report_cooldown(chat_id, new)\n'
    f'{hib}    try:\n'
    f'{hib}        await _safe_edit(query, "⚙️ تنظیمات این گروه", reply_markup=_build_menu(uid, chat_id))\n'
    f'{hib}    except Exception:\n'
    f'{hib}        pass\n'
    f'{hib}    await query.answer(f"✅ فاصله: {{fmt_rep_cd(new)}}")\n'
    f'{hib}except Exception as e:\n'
    f'{hib}    print("[REP_CD ERR] " + str(e))\n'
    f'{hib}return\n'
    f'\n'
)

lines = lines[:hnd_idx] + [handlers_block] + lines[hnd_idx:]
print(f"✅ ۲ هندلر اضافه شد.")

# ==== 9. اضافه کردن ایمپورت ====
content = ''.join(lines)
first_from_db = None
for i, line in enumerate(lines):
    if line.startswith('from database import'):
        first_from_db = i
        break

if first_from_db is not None:
    # چک که از قبل ایمپورت نشده
    if 'get_report_settings' not in lines[first_from_db]:
        # ادامه خط را پیدا کن (ممکنه چند خطی باشه)
        end_of_import = first_from_db
        for j in range(first_from_db, min(first_from_db + 20, len(lines))):
            if ')' in lines[j] or (not lines[j].strip().endswith(',') and not lines[j].strip().endswith('import') and j > first_from_db):
                end_of_import = j
                break
            if lines[j].rstrip().endswith(')'):
                end_of_import = j
                break
        
        # اضافه کردن به آخر import
        # چک کن که خط قبل از ) با کاما تموم میشه یا نه
        prev_line = lines[end_of_import - 1].rstrip()
        if not prev_line.endswith(','):
            lines[end_of_import - 1] = lines[end_of_import - 1].rstrip() + ',\n'
        
        # پیدا کردن خط )
        for j in range(end_of_import, first_from_db - 1, -1):
            if ')' in lines[j]:
                # درج خطوط جدید قبل از )
                indent_imp = ' ' * (len(lines[first_from_db]) - len(lines[first_from_db].lstrip()) + 4)
                new_imp_lines = [
                    f'{indent_imp}get_report_settings, set_report_daily_limit, set_report_cooldown,\n',
                    f'{indent_imp}fmt_rep_cd, REP_LIMIT_OPTS, REP_CD_OPTS,\n',
                ]
                lines = lines[:j] + new_imp_lines + lines[j:]
                print("✅ ایمپورت اضافه شد.")
                break
    else:
        print("⚠️ ایمپورت از قبل هست.")

# ==== 10. نوشتن ====
with open('modules/owner_set_group.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

# ==== 11. کامپایل ====
print("\n=== کامپایل ===")
try:
    py_compile.compile('modules/owner_set_group.py', doraise=True)
    print("✅ کامپایل موفق.")
except Exception as e:
    print(f"❌ خطای کامپایل: {e}")
    shutil.copy(bak, 'modules/owner_set_group.py')
    print("⚠️ Auto-Rollback انجام شد.")
    exit(1)

# ==== 12. ری‌استارت ====
print("\n=== ری‌استارت ربات ===")
os.system('pkill -9 -f "main.py"')
time.sleep(3)
os.system('cd ~/groupbot && bash -c "source venv/bin/activate && nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 &"')
time.sleep(8)
os.system('tail -n 8 ~/groupbot_bot.log')

print("\n" + "="*80)
print("✅ کامل شد!")
print("="*80)
print("""
📌 محل: منوی مالک گروه → تنظیمات این گروه
📌 دکمه‌های جدید:
   • 📊 سهمیه روزانه گزارش: 3
   • ⏱ فاصله بین گزارش‌ها: 5 دقیقه
   
📌 با هر کلیک، مقدار چرخش می‌کند.
📌 سازنده هم وقتی وارد پنل این گروه بشه، می‌بینه.
""")
