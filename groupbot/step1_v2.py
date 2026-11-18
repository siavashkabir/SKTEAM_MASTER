import os, re, glob

print("="*80)
print("🔍 بررسی دقیق: همه patternها در همه فایلها")
print("="*80)

# ============================================================
# 1. جمع‌آوری همه patternها
# ============================================================
all_files = ['main.py']
for f in glob.glob('modules/*.py'):
    if '.bak' not in f and 'crash' not in f:
        all_files.append(f)

all_patterns = {}

for mfile in all_files:
    if not os.path.exists(mfile):
        continue
    with open(mfile, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for i, line in enumerate(lines):
        if 'add_handler' not in line:
            continue
        
        # استخراج pattern
        m = re.search(r'pattern=["\']([^"\']+)["\']', line)
        if not m:
            continue
        
        pat = m.group(1)
        
        # استخراج handler function
        hm = re.search(r'CallbackQueryHandler\((\w+)', line)
        handler_func = hm.group(1) if hm else '?'
        
        # استخراج group
        gm = re.search(r'group=(-?\d+)', line)
        group = gm.group(1) if gm else 'default'
        
        key = pat
        if key not in all_patterns:
            all_patterns[key] = []
        all_patterns[key].append((mfile, i+1, handler_func, group))

print(f"📊 تعداد patternهای یگانه: {len(all_patterns)}")

# چاپ همه
print("\n" + "="*80)
print("📍 همه patternها")
print("="*80)
for pat, locs in sorted(all_patterns.items()):
    print(f"\n📍 {pat[:120]}")
    for f, ln, hf, g in locs:
        print(f"   {f}:{ln} | handler={hf} | group={g}")

# ============================================================
# 2. بررسی 12 کالبک معیوب
# ============================================================
print("\n" + "="*80)
print("🎯 بررسی 12 کالبک معیوب در همه patternها")
print("="*80)

callbacks_to_check = [
    # پنل سازنده اصلی
    ('sub_manage', '💎 مدیریت اشتراک‌ها'),
    ('s_panel_group', '🔗 ورود به پنل گروه'),
    ('owner_readme', '📖 راهنمای کامل'),
    ('owner_set_group', '⚙️ تنظیمات این گروه'),
    ('sys_menu', '🖥 مدیریت سیستم'),
    # بخش سازنده
    ('op_botadmins', '👤 مدیریت ادمین‌های ربات'),
    ('rmt_groups', '🌐 مدیریت گروه‌ها'),
    # پنل مالک گروه
    ('g_op_sub', '💎 مدیریت اشتراک‌ها (مالک)'),
    ('g_op_manage', '👥 مدیریت گروه (مالک)'),
    ('g_op_settings', '⚙️ تنظیمات (مالک)'),
    ('g_depset_menu', '📊 تنظیمات ادمین‌ها'),
    ('g_op_ownerguide', '📖 راهنمای مالک'),
]

result_table = []

for cb, label in callbacks_to_check:
    found_in = []
    for pat, locs in all_patterns.items():
        parts = pat.replace('^(', '').replace(')$', '').split('|')
        # چک دقیق
        if cb in parts:
            for f, ln, hf, g in locs:
                found_in.append((f, ln, hf, g, pat[:60]))
    
    if found_in:
        result_table.append((cb, label, '✅', found_in[0]))
    else:
        result_table.append((cb, label, '❌', None))

print(f"\n{'دکمه':<45} | {'کد':<20} | وضعیت | محل")
print("-" * 130)
for cb, label, status, loc in result_table:
    if loc:
        f, ln, hf, g, pat = loc
        print(f"{label:<45} | {cb:<20} | {status} | {f}:{ln} ({hf}, group={g})")
    else:
        print(f"{label:<45} | {cb:<20} | {status} | ❌ در هیچ pattern نیست!")

# ============================================================
# 3. خلاصه
# ============================================================
print("\n" + "="*80)
print("📊 خلاصه نهایی")
print("="*80)

working = [r for r in result_table if r[2] == '✅']
broken = [r for r in result_table if r[2] == '❌']

print(f"\n✅ در pattern هستن: {len(working)}")
print(f"❌ در pattern نیستن: {len(broken)}")

if broken:
    print("\n🚨 لیست دکمه‌های معیوب واقعی:")
    for cb, label, _, _ in broken:
        print(f"   ❌ {label} ({cb})")
