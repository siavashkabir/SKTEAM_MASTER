#!/data/data/com.termux/files/usr/bin/bash
# ==================================================
# Startup Script - راه‌اندازی خودکار همه سرویس‌ها
# ==================================================

# رنگ‌ها برای خروجی زیبا
GREEN="\033[0;32m"
RED="\033[0;31m"
YELLOW="\033[1;33m"
BLUE="\033[0;34m"
NC="\033[0m"

LOG_FILE="$HOME/groupbot/startup.log"
BOT_DIR="$HOME/groupbot"

log() {
    echo -e "$1"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE" 2>/dev/null
}

echo ""
echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo -e "${BLUE}    🚀 Skteam Bot - Startup Script${NC}"
echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo ""

# چک اتصال به تلگرام
log "${YELLOW}[1/5]${NC} چک اتصال به تلگرام..."
if ping -c 1 -W 3 api.telegram.org > /dev/null 2>&1; then
    log "${GREEN}✅ اتصال به تلگرام OK${NC}"
else
    log "${RED}⚠️  اتصال به تلگرام ضعیف یا قطع! VPN رو چک کن.${NC}"
    log "${YELLOW}   ولی ادامه می‌دم (شاید بعداً وصل شه)...${NC}"
fi

# رفتن به پوشه پروژه
cd "$BOT_DIR" || { log "${RED}❌ پوشه groupbot پیدا نشد!${NC}"; exit 1; }

# فعال کردن محیط مجازی
if [ -f "$BOT_DIR/venv/bin/activate" ]; then
    source "$BOT_DIR/venv/bin/activate"
    log "${GREEN}✅ محیط مجازی فعال شد${NC}"
else
    log "${RED}❌ محیط مجازی پیدا نشد!${NC}"
    exit 1
fi

# تابع برای چک و راه‌اندازی سرویس
start_service() {
    local name="$1"
    local script="$2"
    local logfile="$3"
    
    # چک کن قبلاً اجرا شده
    if pgrep -f "$script" > /dev/null 2>&1; then
        log "${YELLOW}⚠️  $name قبلاً در حال اجراست${NC}"
        return 0
    fi
    
    # راه‌اندازی
    nohup python3 -u "$script" > "$logfile" 2>&1 &
    local pid=$!
    sleep 2
    
    # چک کن واقعاً اجرا شد
    if kill -0 $pid 2>/dev/null; then
        log "${GREEN}✅ $name راه‌اندازی شد (PID: $pid)${NC}"
        return 0
    else
        log "${RED}❌ $name شکست خورد! لاگ: $logfile${NC}"
        return 1
    fi
}

# ۲. راه‌اندازی ربات اصلی
log "${YELLOW}[2/5]${NC} راه‌اندازی ربات اصلی..."
start_service "ربات اصلی" "main.py" "$HOME/groupbot_bot.log"

# صبر کن ربات کامل بالا بیاد
sleep 5

# چک کن ربات واقعاً کار می‌کنه
if tail -n 20 "$HOME/groupbot_bot.log" 2>/dev/null | grep -q "Bot is starting polling"; then
    log "${GREEN}✅ ربات با موفقیت بالا اومد${NC}"
else
    log "${YELLOW}⚠️  ربات شروع کرد ولی لاگ واضح نیست${NC}"
fi

# ۳. راه‌اندازی backup_daemon
log "${YELLOW}[3/5]${NC} راه‌اندازی Backup Daemon (هر ۶ ساعت)..."
start_service "Backup Daemon" "backup_daemon.py" "$HOME/groupbot_backup_daemon.log"

# ۴. راه‌اندازی backup_watcher
log "${YELLOW}[4/5]${NC} راه‌اندازی Backup Watcher (هر تغییر)..."
start_service "Backup Watcher" "backup_watcher.py" "$HOME/groupbot_backup_watcher.log"

# ۵. راه‌اندازی connection_monitor
log "${YELLOW}[5/5]${NC} راه‌اندازی Connection Monitor (نگهبان اتصال)..."
start_service "Connection Monitor" "connection_monitor.py" "$HOME/groupbot_connection_monitor.log"

# نمایش وضعیت نهایی
echo ""
echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo -e "${GREEN}    ✅ همه سرویس‌ها راه‌اندازی شدن${NC}"
echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo ""

# نمایش وضعیت سرویس‌ها
echo -e "${YELLOW}📊 وضعیت سرویس‌ها:${NC}"
if pgrep -f "main.py" > /dev/null; then
    echo -e "  ${GREEN}✅${NC} ربات اصلی"
else
    echo -e "  ${RED}❌${NC} ربات اصلی"
fi

if pgrep -f "backup_daemon.py" > /dev/null; then
    echo -e "  ${GREEN}✅${NC} Backup Daemon"
else
    echo -e "  ${RED}❌${NC} Backup Daemon"
fi

if pgrep -f "backup_watcher.py" > /dev/null; then
    echo -e "  ${GREEN}✅${NC} Backup Watcher"
else
    echo -e "  ${RED}❌${NC} Backup Watcher"
fi

if pgrep -f "connection_monitor.py" > /dev/null; then
    echo -e "  ${GREEN}✅${NC} Connection Monitor"
else
    echo -e "  ${RED}❌${NC} Connection Monitor"
fi

echo ""
echo -e "${YELLOW}📋 لاگ‌ها:${NC}"
echo "  • ربات:    $HOME/groupbot_bot.log"
echo "  • بکاپ:    $HOME/groupbot_backup_daemon.log"
echo "  • Watcher: $HOME/groupbot_backup_watcher.log"
echo ""
echo -e "${YELLOW}💡 برای چک کردن وضعیت:${NC}"
echo "  $BOT_DIR/status.sh"
echo ""

log "Startup completed"
