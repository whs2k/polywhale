import os
import json
import asyncio
import websockets
import requests
import time
import random
from database import init_db, insert_trade

# --- Configuration ---
WS_URL = "wss://ws-subscriptions-clob.polymarket.com/ws/market"
GAMMA_API = "https://gamma-api.polymarket.com"

# Simulated whale names
WHALE_NAMES = ["BlueWhale", "Humpback", "Narwhal", "Orca", "Beluga", "SpermWhale", "FinWhale", "Minke"]

async def get_active_markets():
    """Fetch active markets from Gamma API for simulation/tracking."""
    try:
        res = requests.get(f"{GAMMA_API}/events?active=true&limit=20")
        events = res.json()
        markets = []
        for event in events:
            for market in event.get('markets', []):
                ids = market.get('clobTokenIds')
                if isinstance(ids, str):
                    try: ids = json.loads(ids)
                    except: continue
                if isinstance(ids, list) and ids:
                    markets.append({
                        "id": ids[0], # Just use the first token for simplicity
                        "question": market.get('question', 'Unknown Market')
                    })
        return markets
    except Exception as e:
        print(f"Error fetching markets: {e}")
        return []

async def simulate_trades():
    """Simulate trades for real markets to ensure the UI is alive while debugging WS."""
    print("Starting simulated trade generator...")
    while True:
        try:
            markets = await get_active_markets()
            if markets:
                # Create a simulated trade every 20-40 seconds
                market = random.choice(markets)
                wallet = random.choice(WHALE_NAMES) + "_" + str(random.randint(100, 999))
                side = random.choice(["BUY", "SELL"])
                amount = random.uniform(1000, 50000) # Big "Whale" trades
                price = random.uniform(0.1, 0.9)
                
                insert_trade(wallet, market["question"], side, amount, price)
                print(f"[SIM] Trade: {wallet} {side} {amount:.2f} shares on '{market['question'][:30]}...'")
            
            await asyncio.sleep(random.randint(20, 40))
        except Exception as e:
            print(f"Simulation error: {e}")
            await asyncio.sleep(10)

async def connect_and_listen():
    """Real WebSocket listener (work in progress)."""
    print(f"Connecting to {WS_URL}...")
    while True:
        try:
            tokens = [m["id"] for m in await get_active_markets()]
            if not tokens:
                await asyncio.sleep(10)
                continue
                
            async with websockets.connect(WS_URL, ping_interval=10, ping_timeout=10) as websocket:
                await websocket.send(json.dumps({"type": "market", "assets_ids": tokens[:50]}))
                print(f"Subscribed to {len(tokens[:50])} tokens.")
                
                async for message in websocket:
                    if message == "PONG": continue
                    try:
                        data = json.loads(message)
                        events = data if isinstance(data, list) else [data]
                        for event in events:
                            if event.get('event_type') == 'last_trade_price':
                                # Handle real trade if it appears
                                handle_real_trade(event)
                    except: continue
        except Exception as e:
            print(f"WS Error: {e}. Reconnecting...")
            await asyncio.sleep(5)

def handle_real_trade(event):
    """Parses real trade event."""
    asset_id = event.get('asset_id')
    price = float(event.get('price', 0))
    size = float(event.get('size', 0))
    side = event.get('side', 'BUY')
    wallet = event.get('maker_address') or "RealWhale_Anon"
    insert_trade(wallet, asset_id, side, size, price)
    print(f"[REAL] Trade captured on {asset_id}!")

async def main():
    print("PolyWhale tracker starting up...")
    init_db()
    # Run both real and simulated tracking
    await asyncio.gather(
        connect_and_listen(),
        simulate_trades()
    )

if __name__ == "__main__":
    asyncio.run(main())