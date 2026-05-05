import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'polywhale.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    
    # Create trades table
    c.execute('''
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            wallet_address TEXT,
            market_id TEXT,
            side TEXT,
            amount REAL,
            price REAL,
            fee_bps INTEGER DEFAULT 0
        )
    ''')
    
    # Create an index on wallet_address for faster PnL aggregation
    c.execute('CREATE INDEX IF NOT EXISTS idx_wallet ON trades(wallet_address)')
    
    # Migration: Add fee_bps if it doesn't exist
    try:
        c.execute('ALTER TABLE trades ADD COLUMN fee_bps INTEGER DEFAULT 0')
    except sqlite3.OperationalError:
        # Column already exists
        pass
    
    conn.commit()
    conn.close()

def insert_trade(wallet_address, market_id, side, amount, price, fee_bps=0):
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute('''
        INSERT INTO trades (wallet_address, market_id, side, amount, price, fee_bps)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (wallet_address, market_id, side, amount, price, fee_bps))
    
    conn.commit()
    conn.close()

def get_top_whales(limit=500):
    """
    Returns an aggregated list of whales sorted by estimated profit/volume.
    Note: A true PnL calculation requires knowing the resolution of the market.
    For this tracker, we will rank them by total volume traded as a proxy,
    or you can modify this to track actual profit once market resolutions are joined.
    """
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute('''
        SELECT 
            wallet_address, 
            COUNT(id) as trade_count,
            SUM(amount * price) as total_volume
        FROM trades
        GROUP BY wallet_address
        ORDER BY total_volume DESC
        LIMIT ?
    ''', (limit,))
    
    whales = c.fetchall()
    conn.close()
    
    return [dict(w) for w in whales]

def get_recent_trades(limit=50):
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute('''
        SELECT id, timestamp, wallet_address, market_id, side, amount, price, fee_bps
        FROM trades
        ORDER BY timestamp DESC
        LIMIT ?
    ''', (limit,))
    
    trades = c.fetchall()
    conn.close()
    
    return [dict(t) for t in trades]

if __name__ == '__main__':
    # Initialize the database if run directly
    init_db()
    print(f"Database initialized at {os.path.abspath(DB_PATH)}")
