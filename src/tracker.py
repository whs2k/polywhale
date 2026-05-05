import os
import json
import asyncio
import websockets
import requests
import time
from database import init_db, insert_trade

# --- Configuration ---
WS_URL = "wss://ws-subscriptions-clob.polymarket.com/ws/market"
GAMMA_API = "https://gamma-api.polymarket.com"

async def get_active_tokens():
    """Fetch active tokens from Gamma API."""
    try:
        # Fetch top active events
        res = requests.get(f"{GAMMA_API}/events?active=true&limit=20")
        events = res.json()
        token_ids = []
        for event in events:
            for market in event.get('markets', []):
                ids = market.get('clobTokenIds')
                if isinstance(ids, str):
                    try:
                        ids = json.loads(ids)
                    except: continue
                if isinstance(ids, list):
                    token_ids.extend(ids)
        return list(set(token_ids))[:100] # Unique top 100
    except Exception as e:
        print(f"Error fetching tokens: {e}")
        return []

async def connect_and_listen():
    print("PolyWhale tracker starting up...")
    init_db()
    
    while True:
        try:
            tokens = await get_active_tokens()
            if not tokens:
                print("No active tokens found. Retrying in 10s...")
                await asyncio.sleep(10)
                continue
                
            print(f"Connecting to {WS_URL} and subscribing to {len(tokens)} tokens...")
            
            async with websockets.connect(WS_URL, ping_interval=10, ping_timeout=10) as websocket:
                # Subscription message
                sub_msg = {
                    "type": "market",
                    "assets_ids": tokens,
                    "custom_feature_enabled": True
                }
                await websocket.send(json.dumps(sub_msg))
                print("Subscribed! Waiting for events...")

                while True:
                    try:
                        message = await websocket.recv()
                        if not message: continue
                        
                        # Polymarket sometimes sends plain strings or heartbeats
                        if message == "PONG": continue
                        
                        try:
                            data = json.loads(message)
                        except:
                            if "INVALID" not in message:
                                print(f"Raw Msg: {message}")
                            continue

                        # Handle both single events and lists
                        events = data if isinstance(data, list) else [data]
                        for event in events:
                            etype = event.get('event_type')
                            if etype == 'last_trade_price':
                                handle_trade(event)
                            elif etype and etype != 'new_market':
                                # Log other interesting events like price_change occasionally
                                if time.time() % 60 < 1: # Log once a minute
                                    print(f"Periodic log ({etype}): {json.dumps(event)[:100]}...")

                    except websockets.exceptions.ConnectionClosed:
                        print("WebSocket closed. Reconnecting...")
                        break
        except Exception as e:
            print(f"Tracker error: {e}. Reconnecting in 5s...")
            await asyncio.sleep(5)

def handle_trade(event):
    """Parses trade event and saves to DB."""
    try:
        # Extract fields
        asset_id = event.get('asset_id')
        price = float(event.get('price', 0))
        size = float(event.get('size', 0))
        side = event.get('side', 'BUY')
        
        # Address is often NOT in the public feed, use a placeholder if missing
        # But check all possible fields just in case
        wallet = (event.get('maker_address') or event.get('taker_address') or 
                  event.get('address') or "AnonymousWhale")
        
        if size > 0:
            insert_trade(wallet, asset_id, side, size, price)
            print(f">>> TRADE: {wallet[:8]}... {side} {size} shares at {price} on {asset_id}")
    except Exception as e:
        print(f"Error handling trade: {e}")

if __name__ == "__main__":
    asyncio.run(connect_and_listen())