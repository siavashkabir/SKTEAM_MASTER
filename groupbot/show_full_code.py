import os

print("="*80)
print("🔍 کد کامل هندلرهای تمدید")
print("="*80)

with open('modules/start.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# === 1. osub_manual_ok_ (تأیید پرداخت) ===
print("\n=== 1. هندلر osub_manual_ok_ (کامل) ===")
for i, line in enumerate(lines):
    if 'action.startswith("osub_manual_ok_")' in line:
        for j in range(i, min(i+60, len(lines))):
            print(f"   {j+1}: {lines[j].rstrip()}")
            # توقف در خط بعدی action
            if j > i+5 and ('if action' in lines[j] and j != i):
                break
        break

# === 2. osub_ext_ (تمدید نهایی) ===
print("\n" + "="*80)
print("=== 2. هندلر osub_ext_ (کامل) ===")
for i, line in enumerate(lines):
    if 'action.startswith("osub_ext_")' in line:
        for j in range(i, min(i+70, len(lines))):
            print(f"   {j+1}: {lines[j].rstrip()}")
            if j > i+5 and ('if action' in lines[j] and j != i):
                break
        break

# === 3. osub_cus_ (انتخاب مدت) ===
print("\n" + "="*80)
print("=== 3. هندلر osub_cus_ (کامل) ===")
for i, line in enumerate(lines):
    if 'action.startswith("osub_cus_")' in line:
        for j in range(i, min(i+50, len(lines))):
            print(f"   {j+1}: {lines[j].rstrip()}")
            if j > i+5 and ('if action' in lines[j] and j != i):
                break
        break

# === 4. جستجوی "invoice" یا "فاکتور" ===
print("\n" + "="*80)
print("=== 4. جستجوی کلمه «فاکتور» ===")
for i, line in enumerate(lines):
    if 'فاکتور' in line or 'invoice' in line.lower():
        print(f"   خط {i+1}: {line.strip()[:150]}")

# === 5. جستجوی notify_owner ===
print("\n" + "="*80)
print("=== 5. notify_owner در start.py ===")
for i, line in enumerate(lines):
    if 'notify_owner' in line:
        print(f"   خط {i+1}: {line.strip()[:150]}")
