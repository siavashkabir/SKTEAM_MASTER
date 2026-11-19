"""Melody helper player.

The helper only talks to the panel API and Telegram; all import-time work is
deliberately limited to constants so configuration errors are reported at
startup instead of while tooling imports the module.
"""

from __future__ import annotations

import asyncio
import hashlib
import logging
import os
import subprocess
import time
from pathlib import Path
from typing import Any

import httpx
import yt_dlp
from pyrogram import Client
from pytgcalls import PyTgCalls, filters
from pytgcalls.types import AudioQuality, MediaStream, Update, VideoQuality

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("melody-player")

EQ = {
    "normal": "",
    "bass": "bass=g=8",
    "pop": "bass=g=3,equalizer=f=1000:t=q:w=1:g=3,treble=g=3",
    "rock": "bass=g=5,equalizer=f=1000:t=q:w=1:g=-2,treble=g=4",
    "vocal": "bass=g=-3,equalizer=f=2500:t=q:w=1:g=5",
    "classical": "equalizer=f=250:t=q:w=1:g=2,treble=g=3",
}
MAX_FAILS = 3


def required_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"missing required environment variable: {name}")
    return value


def ydl_opts(output: str, mp3: bool) -> dict[str, Any]:
    opts: dict[str, Any] = {
        "format": "bestaudio/best",
        "outtmpl": output,
        "quiet": True,
        "noplaylist": True,
        "default_search": "ytsearch1",
        "extractor_args": {"youtube": {"player_client": ["android", "ios"]}},
    }
    if mp3:
        opts["postprocessors"] = [
            {"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "320"},
            {"key": "FFmpegMetadata"},
        ]
    return opts


def _find_download(info: dict[str, Any], expected: Path, ydl: yt_dlp.YoutubeDL) -> Path:
    filename = Path(ydl.prepare_filename(info))
    candidates = [expected, filename, filename.with_suffix(".mp3"), filename.with_suffix(".mp4")]
    candidates.extend(filename.parent.glob(f"{expected.stem}.*"))
    for candidate in candidates:
        if candidate.is_file() and candidate.stat().st_size > 0:
            return candidate
    raise FileNotFoundError(f"yt-dlp did not produce a file for {info.get('title') or filename.name}")


def download_youtube(cache: Path, query: str, mp3: bool, video: bool = False) -> tuple[str, dict[str, Any]]:
    key = hashlib.sha256(query.encode("utf-8")).hexdigest()[:20]
    base = cache / f"{key}{'_mp3' if mp3 else ''}{'_v' if video else ''}"
    expected = base.with_suffix(".mp3" if mp3 else ".mp4" if video else ".webm")
    if expected.is_file() and expected.stat().st_size > 0:
        return str(expected), {}

    opts = ydl_opts(str(base) + ".%(ext)s", mp3)
    if video:
        opts["format"] = "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720]/best"
        opts["merge_output_format"] = "mp4"
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(query, download=True)
        entries = info.get("entries") if isinstance(info, dict) else None
        if entries:
            info = next((entry for entry in entries if entry), None)
        if not isinstance(info, dict):
            raise RuntimeError("yt-dlp returned no media information")
        path = _find_download(info, expected, ydl)
    return str(path), info


def media_stream(path: str, eq: str, seek: float = 0, video: bool = False) -> MediaStream:
    filters_for_stream: list[str] = []
    audio_filter = EQ.get(eq, "")
    if audio_filter:
        filters_for_stream.extend(("-af", audio_filter))
    if seek > 1:
        filters_for_stream[:0] = ["-ss", str(int(seek))]
    args = " ".join(filters_for_stream) or None
    if video:
        return MediaStream(
            path,
            audio_parameters=AudioQuality.HIGH,
            video_parameters=VideoQuality.HD_720p,
            ffmpeg_parameters=args,
        )
    return MediaStream(
        path,
        audio_parameters=AudioQuality.STUDIO,
        video_flags=MediaStream.Flags.IGNORE,
        ffmpeg_parameters=args,
    )


def probe_duration(path: str) -> int | None:
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
            capture_output=True,
            text=True,
            timeout=20,
            check=True,
        )
        return int(float(result.stdout.strip())) if result.stdout.strip() else None
    except (FileNotFoundError, OSError, subprocess.SubprocessError, ValueError):
        return None


class MelodyPlayer:
    def __init__(
        self,
        *,
        api_base: str,
        player_key: str,
        calls: Any,
        http: httpx.AsyncClient,
        cache: Path,
    ) -> None:
        self.api_base = api_base.rstrip("/")
        self.player_key = player_key
        self.calls = calls
        self.http = http
        self.cache = cache
        self.state: dict[int, dict[str, Any]] = {}
        self.locks: dict[int, asyncio.Lock] = {}
        self.background_tasks: set[asyncio.Task[Any]] = set()

    async def response_json(self, response: httpx.Response) -> dict[str, Any]:
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, dict):
            raise RuntimeError(f"panel returned a non-object JSON response for {response.request.url.path}")
        return data

    async def fetch_media(self, item: dict[str, Any]) -> str:
        file_id = item.get("tg_file_id")
        if file_id:
            digest = hashlib.sha256(str(file_id).encode("utf-8")).hexdigest()
            path = self.cache / f"tg_{digest[:24]}"
            if not path.is_file() or path.stat().st_size < 10_000:
                response = await self.http.get(
                    f"{self.api_base}/player/file", params={"file_id": file_id}
                )
                response.raise_for_status()
                content_type = response.headers.get("content-type", "")
                if "text/html" in content_type or len(response.content) < 10_000:
                    raise RuntimeError(
                        f"file download failed [{response.status_code}]: {response.text[:150]}"
                    )
                await asyncio.to_thread(self._replace_file, path, response.content)
            return str(path)

        source = item.get("source_url")
        if not source:
            raise RuntimeError("queue item has no source_url or tg_file_id")
        if (
            item.get("is_video")
            and (".m3u8" in source or source.startswith("rtmp") or source.endswith((".mp4", ".mkv", ".ts")))
        ):
            return source
        path, _ = await asyncio.to_thread(
            download_youtube, self.cache, source, False, bool(item.get("is_video"))
        )
        return path

    @staticmethod
    def _replace_file(path: Path, content: bytes) -> None:
        temporary = path.with_suffix(path.suffix + ".part")
        temporary.write_bytes(content)
        temporary.replace(path)

    async def set_volume(self, chat_id: int, volume: int) -> None:
        if volume <= 0:
            await self.calls.mute(chat_id)
            return
        try:
            await self.calls.unmute(chat_id)
        except Exception:
            pass
        await self.calls.change_volume_call(chat_id, max(1, min(200, volume)))

    @staticmethod
    def elapsed(player_state: dict[str, Any]) -> float:
        paused_at = player_state.get("paused_at")
        if paused_at is not None:
            return max(0.0, paused_at - player_state["started"]) + player_state.get("offset", 0)
        return max(0.0, time.monotonic() - player_state["started"]) + player_state.get("offset", 0)

    async def play_next(
        self, chat_id: int, finished: str | None = None, failed: bool = False, error: str = ""
    ) -> None:
        lock = self.locks.setdefault(chat_id, asyncio.Lock())
        async with lock:
            failures = 0
            while True:
                payload: dict[str, Any] = {"chat_id": chat_id, "finished_item_id": finished}
                if failed:
                    payload.update(failed=True, error=error[:400])
                response = await self.http.post(f"{self.api_base}/player/next", json=payload)
                data = await self.response_json(response)
                failed = False
                item = data.get("item")
                if not item:
                    self.state.pop(chat_id, None)
                    try:
                        await self.calls.leave_call(chat_id)
                    except Exception:
                        pass
                    return

                eq = str(data.get("eq", "normal"))
                is_video = bool(item.get("is_video"))
                try:
                    path = await self.fetch_media(item)
                    try:
                        await self.calls.play(chat_id, media_stream(path, eq, video=is_video))
                    except Exception:
                        if eq == "normal":
                            raise
                        log.warning("play with EQ %s failed; retrying without EQ", eq)
                        await self.calls.play(chat_id, media_stream(path, "normal", video=is_video))
                        eq = "normal"
                except Exception as exc:
                    failures += 1
                    log.error("play failed (%d/%d): %s", failures, MAX_FAILS, exc)
                    finished, failed, error = str(item.get("id", "")), True, str(exc)
                    if failures >= MAX_FAILS:
                        await self.http.post(
                            f"{self.api_base}/player/next",
                            json={
                                "chat_id": chat_id,
                                "finished_item_id": finished,
                                "failed": True,
                                "error": error[:400],
                            },
                        )
                        self.state.pop(chat_id, None)
                        return
                    continue

                try:
                    await self.set_volume(chat_id, int(data.get("volume", 100)))
                except Exception as exc:
                    log.warning("volume: %s (helper may need admin rights)", exc)
                duration = item.get("duration")
                if not duration and not path.startswith(("http://", "https://", "rtmp://")):
                    duration = await asyncio.to_thread(probe_duration, path)
                self.state[chat_id] = {
                    "item": item,
                    "path": path,
                    "eq": eq,
                    "video": is_video,
                    "started": time.monotonic(),
                    "paused_at": None,
                    "offset": 0.0,
                    "duration": duration,
                }
                return

    async def download_and_send(self, chat_id: int, payload: dict[str, Any]) -> None:
        source = payload.get("source_url")
        if not source:
            raise RuntimeError("download command has no source_url")
        path, info = await asyncio.to_thread(
            download_youtube, self.cache, source, True, False
        )
        with open(path, "rb") as media_file:
            files = {"audio": (Path(path).name, media_file, "audio/mpeg")}
            form = {
                "chat_id": str(chat_id),
                "title": str(payload.get("title") or info.get("title") or ""),
                "performer": str(payload.get("performer") or info.get("uploader") or ""),
                "duration": str(int(info.get("duration") or 0)),
                "queue_item_id": str(payload.get("queue_item_id") or ""),
            }
            response = await self.http.post(f"{self.api_base}/player/upload", data=form, files=files)
        response.raise_for_status()
        log.info("upload complete for chat %s", chat_id)

    async def handle(self, command: dict[str, Any]) -> None:
        try:
            chat_id = int(command["chat_id"])
        except (KeyError, TypeError, ValueError) as exc:
            raise RuntimeError("command has invalid chat_id") from exc
        action = str(command.get("action", "")).lower()
        payload = command.get("payload") or {}
        player_state = self.state.get(chat_id)
        log.info("command %s for %s", action, chat_id)

        if action == "play_next":
            if not player_state:
                await self.play_next(chat_id)
        elif action == "pause" and player_state:
            await self.calls.pause(chat_id)
            if player_state.get("paused_at") is None:
                player_state["paused_at"] = time.monotonic()
        elif action == "resume" and player_state:
            await self.calls.resume(chat_id)
            if player_state.get("paused_at") is not None:
                player_state["started"] += time.monotonic() - player_state["paused_at"]
                player_state["paused_at"] = None
        elif action == "skip":
            finished = player_state["item"]["id"] if player_state else None
            await self.play_next(chat_id, finished)
        elif action == "stop":
            self.state.pop(chat_id, None)
            try:
                await self.calls.leave_call(chat_id)
            except Exception:
                pass
        elif action == "volume" and player_state:
            await self.set_volume(chat_id, int(payload.get("volume", 100)))
        elif action == "eq" and player_state:
            position = self.elapsed(player_state)
            eq = str(payload.get("eq", "normal"))
            await self.calls.play(
                chat_id,
                media_stream(
                    player_state["path"], eq, position, video=bool(player_state.get("video"))
                ),
            )
            player_state.update(
                eq=eq, started=time.monotonic(), offset=position, paused_at=None
            )
        elif action == "download":
            self.spawn(self.download_and_send(chat_id, payload))
        else:
            log.warning("ignored unknown or inactive command %s for %s", action, chat_id)

    def spawn(self, coroutine: Any) -> asyncio.Task[Any]:
        task = asyncio.create_task(coroutine)
        self.background_tasks.add(task)

        def done(completed: asyncio.Task[Any]) -> None:
            self.background_tasks.discard(completed)
            if not completed.cancelled():
                error = completed.exception()
                if error:
                    log.error("background task failed", exc_info=(type(error), error, error.__traceback__))

        task.add_done_callback(done)
        return task

    async def on_stream_end(self, _: Any, update: Update) -> None:
        player_state = self.state.get(update.chat_id)
        if not player_state:
            return
        elapsed = time.monotonic() - player_state["started"]
        if elapsed < 5 and player_state["eq"] != "normal":
            player_state["eq"] = "normal"
            player_state["started"] = time.monotonic()
            await self.calls.play(
                update.chat_id,
                media_stream(
                    player_state["path"], "normal", video=bool(player_state.get("video"))
                ),
            )
            return
        await self.play_next(
            update.chat_id,
            player_state["item"]["id"],
            failed=elapsed < 5,
            error="stream ended instantly" if elapsed < 5 else "",
        )

    async def progress_loop(self) -> None:
        while True:
            await asyncio.sleep(10)
            for chat_id, player_state in list(self.state.items()):
                try:
                    await self.http.post(
                        f"{self.api_base}/player/progress",
                        json={
                            "chat_id": chat_id,
                            "item_id": player_state["item"]["id"],
                            "position": int(self.elapsed(player_state)),
                            "duration": player_state.get("duration"),
                            "paused": player_state.get("paused_at") is not None,
                        },
                    )
                except Exception as exc:
                    log.warning("progress for %s failed: %s", chat_id, exc)

    async def poll_loop(self, poll_seconds: float) -> None:
        while True:
            try:
                response = await self.http.get(f"{self.api_base}/player/commands")
                data = await self.response_json(response)
                for command in data.get("commands", []):
                    try:
                        await self.handle(command)
                    except Exception:
                        log.exception("command failed: %r", command)
            except Exception as exc:
                log.warning("poll error: %s", exc)
            await asyncio.sleep(poll_seconds)

    async def close(self) -> None:
        for task in self.background_tasks:
            task.cancel()
        if self.background_tasks:
            await asyncio.gather(*self.background_tasks, return_exceptions=True)


async def run() -> None:
    api_base = required_env("PANEL_API_BASE").rstrip("/")
    player_key = required_env("PLAYER_API_KEY")
    api_id = int(required_env("TG_API_ID"))
    api_hash = required_env("TG_API_HASH")
    session = required_env("TG_SESSION_STRING")
    poll_seconds = max(0.1, float(os.environ.get("POLL_SECONDS", "2")))
    cache = Path(os.environ.get("CACHE_DIR", "/data/cache")).expanduser()
    cache.mkdir(parents=True, exist_ok=True)
    workdir = Path(os.environ.get("PYRO_WORKDIR", "./data")).expanduser()
    workdir.mkdir(parents=True, exist_ok=True)

    headers = {
        "X-Api-Key": player_key,
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/126.0 Safari/537.36 SKTeamPlayer/2.0"
        ),
        "Accept": "*/*",
    }
    app = Client(
        "helper",
        api_id=api_id,
        api_hash=api_hash,
        session_string=session,
        workdir=str(workdir),
    )
    calls = PyTgCalls(app)
    async with httpx.AsyncClient(timeout=120, headers=headers) as http:
        helper = MelodyPlayer(
            api_base=api_base,
            player_key=player_key,
            calls=calls,
            http=http,
            cache=cache,
        )
        calls.on_update(filters.stream_end())(helper.on_stream_end)
        await app.start()
        try:
            await calls.start()
            me = await app.get_me()
            log.info("helper account online: %s", me.username or me.id)
            progress = asyncio.create_task(helper.progress_loop())
            try:
                await helper.poll_loop(poll_seconds)
            finally:
                progress.cancel()
                await asyncio.gather(progress, return_exceptions=True)
                await helper.close()
        finally:
            try:
                await calls.stop()
            finally:
                await app.stop()


def main() -> None:
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        pass
