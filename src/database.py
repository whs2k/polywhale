import sqlite3
import os

DB_PATH = 'polywhale.db'

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
            price REAL
        )
    ''')
    
    # Create an index on wallet_address for faster PnL aggregation
    c.execute('CREATE INDEX IF NOT EXISTS idx_wallet ON trades(wallet_address)')
    
    conn.commit()
    conn.close()

def insert_trade(wallet_address, market_id, side, amount, price):
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute('''
        INSERT INTO trades (wallet_address, market_id, side, amount, price)
        VALUES (?, ?, ?, ?, ?)
    ''', (wallet_address, market_id, side, amount, price))
    
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

if __name__ == '__main__':
    # Initialize the database if run directly
    init_db()
    print(f"Database initialized at {os.path.abspath(DB_PATH)}")
