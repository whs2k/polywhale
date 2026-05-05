import requests
import json

try:
    res = requests.get('https://gamma-api.polymarket.com/events?active=true&limit=1')
    data = res.json()
    markets = data[0].get('markets', [])
    for m in markets:
        print("Tokens:", m.get('clobTokenIds'))
except Exception as e:
    print("Error:", e)
