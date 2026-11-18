#!/data/data/com.termux/files/usr/bin/bash

ST=modules/start.py
TS=$(date +%Y%m%d_%H%M%S)

cp "$ST" "$ST.bak_text_$TS"
echo "✅ بک‌آپ: $ST.bak_text_$TS"

source venv/bin/activate

python3 << 'PYEOF'
ST = "/data/data/com.termux/files/home/groupbot/modules/start.py"

with open(ST, "r", encoding="utf-8") as f:
    content = f.read()

# جایگزینی همه `len(admins)` با `len(_db_admins)`
count1 = content.count("len(admins)")
content = content.replace("len(admins)", "len(_db_admins)")
print(f"✅ {count1} تا 'len(admins)' → 'len(_db_admins)'")

# جایگزینی همه `len(owners)` با `len(_owner_ids)`
count2 = content.count("len(owners)")
content = content.replace("len(owners)", "len(_owner_ids)")
print(f"✅ {count2} تا 'len(owners)' → 'len(_owner_ids)'")

# جایگزینی `str(owners)` و `str(admins)`
count3 = content.count("str(owners)")
content = content.replace("str(owners)", "str(len(_owner_ids))")
print(f"✅ {count3} تا 'str(owners)'")

count4 = content.count("str(admins)")
content = content.replace("str(admins)", "str(len(_db_admins))")
print(f"✅ {count4} تا 'str(admins)'")

# جایگزینی `admins)` تنها (توی متن)
count5 = content.count('" + str(admins)')
content = content.replace('" + str(admins)', '" + str(len(_db_admins))')
print(f"✅ {count5} تا '\" + str(admins)'")

with open(ST, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ ذخیره شد")
PYEOF

echo ""

if python3 -m py_compile "$ST" 2>&1; then
    echo "✅ کامپایل OK"
else
    echo "❌ خطا — rollback!"
    cp "$ST.bak_text_$TS" "$ST"
    exit 1
fi
echo ""

echo "─── چک: admins/owners باقی‌مونده ───"
grep -n "admins\b\|owners\b" "$ST" | grep -v "_db_admins\|_tg_admins\|_owner_ids\|get_group_admins\|admin_perms\|db_admins" | head -10
echo ""

echo "═══════════════════════════════════════════════════"
echo "✅ Fix انجام شد"
echo ""
echo "🎯 ری‌استارت:"
echo "pkill -9 -f 'python3 -u'; sleep 3; rm -f .bot.lock; nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 & sleep 15"
echo "═══════════════════════════════════════════════════"
