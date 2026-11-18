"""Helper for Manager bot to talk to Sk.Media server."""
import httpx
SERVER = "http://127.0.0.1:8080"

async def send_command(action, chat_id, **kw):
    payload = {"action": action, "chat_id": chat_id, **kw}
    async with httpx.AsyncClient(timeout=10) as h:
        r = await h.post(f"{SERVER}/command", json=payload)
        return r.json()

async def play(chat_id, query, user=""):
    return await send_command("play", chat_id, query=query, requested_by=user)

async def pause(chat_id):   return await send_command("pause", chat_id)
async def resume(chat_id):  return await send_command("resume", chat_id)
async def stop(chat_id):    return await send_command("stop", chat_id)
async def mute(chat_id):    return await send_command("mute", chat_id)
async def unmute(chat_id):  return await send_command("unmute", chat_id)

async def now_playing(chat_id):
    async with httpx.AsyncClient(timeout=10) as h:
        r = await h.get(f"{SERVER}/now-playing", params={"chat_id": chat_id})
        return r.json()

async def health():
    async with httpx.AsyncClient(timeout=10) as h:
        r = await h.get(f"{SERVER}/health")
        return r.json()
