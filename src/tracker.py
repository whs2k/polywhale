import os
import json
import asyncio
import websockets
import google.generativeai as genai
from database import init_db, insert_trade, get_top_whales

# --- Configuration & Setup ---
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
WS_URL = "wss://ws-subscriptions-clob.polymarket.com/ws/market"

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')

async def connect_and_listen():
    print(f"Connecting to Polymarket WebSocket at {WS_URL}...")
    
    # Example reconnection loop
    while True:
        try:
            async with websockets.connect(WS_URL) as websocket:
                print("Connected! Listening for trades...")
                
                # Note: Polymarket CLOB requires subscribing to specific markets to get their trades.
                # Since we want to track whales globally, in a full production system you would 
                # first fetch all active market IDs from the Gamma API and subscribe to them.
                # For this MVP, we will send a subscription message format. 
                # If there's a global firehose, we'd subscribe to that.
                
                # Placeholder subscription message (would need real asset_ids in production)
                subscribe_msg = {
                    "assets_ids": ["*"], # Some APIs accept wildcard, otherwise provide specific IDs
                    "type": "market"
                }
                # await websocket.send(json.dumps(subscribe_msg))

                while True:
                    message = await websocket.recv()
                    data = json.loads(message)
                    
                    # Example payload parsing (Adjust according to actual Polymarket CLOB schema)
                    if isinstance(data, list):
                        for event in data:
                            if event.get('event_type') == 'last_trade_price':
                                handle_trade(event)
                    elif data.get('event_type') == 'last_trade_price':
                        handle_trade(data)
                        
                    # For testing, just print the raw messages if we get any
                    print("Received data:", data)
                    
        except websockets.exceptions.ConnectionClosed as e:
            print(f"WebSocket closed: {e}. Reconnecting in 5 seconds...")
            await asyncio.sleep(5)
        except Exception as e:
            print(f"Unexpected error: {e}. Reconnecting in 5 seconds...")
            await asyncio.sleep(5)

def handle_trade(event):
    """Parses a trade event and inserts it into the SQLite DB."""
    # These fields depend on the exact JSON schema Polymarket returns via WS
    wallet = event.get('maker_address') or event.get('taker_address') or "UnknownWallet"
    market_id = event.get('asset_id') or "UnknownMarket"
    side = event.get('side', 'BUY')
    
    # Amount is often in shares or USDC, price is the odds
    amount = float(event.get('size', 0))
    price = float(event.get('price', 0))
    
    if wallet and amount > 0:
        insert_trade(wallet, market_id, side, amount, price)
        print(f"Logged trade: Wallet {wallet[:6]}... bought {amount} shares at {price} on {market_id}")

def analyze_whales():
    """ Periodically analyze the database to find the biggest whales. """
    print("\n--- Current Top Whales (by Volume) ---")
    whales = get_top_whales(limit=5)
    for w in whales:
        print(f"Wallet: {w['wallet_address']} | Trades: {w['trade_count']} | Vol: ${w['total_volume']:.2f}")
    print("--------------------------------------\n")

async def background_analyzer():
    while True:
        await asyncio.sleep(60) # Run every 60 seconds
        analyze_whales()

async def main():
    # Ensure database is initialized
    init_db()
    
    # Run the websocket listener and the analyzer concurrently
    await asyncio.gather(
        connect_and_listen(),
        background_analyzer()
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Stopping PolyWhale tracker...")