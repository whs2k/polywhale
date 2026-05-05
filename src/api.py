from flask import Flask, jsonify, send_from_directory
import os
from database import get_top_whales, get_recent_trades

app = Flask(__name__, static_folder="../frontend", static_url_path="")

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/<path:path>")
def static_files(path):
    return send_from_directory(app.static_folder, path)

@app.route("/api/whales")
def api_whales():
    # Return top 50 whales
    whales = get_top_whales(limit=50)
    # Format the data slightly to match what frontend expects
    formatted_whales = []
    for i, w in enumerate(whales):
        # We don't have true winRate yet, so we mock it based on volume or just leave it generic
        # or calculate something simple. For now, we will return the raw data and let JS format it.
        formatted_whales.append({
            "rank": i + 1,
            "address": w["wallet_address"],
            "profit": w["total_volume"] * 0.1, # Just a placeholder since we don't have resolution yet
            "winRate": 55.0 + (i % 10), # Placeholder
            "volume": w["total_volume"]
        })
    
    # Calculate some aggregate stats
    total_profit = sum(w["profit"] for w in formatted_whales)
    avg_win_rate = sum(w["winRate"] for w in formatted_whales) / len(formatted_whales) if formatted_whales else 0

    return jsonify({
        "stats": {
            "totalProfit": total_profit,
            "activeWhales": len(whales),
            "avgWinRate": avg_win_rate
        },
        "whales": formatted_whales
    })

@app.route("/api/live")
def api_live():
    trades = get_recent_trades(limit=50)
    return jsonify({
        "trades": trades
    })

@app.route("/api/logs")
def api_logs():
    import subprocess
    try:
        tracker_status = subprocess.run(["systemctl", "status", "tracker"], capture_output=True, text=True).stdout
        tracker_logs = subprocess.run(["journalctl", "-u", "tracker", "-n", "200", "--no-pager"], capture_output=True, text=True).stdout
        return f"<h3>Tracker Status</h3><pre>{tracker_status}</pre><h3>Tracker Logs</h3><pre>{tracker_logs}</pre>"
    except Exception as e:
        return str(e)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
