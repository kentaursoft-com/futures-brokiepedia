import asyncio
import aiohttp
import os
import json
from datetime import datetime, timezone

CF_ACCOUNT_ID = os.environ.get("CF_ACCOUNT_ID")
CF_API_TOKEN = os.environ.get("CF_API_TOKEN")
KV_NAMESPACE_ID = os.environ.get("KV_NAMESPACE_ID")
VPS_INTERNAL_KEY = os.environ.get("VPS_INTERNAL_KEY")

async def write_kv(key: str, value: str):
    if not CF_ACCOUNT_ID or not CF_API_TOKEN or not KV_NAMESPACE_ID:
        print(f"[health] Missing Cloudflare credentials, skipping KV write for {key}")
        return
    
    url = (f"https://api.cloudflare.com/client/v4/accounts/"
           f"{CF_ACCOUNT_ID}/storage/kv/namespaces/"
           f"{KV_NAMESPACE_ID}/values/{key}")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.put(
                url,
                data=value,
                headers={"Authorization": f"Bearer {CF_API_TOKEN}",
                        "Content-Type": "text/plain"}
            ) as resp:
                if resp.status not in (200, 201):
                    print(f"[health] KV write failed for {key}: {resp.status}")
    except Exception as e:
        print(f"[health] KV write error for {key}: {e}")

async def check_questdb() -> bool:
    try:
        async with aiohttp.ClientSession() as s:
            r = await asyncio.wait_for(
                s.get("http://localhost:9000/health"), timeout=3)
            return r.status == 200
    except:
        return False

async def check_chromadb() -> bool:
    try:
        async with aiohttp.ClientSession() as s:
            r = await asyncio.wait_for(
                s.get("http://localhost:8001/api/v1/heartbeat"), timeout=3)
            return r.status == 200
    except:
        return False

async def report_health(binance_ws_alive: bool):
    now = datetime.now(timezone.utc).isoformat()
    questdb_ok = await check_questdb()
    chroma_ok = await check_chromadb()

    await write_kv("binance_ws_alive",
                   json.dumps({"value": binance_ws_alive, "ts": now}))
    await write_kv("questdb_alive",
                   json.dumps({"value": questdb_ok, "ts": now}))
    await write_kv("chromadb_alive",
                   json.dumps({"value": chroma_ok, "ts": now}))
    await write_kv("turso_sync_ts",
                   json.dumps({"ts": now}))
    
    print(f"[health] QuestDB:{questdb_ok} "
          f"ChromaDB:{chroma_ok} WS:{binance_ws_alive} @ {now}")

async def run_health_loop(get_ws_status_fn):
    while True:
        try:
            ws_alive = get_ws_status_fn()
            await report_health(ws_alive)
        except Exception as e:
            print(f"[health] Error: {e}")
        await asyncio.sleep(30)
