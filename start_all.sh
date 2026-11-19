#!/data/data/com.termux/files/usr/bin/bash

set -euo pipefail

ROOT="${SKTEAM_ROOT:-$HOME}"
LOG_DIR="${SKTEAM_LOG_DIR:-$HOME/logs}"
STATE_DIR="${SKTEAM_STATE_DIR:-$HOME/.skteam_services}"
LOCK_DIR="$STATE_DIR/start.lock"

mkdir -p "$LOG_DIR" "$STATE_DIR"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
    echo "start_all.sh قبلاً در حال اجراست؛ خروج."
    exit 0
fi
trap 'rmdir "$LOCK_DIR" 2>/dev/null || true' EXIT INT TERM

stop_service() {
    local name="$1"
    local pid_file="$STATE_DIR/$name.pid"
    local pid

    [[ -f "$pid_file" ]] || return 0
    pid="$(cat "$pid_file" 2>/dev/null || true)"
    if [[ "$pid" =~ ^[0-9]+$ ]] && kill -0 "$pid" 2>/dev/null; then
        kill -TERM "$pid" 2>/dev/null || true
        for _ in {1..50}; do
            kill -0 "$pid" 2>/dev/null || break
            sleep 0.1
        done
        kill -KILL "$pid" 2>/dev/null || true
    fi
    rm -f "$pid_file"
}

start_service() {
    local name="$1"
    local delay="$2"
    local log="$3"
    shift 3

    : > "$log"
    setsid "$@" < /dev/null > "$log" 2>&1 &
    local pid=$!
    echo "$pid" > "$STATE_DIR/$name.pid"
    sleep "$delay"
    if ! kill -0 "$pid" 2>/dev/null; then
        echo "سرویس $name راه‌اندازی نشد؛ لاگ: $log" >&2
        return 1
    fi
    echo "▶ $name آماده شد (PID $pid)"
}

python_service() {
    local name="$1"
    local delay="$2"
    local directory="$3"
    local venv="$4"
    local script="$5"

    local log="$LOG_DIR/$name.log"
    start_service "$name" "$delay" "$log" \
        bash -c 'cd "$1" && source "$2/bin/activate" && exec python3 -u "$3"' \
        bash "$directory" "$venv" "$script"
}

for service in groupbot music userbot server player watchdog; do
    stop_service "$service"
done

echo "════════ شروع $(date) ════════"

python_service server 3 "$ROOT/sk_media" "$ROOT/groupbot/venv" "$ROOT/sk_media/server.py"
python_service groupbot 8 "$ROOT/groupbot" "$ROOT/groupbot/venv" "$ROOT/groupbot/main.py"
python_service music 8 "$ROOT/skteam_music" "$ROOT/skteam_music/venv" "$ROOT/skteam_music/bot.py"
python_service userbot 5 "$ROOT/groupbot" "$ROOT/groupbot/venv" "$ROOT/groupbot/userbot_service.py"

echo "▶ راه‌اندازی Player..."
player_log="$LOG_DIR/player.log"
if command -v proot-distro >/dev/null 2>&1; then
    start_service player 10 "$player_log" \
        proot-distro login ubuntu --isolated -- \
        bash -c '
            set -e
            cd /root/sk_media
            set -a
            source /root/melody-player/.env
            set +a
            : "${MUSIC_BOT_API_KEY:?MUSIC_BOT_API_KEY is required}"
            source /root/melody-player/venv/bin/activate
            exec python3 -u player.py
        '
else
    echo "proot-distro پیدا نشد؛ Player اجرا نمی‌شود." >&2
fi

if [[ -f "$ROOT/watchdog.py" ]]; then
    echo "▶ راه‌اندازی Watchdog..."
    start_service watchdog 2 "$LOG_DIR/watchdog.log" python3 -u "$ROOT/watchdog.py"
else
    echo "فایل $ROOT/watchdog.py پیدا نشد؛ Watchdog اجرا نمی‌شود."
fi

if command -v sshd >/dev/null 2>&1; then
    if ! pgrep -x sshd >/dev/null 2>&1; then
        sshd
    fi
    echo "▶ SSH daemon بررسی شد."
fi

echo "════════ سرویس‌های فعال ════════"
for pid_file in "$STATE_DIR"/*.pid; do
    [[ -e "$pid_file" ]] || continue
    name="$(basename "$pid_file" .pid)"
    pid="$(cat "$pid_file")"
    if kill -0 "$pid" 2>/dev/null; then
        echo "$name: فعال (PID $pid)"
    else
        echo "$name: متوقف شده" >&2
    fi
done
