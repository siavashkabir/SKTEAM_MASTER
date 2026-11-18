#!/data/data/com.termux/files/usr/bin/bash
# ═══ SK-START-LOCK — جلوگیری از اجرای دوگانه ═══
LOCKDIR="$HOME/.skteam_start.lock.d"
if ! mkdir "$LOCKDIR" 2>/dev/null; then
    echo "⚠️ start_all.sh قبلاً در حال اجراست → خروج"
    exit 0
fi
trap "rmdir '$LOCKDIR' 2>/dev/null" EXIT INT TERM

# Sk.Team — راه‌اندازی همه ۵ سرویس (11T Native + Player proot)
set -e
LOG_DIR="$HOME/logs"
mkdir -p "$LOG_DIR" "$HOME/sk_media/logs"

echo "════════ شروع $(date) ════════"

# کشتن سرویس‌های قبلی
pkill -9 -f "python3 -u main.py" 2>/dev/null || true
pkill -9 -f "python3 -u bot.py" 2>/dev/null || true
pkill -9 -f "sk_media/server.py" 2>/dev/null || true
pkill -9 -f "userbot_service.py" 2>/dev/null || true
pkill -9 -f "player.py" 2>/dev/null || true
pkill -9 -f "proot --kill-on-exit" 2>/dev/null || true
sleep 4

# ۱. Media Server
echo "▶ Media Server..."
cd $HOME/groupbot && source venv/bin/activate
: > $LOG_DIR/server.log
setsid python3 -u $HOME/sk_media/server.py < /dev/null > $LOG_DIR/server.log 2>&1 &
sleep 4 && deactivate

# ۲. ربات مدیریت
echo "▶ ربات مدیریت..."
cd $HOME/groupbot && source venv/bin/activate
: > $LOG_DIR/groupbot.log
setsid python3 -u main.py < /dev/null > $LOG_DIR/groupbot.log 2>&1 &
sleep 10 && deactivate

# ۳. ربات موزیک
echo "▶ ربات موزیک..."
cd $HOME/skteam_music && source venv/bin/activate
: > $LOG_DIR/music.log
setsid python3 -u bot.py < /dev/null > $LOG_DIR/music.log 2>&1 &
sleep 10 && deactivate

# ۴. Userbot
echo "▶ Userbot..."
cd $HOME/groupbot && source venv/bin/activate
: > $LOG_DIR/userbot.log
setsid python3 -u userbot_service.py < /dev/null > $LOG_DIR/userbot.log 2>&1 &
sleep 6 && deactivate

# ۵. Player (proot)
echo "▶ Player (proot)..."
: > $HOME/sk_media/logs/player.log
setsid proot-distro login ubuntu --isolated -- bash -c '
cd /root/sk_media && \
set -a && source /root/melody-player/.env && set +a && \
export MUSIC_BOT_API_KEY="SktTeam_vcstat_1791787127_secret" && \
source /root/melody-player/venv/bin/activate && \
exec python3 -u player.py
' < /dev/null > $HOME/sk_media/logs/player.log 2>&1 &
sleep 15

echo ""
echo "════ سرویس‌های زنده ════"
ps aux | grep -E "main\.py|bot\.py|server\.py|player\.py|userbot_service" | grep -v grep
echo ""
echo "════════ تموم شد $(date) ════════"


# ───── Watchdog ─────
echo "▶ Watchdog..."
pkill -9 -f "watchdog.py" 2>/dev/null || true
sleep 1
: > $HOME/logs/watchdog.log
setsid python3 -u $HOME/watchdog.py < /dev/null > $HOME/logs/watchdog.log 2>&1 &
sleep 3
echo "✅ Watchdog راه‌اندازی شد"


# ───── SSH Server ─────
echo "▶ SSH Server..."
pkill -9 sshd 2>/dev/null || true
sleep 2
sshd
sleep 2
if ps aux | grep -q "[s]shd"; then
    echo "✅ SSH Server زنده"
else
    echo "❌ SSH Server راه نیفتاد"
fi
