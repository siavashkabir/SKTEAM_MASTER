import os, shutil, py_compile, time

print("="*80)
print("🔧 افزودن 3 handler برای جوین اجباری + آمار سودوها + آمار گروه‌ها")
print("="*80)

ts = time.strftime("%H%M%S")
bak = f'modules/start.py.bak_3h_{ts}'
shutil.copy('modules/start.py', bak)
print(f"✅ بکاپ: {bak}")

with open('modules/start.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# ============================================================
# 1. پیدا کردن محل درج (قبل از handler owner_section_menu)
# ============================================================
anchor_idx = None
for i, line in enumerate(lines):
    if 'if action == "owner_section_menu"' in line:
        anchor_idx = i
        break

if anchor_idx is None:
    print("❌ anchor پیدا نشد!")
    exit(1)

print(f"📍 anchor در خط {anchor_idx+1}")

# ============================================================
# 2. ساخت 3 handler
# ============================================================
indent = ' ' * (len(lines[anchor_idx]) - len(lines[anchor_idx].lstrip()))
hib = ' ' * (len(lines[anchor_idx]) - len(lines[anchor_idx].lstrip()) + 4)

new_handlers = (
    f'{indent}if action == "s_fj_menu":\n'
    f'{hib}# [PERM CHECK]\n'
    f'{hib}try:\n'
    f'{hib}    from config import OWNER_ID\n'
    f'{hib}    from database import is_bot_admin\n'
    f'{hib}    _o = (user.id == OWNER_ID)\n'
    f'{hib}    _s = False if _o else is_bot_admin(user.id)\n'
    f'{hib}    if not (_o or _s):\n'
    f'{hib}        await query.answer("\\u26d4 \\u0641\\u0642\\u0637 \\u0633\\u0627\\u0632\\u0646\\u062f\\u0647 \\u0648 \\u0633\\u0648\\u062f\\u0648", show_alert=True)\n'
    f'{hib}        return\n'
    f'{hib}except Exception as _pe:\n'
    f'{hib}    print("[FJ PERM ERR] " + str(_pe))\n'
    f'{hib}try:\n'
    f'{hib}    from database import get_setting\n'
    f'{hib}    _en = get_setting(0, "fj_enabled", "0") == "1"\n'
    f'{hib}    _lnk = get_setting(0, "fj_link", "") or "(\\u062a\\u0646\\u0637\\u06cc\\u0645 \\u0646\\u0634\\u062f\\u0647)"\n'
    f'{hib}    _status = "\\u2705 \\u0641\\u0639\\u0627\\u0644" if _en else "\\u274c \\u063a\\u06cc\\u0631\\u0641\\u0639\\u0627\\u0644"\n'
    f'{hib}    _txt = "\\U0001F512 \\u062c\\u0648\\u06cc\\u0646 \\u0627\\u062c\\u0628\\u0627\\u0631\\u06cc\\n\\n" \\\n'
    f'{hib}           "\\u0648\\u0636\\u0639\\u06cc\\u062a: " + _status + "\\n" \\\n'
    f'{hib}           "\\U0001F517 \\u0644\\u06cc\\u0646\\u06a9: " + _lnk\n'
    f'{hib}    kb = InlineKeyboardMarkup([\n'
    f'{hib}        [InlineKeyboardButton(("\\u274c \\u063a\\u06cc\\u0631\\u0641\\u0639\\u0627\\u0644 \\u06a9\\u0631\\u062f\\u0646" if _en else "\\u2705 \\u0641\\u0639\\u0627\\u0644 \\u06a9\\u0631\\u062f\\u0646"), callback_data=f"fj_toggle_sudo:{uid}")],\n'
    f'{hib}        [InlineKeyboardButton("\\U0001F517 \\u062a\\u0646\\u0637\\u06cc\\u0645 \\u0644\\u06cc\\u0646\\u06a9", callback_data=f"fj_setlink_sudo:{uid}")],\n'
    f'{hib}        [InlineKeyboardButton("\\U0001F519 \\u0628\\u0627\\u0632\\u06af\\u0634\\u062a", callback_data=f"owner_section_back:{uid}:{chat_id}")]\n'
    f'{hib}    ])\n'
    f'{hib}    await query.edit_message_text(_txt, reply_markup=kb)\n'
    f'{hib}except Exception as e:\n'
    f'{hib}    print("[FJ MENU ERR] " + str(e))\n'
    f'{hib}return\n'
    f'\n'
    f'{indent}if action == "fj_toggle_sudo":\n'
    f'{hib}try:\n'
    f'{hib}    from database import get_setting, set_setting\n'
    f'{hib}    _cur = get_setting(0, "fj_enabled", "0")\n'
    f'{hib}    _new = "0" if _cur == "1" else "1"\n'
    f'{hib}    set_setting(0, "fj_enabled", _new)\n'
    f'{hib}    await query.answer("\\u2705 \\u0641\\u0639\\u0627\\u0644 \\u0634\\u062f" if _new == "1" else "\\u274c \\u063a\\u06cc\\u0631\\u0641\\u0639\\u0627\\u0644 \\u0634\\u062f")\n'
    f'{hib}    # refresh\n'
    f'{hib}    from database import get_setting as _gs\n'
    f'{hib}    _en = _gs(0, "fj_enabled", "0") == "1"\n'
    f'{hib}    _lnk = _gs(0, "fj_link", "") or "(\\u062a\\u0646\\u0637\\u06cc\\u0645 \\u0646\\u0634\\u062f\\u0647)"\n'
    f'{hib}    _status = "\\u2705 \\u0641\\u0639\\u0627\\u0644" if _en else "\\u274c \\u063a\\u06cc\\u0631\\u0641\\u0639\\u0627\\u0644"\n'
    f'{hib}    _txt = "\\U0001F512 \\u062c\\u0648\\u06cc\\u0646 \\u0627\\u062c\\u0628\\u0627\\u0631\\u06cc\\n\\n\\u0648\\u0636\\u0639\\u06cc\\u062a: " + _status + "\\n\\U0001F517 \\u0644\\u06cc\\u0646\\u06a9: " + _lnk\n'
    f'{hib}    kb = InlineKeyboardMarkup([\n'
    f'{hib}        [InlineKeyboardButton(("\\u274c \\u063a\\u06cc\\u0631\\u0641\\u0639\\u0627\\u0644" if _en else "\\u2705 \\u0641\\u0639\\u0627\\u0644"), callback_data=f"fj_toggle_sudo:{uid}")],\n'
    f'{hib}        [InlineKeyboardButton("\\U0001F517 \\u062a\\u0646\\u0637\\u06cc\\u0645 \\u0644\\u06cc\\u0646\\u06a9", callback_data=f"fj_setlink_sudo:{uid}")],\n'
    f'{hib}        [InlineKeyboardButton("\\U0001F519 \\u0628\\u0627\\u0632\\u06af\\u0634\\u062a", callback_data=f"owner_section_back:{uid}:{chat_id}")]\n'
    f'{hib}    ])\n'
    f'{hib}    await query.edit_message_text(_txt, reply_markup=kb)\n'
    f'{hib}except Exception as e:\n'
    f'{hib}    print("[FJ TOGGLE ERR] " + str(e))\n'
    f'{hib}return\n'
    f'\n'
    f'{indent}if action == "s_op_sudo_stats":\n'
    f'{hib}# [PERM CHECK]\n'
    f'{hib}try:\n'
    f'{hib}    from config import OWNER_ID\n'
    f'{hib}    from database import is_bot_admin\n'
    f'{hib}    _o = (user.id == OWNER_ID)\n'
    f'{hib}    _s = False if _o else is_bot_admin(user.id)\n'
    f'{hib}    if not (_o or _s):\n'
    f'{hib}        await query.answer("\\u26d4 \\u0641\\u0642\\u0637 \\u0633\\u0627\\u0632\\u0646\\u062f\\u0647 \\u0648 \\u0633\\u0648\\u062f\\u0648", show_alert=True)\n'
    f'{hib}        return\n'
    f'{hib}except Exception:\n'
    f'{hib}    return\n'
    f'{hib}try:\n'
    f'{hib}    import sqlite3\n'
    f'{hib}    from config import DATABASE_PATH\n'
    f'{hib}    conn = sqlite3.connect(DATABASE_PATH)\n'
    f'{hib}    cur = conn.cursor()\n'
    f'{hib}    cur.execute("SELECT user_id FROM bot_admins ORDER BY user_id")\n'
    f'{hib}    admins = [r[0] for r in cur.fetchall()]\n'
    f'{hib}    conn.close()\n'
    f'{hib}    if not admins:\n'
    f'{hib}        await query.edit_message_text("\\U0001F4CA \\u0622\\u0645\\u0627\\u0631 \\u0633\\u0648\\u062f\\u0648\\u0647\\u0627\\n\\n\\u0647\\u06cc\\u0686 \\u0633\\u0648\\u062f\\u0648\\u06cc\\u06cc \\u062a\\u0639\\u0631\\u06cc\\u0641 \\u0646\\u0634\\u062f\\u0647.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("\\U0001F519 \\u0628\\u0627\\u0632\\u06af\\u0634\\u062a", callback_data=f"owner_section_back:{uid}:{chat_id}")]]))\n'
    f'{hib}        return\n'
    f'{hib}    txt = "\\U0001F4CA \\u0622\\u0645\\u0627\\u0631 \\u0633\\u0648\\u062f\\u0648\\u0647\\u0627\\n\\n"\n'
    f'{hib}    txt += "\\U0001F465 \\u062a\\u0639\\u062f\\u0627\\u062f \\u06a9\\u0644: " + str(len(admins)) + "\\n\\n"\n'
    f'{hib}    for aid in admins[:30]:\n'
    f'{hib}        txt += "\\u2022 " + str(aid) + "\\n"\n'
    f'{hib}    if len(admins) > 30:\n'
    f'{hib}        txt += "\\n... \\u0648 " + str(len(admins) - 30) + " \\u0646\\u0641\\u0631 \\u062f\\u06cc\\u06af\\u0631"\n'
    f'{hib}    kb = InlineKeyboardMarkup([[InlineKeyboardButton("\\U0001F519 \\u0628\\u0627\\u0632\\u06af\\u0634\\u062a", callback_data=f"owner_section_back:{uid}:{chat_id}")]])\n'
    f'{hib}    await query.edit_message_text(txt, reply_markup=kb)\n'
    f'{hib}except Exception as e:\n'
    f'{hib}    print("[SUDO STATS ERR] " + str(e))\n'
    f'{hib}return\n'
    f'\n'
    f'{indent}if action == "s_op_group_stats":\n'
    f'{hib}# [PERM CHECK]\n'
    f'{hib}try:\n'
    f'{hib}    from config import OWNER_ID\n'
    f'{hib}    from database import is_bot_admin\n'
    f'{hib}    _o = (user.id == OWNER_ID)\n'
    f'{hib}    _s = False if _o else is_bot_admin(user.id)\n'
    f'{hib}    if not (_o or _s):\n'
    f'{hib}        await query.answer("\\u26d4 \\u0641\\u0642\\u0637 \\u0633\\u0627\\u0632\\u0646\\u062f\\u0647 \\u0648 \\u0633\\u0648\\u062f\\u0648", show_alert=True)\n'
    f'{hib}        return\n'
    f'{hib}except Exception:\n'
    f'{hib}    return\n'
    f'{hib}try:\n'
    f'{hib}    import sqlite3\n'
    f'{hib}    from config import DATABASE_PATH\n'
    f'{hib}    conn = sqlite3.connect(DATABASE_PATH)\n'
    f'{hib}    cur = conn.cursor()\n'
    f'{hib}    cur.execute("SELECT chat_id, title FROM groups ORDER BY chat_id")\n'
    f'{hib}    groups = cur.fetchall()\n'
    f'{hib}    conn.close()\n'
    f'{hib}    if not groups:\n'
    f'{hib}        await query.edit_message_text("\\U0001F4C8 \\u0622\\u0645\\u0627\\u0631 \\u06af\\u0631\\u0648\\u0647\\u200c\\u0647\\u0627\\n\\n\\u0647\\u06cc\\u0686 \\u06af\\u0631\\u0648\\u0647\\u200c\\u0627\\u06cc \\u062b\\u0628\\u062a \\u0646\\u0634\\u062f\\u0647.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("\\U0001F519 \\u0628\\u0627\\u0632\\u06af\\u0634\\u062a", callback_data=f"owner_section_back:{uid}:{chat_id}")]]))\n'
    f'{hib}        return\n'
    f'{hib}    txt = "\\U0001F4C8 \\u0622\\u0645\\u0627\\u0631 \\u06af\\u0631\\u0648\\u0647\\u200c\\u0647\\u0627\\n\\n"\n'
    f'{hib}    txt += "\\U0001F3E0 \\u062a\\u0639\\u062f\\u0627\\u062f \\u06a9\\u0644: " + str(len(groups)) + "\\n\\n"\n'
    f'{hib}    for cid, ttl in groups[:15]:\n'
    f'{hib}        ttl_short = (ttl or str(cid))[:30]\n'
    f'{hib}        txt += "\\u2022 " + ttl_short + "\\n   \\U0001F194 " + str(cid) + "\\n"\n'
    f'{hib}    if len(groups) > 15:\n'
    f'{hib}        txt += "\\n... \\u0648 " + str(len(groups) - 15) + " \\u06af\\u0631\\u0648\\u0647 \\u062f\\u06cc\\u06af\\u0631"\n'
    f'{hib}    kb = InlineKeyboardMarkup([[InlineKeyboardButton("\\U0001F519 \\u0628\\u0627\\u0632\\u06af\\u0634\\u062a", callback_data=f"owner_section_back:{uid}:{chat_id}")]])\n'
    f'{hib}    await query.edit_message_text(txt, reply_markup=kb)\n'
    f'{hib}except Exception as e:\n'
    f'{hib}    print("[GROUP STATS ERR] " + str(e))\n'
    f'{hib}return\n'
    f'\n'
)

# درج هندلرها
lines.insert(anchor_idx, new_handlers)
print(f"✅ 4 handler جدید اضافه شد")

# ============================================================
# 3. اضافه کردن actionها به pattern
# ============================================================
content = ''.join(lines)

# پیدا کردن pattern
import re
m = re.search(r'pattern="([^"]*menu_status[^"]*)"', content)
if m:
    old_pat = m.group(1)
    new_actions = ['s_fj_menu', 's_op_sudo_stats', 's_op_group_stats', 'fj_toggle_sudo', 'fj_setlink_sudo']
    new_pat = old_pat
    for a in new_actions:
        if a not in new_pat:
            new_pat += '|' + a
    content = content.replace(f'pattern="{old_pat}"', f'pattern="{new_pat}"', 1)
    print(f"✅ {len(new_actions)} action به pattern اضافه شد")

with open('modules/start.py', 'w', encoding='utf-8') as f:
    f.write(content)

# ============================================================
# 4. کامپایل
# ============================================================
print("\n=== کامپایل ===")
try:
    py_compile.compile('modules/start.py', doraise=True)
    print("✅ کامپایل موفق")
except Exception as e:
    print(f"❌ خطای کامپایل: {e}")
    shutil.copy(bak, 'modules/start.py')
    print("⚠️ Auto-Rollback")
    exit(1)

# ============================================================
# 5. پاک کردن کش
# ============================================================
print("\n=== پاک کردن __pycache__ ===")
for root, dirs, files in os.walk('.'):
    if 'venv' in root:
        continue
    if '__pycache__' in root:
        shutil.rmtree(root, ignore_errors=True)

# ============================================================
# 6. ری‌استارت
# ============================================================
print("\n=== ری‌استارت ربات ===")
os.system('pkill -9 -f "main.py"')
os.system('pkill -9 -f "connection_monitor.py"')
time.sleep(4)
os.system('cd ~/groupbot && nohup bash bot_watchdog.sh > ~/groupbot_watchdog.log 2>&1 &')
time.sleep(10)
os.system('tail -n 6 ~/groupbot_bot.log')

print("\n" + "="*80)
print("✅ تمام شد! حالا تست کن:")
print("   پنل → 🔧 بخش سازنده")
print("   • 🔒 جوین اجباری (روشن/خاموش + لینک)")
print("   • 📊 آمار سودوها (لیست ادمین‌ها)")
print("   • 📈 آمار گروه‌ها (لیست گروه‌ها)")
print("="*80)
