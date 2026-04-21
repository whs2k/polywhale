import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import google.generativeai as genai

# --- Configuration & Setup ---
STATE_FILE = 'state.json'
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
GMAIL_ADDRESS = os.environ.get('GMAIL_ADDRESS')
GMAIL_APP_PASSWORD = os.environ.get('GMAIL_APP_PASSWORD')
ALERT_RECIPIENT = os.environ.get('ALERT_RECIPIENT')

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {"last_processed_tx": None, "daily_email_sent": False}

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=4)

def fetch_top_whales():
    # TODO: Implement Polymarket Gamma API call to fetch leaderboard wallets
    # Example placeholder return:
    return ["0xWhaleWallet1", "0xWhaleWallet2"]

def fetch_recent_bets(whale_addresses, last_tx):
    # TODO: Query Polymarket/Polygon for recent transactions by these wallets
    # Filter out anything older than last_tx to avoid duplicate processing
    
    # Placeholder mock data
    mock_bets = [
        {"wallet": "0xWhaleWallet1", "market": "Will interest rates drop?", "side": "Yes", "amount": 50000},
        {"wallet": "0xWhaleWallet2", "market": "Will the sun rise?", "side": "No", "amount": 1000}
    ]
    return mock_bets

def analyze_bets_with_gemini(bets):
    """Uses Gemini to pick the single most important bet of the day."""
    if not bets:
        return None
        
    prompt = f"""
    You are a quantitative analyst. Review the following recent trades by highly profitable accounts on Polymarket.
    Identify the SINGLE most significant bet based on size and market context. 
    Write a brief, punchy email alert summarizing this bet and why it matters.
    
    Trades: {json.dumps(bets)}
    """
    
    response = model.generate_content(prompt)
    return response.text

def send_email_alert(content):
    msg = MIMEMultipart()
    msg['From'] = GMAIL_ADDRESS
    msg['To'] = ALERT_RECIPIENT
    msg['Subject'] = "🐋 Smart Money Alert: Polymarket Whale Activity"

    msg.attach(MIMEText(content, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        server.send_message(msg)
        server.quit()
        print("Alert sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")

def main():
    state = load_state()
    
    print("Fetching whale wallets...")
    whales = fetch_top_whales()
    
    print("Scanning for new bets...")
    recent_bets = fetch_recent_bets(whales, state.get("last_processed_tx"))
    
    if recent_bets:
        print("Analyzing bets with Gemini...")
        alert_content = analyze_bets_with_gemini(recent_bets)
        
        if alert_content:
            send_email_alert(alert_content)
            
            # Update state so we don't alert on these again
            state["last_processed_tx"] = "UPDATED_TX_HASH" # Replace with actual logic
            state["daily_email_sent"] = True
            save_state(state)
    else:
        print("No new whale bets found.")

if __name__ == "__main__":
    main()