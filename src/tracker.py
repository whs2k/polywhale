import os
import json
import asyncio
import websockets
import requests
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
    
    while True:
        try:
            async with websockets.connect(WS_URL) as websocket:
                print("Connected! Listening for trades...")
                
                # 1. Fetch active markets from Gamma API
                print("Fetching active markets...")
                res = requests.get('https://gamma-api.polymarket.com/events?active=true&limit=50')
                active_events = res.json()
                # Hardcoded active tokens for testing (BTC Up/Down)
                token_ids = [
                    "68178860044558509376672322612710178351545648802953282218000455850937667232261", # BTC Up
                    "57321561048821612594626385532706912750332728571942532289631379312455583992563"  # BTC Down (Examples)
                ]
                
                # 2. Subscribe
                subscribe_msg = {
                    "assets_ids": token_ids, 
                    "type": "market"
                }
                await websocket.send(json.dumps(subscribe_msg))
                print(f"Subscribed to test tokens: {token_ids}")

                # 4. Message loop
                while True:
                    message = await websocket.recv()
                    print(f"RAW MSG: {message}") # Log everything raw
                    if message == "PONG":
                        continue
                        
                    try:
                        data = json.loads(message)
                    except json.JSONDecodeError:
                        print(f"Non-JSON message received: {message}")
                        continue
                    
                    # Log ALL messages for debugging
                    print(f"WS Msg: {json.dumps(data)[:200]}...") # Print first 200 chars

                    events = data if isinstance(data, list) else [data]
                    for event in events:
                        etype = event.get('event_type') or event.get('type')
                        if etype == 'last_trade_price' or etype == 'trade':
                            handle_trade(event)
                        elif etype == 'price_change':
                            # Maybe we can extract trade info from price changes if needed
                            pass
                        
        except Exception as e:
            print(f"Connection error: {e}. Reconnecting in 5 seconds...")
            await asyncio.sleep(5)

def handle_trade(event):
    """Parses a trade event and inserts it into the SQLite DB."""
    print("Parsing trade event:", json.dumps(event))
    # Try all possible fields for wallet address
    wallet = (event.get('maker_address') or event.get('taker_address') or 
              event.get('address') or event.get('wallet') or 
              event.get('owner') or event.get('from') or "UnknownWallet")
    market_id = event.get('asset_id') or "UnknownMarket"
    side = event.get('side', 'BUY')
    
    # Amount is often in shares or USDC, price is the odds
    amount = float(event.get('size', 0))
    price = float(event.get('price', 0))
    
    print(f"Checking trade: Wallet={wallet}, Amount={amount}, Price={price}")
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
    print("PolyWhale tracker starting up...")
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