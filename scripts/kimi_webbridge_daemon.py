#!/usr/bin/env python3
"""
kimi_webbridge_daemon.py — Local WebBridge Server on 127.0.0.1:10086
Accepts WebSocket connections from the Kimi browser extension at ws://127.0.0.1:10086/ws
and exposes HTTP POST /command + GET /status on http://127.0.0.1:10086.
"""
import asyncio
import json
import uuid
from aiohttp import web

connected_ws = None
pending_requests = {}

async def handle_status(request):
    return web.json_response({
        "ok": True,
        "version": "2.0.24",
        "connected": connected_ws is not None and not connected_ws.closed,
        "skill_mismatch": False
    })

async def handle_ws(request):
    global connected_ws
    ws = web.WebSocketResponse(max_msg_size=100 * 1024 * 1024)
    await ws.prepare(request)
    connected_ws = ws
    print("[KimiWebBridge] Browser extension connected via WebSocket!")

    try:
        async for msg in ws:
            if msg.type == web.WSMsgType.TEXT:
                data = json.loads(msg.data)
                mtype = data.get("type")
                if mtype == "hello":
                    await ws.send_json({"type": "hello_ack", "payload": {"version": "2.0.24"}})
                elif mtype == "ping":
                    await ws.send_json({"type": "pong"})
                elif mtype == "tool_result":
                    req_id = data.get("responseToRequestId")
                    fut = pending_requests.pop(req_id, None)
                    if fut and not fut.done():
                        fut.set_result(data.get("payload", {}))
    finally:
        if connected_ws is ws:
            connected_ws = None
        print("[KimiWebBridge] Browser extension disconnected.")
    return ws

async def handle_command(request):
    global connected_ws
    if connected_ws is None or connected_ws.closed:
        return web.json_response({"ok": False, "error": {"code": "no_browser", "message": "Kimi extension not connected yet"}}, status=503)

    body = await request.json()
    action = body.get("action")
    args = body.get("args") or {}
    session = body.get("session") or "default"
    if "_session" not in args:
        args["_session"] = session

    req_id = str(uuid.uuid4())
    loop = asyncio.get_running_loop()
    fut = loop.create_future()
    pending_requests[req_id] = fut

    await connected_ws.send_json({
        "type": "tool_call",
        "requestId": req_id,
        "payload": {
            "name": action,
            "args": args
        }
    })

    try:
        res = await asyncio.wait_for(fut, timeout=45.0)
        if "error" in res and res["error"]:
            return web.json_response({"ok": False, "error": res["error"]})
        return web.json_response({"ok": True, "data": res.get("data")})
    except asyncio.TimeoutError:
        pending_requests.pop(req_id, None)
        return web.json_response({"ok": False, "error": "timeout"}, status=504)

app = web.Application(client_max_size=100 * 1024 * 1024)
app.router.add_get("/status", handle_status)
app.router.add_get("/ws", handle_ws)
app.router.add_post("/command", handle_command)

if __name__ == "__main__":
    web.run_app(app, host="127.0.0.1", port=10086, print=lambda *a: print("[KimiWebBridge] Listening on http://127.0.0.1:10086"))
