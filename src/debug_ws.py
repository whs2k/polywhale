import os, json, asyncio, websockets

async def test_ws():
    uri = "wss://ws-subscriptions-clob.polymarket.com/ws/market"
    print(f"Connecting to {uri}...")
    async with websockets.connect(uri) as websocket:
        # Subscribe to EVERYTHING
        await websocket.send(json.dumps({"type": "market", "assets_ids": []}))
        print("Subscribed to global feed. Logging for 60s...")
        
        start_time = asyncio.get_event_loop().time()
        while asyncio.get_event_loop().time() - start_time < 60:
            try:
                msg = await asyncio.wait_for(websocket.recv(), timeout=10)
                data = json.loads(msg)
                # Print only first 100 chars to avoid flooding
                print(f"MSG: {json.dumps(data)[:100]}")
            except asyncio.TimeoutError:
                print("Timeout - no message for 10s")
            except Exception as e:
                print(f"Error: {e}")
                break

if __name__ == "__main__":
    asyncio.run(test_ws())
