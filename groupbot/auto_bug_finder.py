import os, re, glob

print("="*80)
print("🤖 ربات پیدا کردن باگ - تحلیل خودکار همه منوها")
print("="*80)

# ============================================================
# 1. بارگذاری همه فایل‌ها
# ============================================================
files = {}
for f in ['modules/start.py'] + glob.glob('modules/*.py'):
    if '.bak' in f or 'crash' in f:
        continue
    if not os.path.exists(f):
        continue
    try:
        with open(f, 'r', encoding='utf-8') as file:
            files[f] = file.readlines()
    except:
        pass

print(f"\n📊 {len(files)} فایل بارگذاری شد")

# ============================================================
# 2. پیدا کردن توابع منو
# ============================================================
MENU_FUNCS = {}
for fname, lines in files.items():
    for i, line in enumerate(lines):
        m = re.match(r'^def\s+(\w+)\s*\(', line)
        if not m: continue
        fname_f = m.group(1)
        # فقط منوها
        if not any(k in fname_f.lower() for k in ['menu', 'panel', 'keyboard', '_kb']):
            continue
        end = len(lines)
        for j in range(i+1, len(lines)):
            if lines[j].startswith('def ') or lines[j].startswith('async def '):
                end = j
                break
        MENU_FUNCS[fname_f] = (fname, i+1, end)

# ============================================================
# 3. استخراج دکمه‌ها + هندلرها
# ============================================================
def get_buttons(lines, start, end):
    btns = []
    for k in range(start, min(end, len(lines))):
        line = lines[k]
        if 'InlineKeyboardButton' not in line: continue
        m1 = re.search(r'InlineKeyboardButton\(["\']([^"\']+)["\']', line)
        label = m1.group(1)[:40] if m1 else '?'
        cb = None
        m2 = re.search(r'callback_data=["\']([^"\']+)["\']', line)
        if m2: cb = m2.group(1)
        else:
            m3 = re.search(r'callback_data=f["\']([^"\']+)["\']', line)
            if m3: cb = m3.group(1)
        if cb:
            cb_norm = cb.split(':')[0] if ':' in cb else cb
            btns.append((label, cb_norm, k+1))
    return btns

HANDLERS = {}
for fname, lines in files.items():
    for i, line in enumerate(lines):
        m = re.match(r'\s*if action == ["\']([^"\']+)["\']', line)
        if not m: continue
        act = m.group(1)
        end = len(lines)
        for j in range(i+1, len(lines)):
            if re.match(r'\s*if action', lines[j]) or lines[j].startswith('def ') or lines[j].startswith('async def '):
                end = j
                break
        # reply_markup
        dest = None
        for k in range(i, end):
            m2 = re.search(r'reply_markup=(\w+)\(', lines[k])
            if m2:
                dest = m2.group(1)
                break
        HANDLERS[act] = (fname, i+1, dest)

# ============================================================
# 4. ساخت گراف: کدوم منو، کالبک‌هاش کجا می‌رن
# ============================================================
# menu_opened_via = {menu_name: [(via_callback, in_menu)]}
opened_map = {}  # dest_menu -> [(cb, parent_menu)]
for menu_name, (fname, start, end) in MENU_FUNCS.items():
    lines = files[fname]
    btns = get_buttons(lines, start-1, end)
    for label, cb, ln in btns:
        if cb in HANDLERS:
            _, _, dest = HANDLERS[cb]
            if dest and dest in MENU_FUNCS:
                if dest not in opened_map:
                    opened_map[dest] = []
                opened_map[dest].append((cb, label, menu_name))

# ============================================================
# 5. لیست منوهای اصلی (بدون نیاز به بازگشت)
# ============================================================
MAIN_MENUS = {'sudo_panel_menu', 'group_owner_panel_menu', 'owner_manage_menu',
              'group_manage_menu', 'group_panel_menu', 'start_cmd', 'main_menu_kb',
              'build_sysinfo_keyboard'}

# ============================================================
# 6. تحلیل هر منو
# ============================================================
print("\n" + "="*80)
print("🚨 باگ‌های پیدا شده به صورت خودکار")
print("="*80)

bugs = []

for menu_name, (fname, start, end) in MENU_FUNCS.items():
    lines = files[fname]
    btns = get_buttons(lines, start-1, end)
    
    back_btns = [(l, cb, ln) for l, cb, ln in btns if 'بازگشت' in l or 'back' in cb.lower()]
    close_btns = [(l, cb, ln) for l, cb, ln in btns if 'بستن' in l or 'close' in cb.lower()]
    
    # باگ ۱: منوهای غیر اصلی بدون بازگشت
    if not back_btns and menu_name not in MAIN_MENUS and len(btns) > 0:
        bugs.append(('NO_BACK', menu_name, fname, start, f'منو بازگشت نداره ({len(btns)} دکمه)'))
    
    # باگ ۲: بررسی مقصد بازگشت
    for lbl, cb, ln in back_btns:
        if cb in HANDLERS:
            _, _, dest = HANDLERS[cb]
            if dest:
                # باید به یکی از والدین بره
                parents = [p for c, l, p in opened_map.get(menu_name, [])]
                if parents and dest not in parents and dest != menu_name:
                    bugs.append(('WRONG_BACK', menu_name, fname, ln,
                                f'بازگشت به {dest} می‌ره، ولی والدش {parents} هست'))
                if dest == menu_name:
                    bugs.append(('LOOP_BACK', menu_name, fname, ln, f'بازگشت به خودش (loop!)'))
        else:
            bugs.append(('NO_BACK_HANDLER', menu_name, fname, ln, f'بازگشت {cb} هندلر نداره'))
    
    # باگ ۳: منوهای غیر اصلی بدون بستن (اگه بازگشت دارن، بستن لازم نیست)
    # اینو skip می‌کنیم چون طراحی جدید گفته بستن نباشه

# ============================================================
# 7. کالبک‌های بدون handler
# ============================================================
print("\n" + "="*80)
print("🔍 کالبک‌های بدون handler (خطر بن‌بست)")
print("="*80)

# جمع‌آوری همه کالبک‌های استفاده شده
all_cbs = set()
for fname, lines in files.items():
    for line in lines:
        m = re.search(r'callback_data=["\']([^"\']+)["\']', line)
        if m: all_cbs.add(m.group(1).split(':')[0])
        m = re.search(r'callback_data=f["\']([^"\']+)["\']', line)
        if m: all_cbs.add(m.group(1).split(':')[0])

# چک patternها
all_pattern_parts = set()
for fname, lines in files.items():
    for line in lines:
        if 'add_handler' in line and 'pattern=' in line:
            m = re.search(r'pattern=["\']([^"\']+)["\']', line)
            if m:
                parts = m.group(1).replace('^(', '').replace(')$', '').split('|')
                all_pattern_parts.update(parts)

no_handler_cbs = []
no_pattern_cbs = []
for cb in sorted(all_cbs):
    if cb not in HANDLERS and not any(cb.startswith(s) for s in HANDLERS if s.endswith('_')):
        no_handler_cbs.append(cb)
    if cb not in all_pattern_parts and not any(cb.startswith(s) for s in all_pattern_parts if s.endswith('_')):
        no_pattern_cbs.append(cb)

print(f"\n❌ {len(no_handler_cbs)} کالبک بدون handler:")
for cb in no_handler_cbs[:30]:
    print(f"   • {cb}")

print(f"\n⚠️ {len(no_pattern_cbs)} کالبک بدون pattern:")
for cb in no_pattern_cbs[:30]:
    print(f"   • {cb}")

# ============================================================
# 8. هندلرهای بدون کالبک (کد مرده)
# ============================================================
print("\n" + "="*80)
print("💀 هندلرهای مرده (کالبکی ندارن)")
print("="*80)

dead_handlers = []
for act in HANDLERS:
    if act not in all_cbs:
        dead_handlers.append(act)

print(f"\n💀 {len(dead_handlers)} هندلر مرده:")
for h in dead_handlers[:40]:
    fname, ln, _ = HANDLERS[h]
    print(f"   • {h} [{fname}:{ln}]")

# ============================================================
# 9. خلاصه
# ============================================================
print("\n" + "="*80)
print("📊 خلاصه نهایی")
print("="*80)
print(f"""
🔴 باگ‌های بازگشت/بستن: {len(bugs)}
❌ کالبک‌های بدون handler: {len(no_handler_cbs)}
⚠️ کالبک‌های بدون pattern: {len(no_pattern_cbs)}
💀 هندلرهای مرده: {len(dead_handlers)}
""")

if bugs:
    print("\n🚨 لیست باگ‌ها:")
    for bt, menu, fname, ln, desc in bugs:
        print(f"\n   [{bt}] {menu}")
        print(f"      {fname}:{ln}")
        print(f"      {desc}")
