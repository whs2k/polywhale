import asyncio
import websockets
import json
import requests

async def test_ws():
    WS_URL = "wss://ws-subscriptions-clob.polymarket.com/ws/market"
    try:
        res = requests.get('https://gamma-api.polymarket.com/events?active=true&limit=2')
        active_events = res.json()
        token_ids = []
        for event in active_events:
            for market in event.get('markets', []):
                token_ids.extend(market.get('clobTokenIds', []))
                
        async with websockets.connect(WS_URL) as websocket:
            print("Connected")
            msg = {
                "assets_ids": token_ids,
                "type": "market"
            }
            await websocket.send(json.dumps(msg))
            print("Sent sub for", len(token_ids), "tokens")
            for _ in range(5):
                res = await websocket.recv()
                print("Recv:", res[:200])
    except Exception as e:
        print("Error:", e)

asyncio.run(test_ws())
