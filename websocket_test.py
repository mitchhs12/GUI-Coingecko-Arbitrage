import websockets
import asyncio


async def listen():
    url = "ws://simple-websocket-server-echo.glitch.me/"

    async with websockets.connect(url) as ws:
        msg = await ws.recv()
        print(msg)


asyncio.get_event_loop().run_until_complete(listen())
