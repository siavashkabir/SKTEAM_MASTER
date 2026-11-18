#!/data/data/com.termux/files/usr/bin/bash

ST=modules/start.py
TS=$(date +%Y%m%d_%H%M%S)

cp "$ST" "$ST.bak_pmdebug_$TS"
echo "✅ بک‌آپ: $ST.bak_pmdebug_$TS"
echo ""

source venv/bin/activate

python3 << 'PYEOF'
ST = "/data/data/com.termux/files/home/groupbot/modules/start.py"

with open(ST, "r", encoding="utf-8") as f:
    content = f.read()

# پیدا کردن کد فعلی ذخیره perms
old = '''        try:
            from database import set_admin_perm
            _perms = PROMOTE_WAIT.get(uid, {}).get("perms", {})
            print(f"[PM_CONFIRM] perms count = {len(_perms)}")
            for _perm_name, _enabled in _perms.items():
                set_admin_perm(chat_id, target_id, "admin", _perm_name, 1 if _enabled else 0)
        except Exception as _e:
            print(f"[PM_CONFIRM PERMS ERR] {_e}")'''

new = '''        try:
            from database import set_admin_perm
            _perms = PROMOTE_WAIT.get(uid, {}).get("perms", {})
            print(f"[PM_CONFIRM] perms count = {len(_perms)}")
            print(f"[PM_CONFIRM] perms = {_perms}")
            _saved = 0
            for _perm_name, _enabled in _perms.items():
                try:
                    _val = 1 if _enabled else 0
                    print(f"[PM_CONFIRM] writing {_perm_name}={_val}")
                    set_admin_perm(chat_id, target_id, "admin", _perm_name, _val)
                    _saved += 1
                    print(f"[PM_CONFIRM] ✅ saved {_perm_name}")
                except Exception as _inner:
                    print(f"[PM_CONFIRM INNER ERR] {_perm_name}: {_inner}")
            print(f"[PM_CONFIRM] TOTAL SAVED = {_saved}/{len(_perms)}")
        except Exception as _e:
            print(f"[PM_CONFIRM PERMS ERR] {_e}")
            import traceback
            traceback.print_exc()'''

if old in content:
    content = content.replace(old, new, 1)
    print("✅ debug اضافه شد")
else:
    print("⚠️ الگو پیدا نشد — دنبالش می‌گردم...")
    import re
    pattern = r'from database import set_admin_perm.*?print\(f"\[PM_CONFIRM PERMS ERR\] \{_e\}"\)'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        print("❌ الگو با regex هم پیدا نشد")
        print("کد فعلی:")
        print(match.group(0)[:500])
        exit(1)
    else:
        print("❌ هیچ الگویی پیدا نشد")
        exit(1)

with open(ST, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ ذخیره شد")
PYEOF

echo ""

if python3 -m py_compile "$ST" 2>&1; then
    echo "✅ کامپایل OK"
else
    echo "❌ خطا — rollback!"
    cp "$ST.bak_pmdebug_$TS" "$ST"
    exit 1
fi
echo ""

echo "─── چک: set_admin_perm signature ───"
grep -n "def set_admin_perm" database.py
LINE=$(grep -n "def set_admin_perm" database.py | head -1 | cut -d: -f1)
if [ -n "$LINE" ]; then
    sed -n "${LINE},$((LINE+25))p" database.py
fi
echo ""

echo "═══════════════════════════════════════════════════"
echo "✅ Fix انجام شد"
echo ""
echo "🎯 ری‌استارت:"
echo "pkill -9 -f 'python3 -u'; sleep 3; rm -f .bot.lock; nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 & sleep 15"
echo "═══════════════════════════════════════════════════"
