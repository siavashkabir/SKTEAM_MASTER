#!/data/data/com.termux/files/usr/bin/bash
# start.sh - اسکریپت راه‌اندازی اولیه ربات

cd ~/groupbot
source venv/bin/activate
nohup python3 -u main.py > ~/groupbot_bot.log 2>&1 &
echo "[START] ربات با موفقیت اجرا شد."
