import requests
import hmac
import hashlib
import time
import json
from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager


BASE_URL = 'https://api.binance.com'

HEADERS = {
    'X-MBX-APIKEY': 'txcBeyOztLYTy3or6l1Hdya9TCpZhK5AQ7FF0rk1mrxqE8xCr2ml8j9wFVKXIj3G',
    # 'content-type': 'application/x-www-form-urlencoded'
}
SECRET_KEY = 'bzloGwx1kZ6A5WT3pUpz3hAGMxigWL9Tmd9AFdPHnzJVichOg8BM5rKrdtAB14OU'

PAYLOAD = {
    # 'symbol': 'BTCUSDT',
    # 'side': 'BUY',
    # 'type': 'LIMIT',
    # 'timeInForce': 'GTC',
    # 'quantity': 0.01,
    # 'price': 30000,
    'recvWindow': 5000,
    'timestamp': int(time.time() * 1000)
}

def get_signature(payload):
    return hmac.new(SECRET_KEY.encode('utf-8'),payload.encode('utf-8'),hashlib.sha256).hexdigest()

def get_data(payload, endpoint):
    # Convert payload to query string
    query_string = '&'.join([f"{key}={value}" for key, value in payload.items()])
    # Generate signature
    signature = get_signature(query_string)
    # Append signature to query string
    query_string += f"&signature={signature}"
    # Make the request
    response = requests.get(f"{BASE_URL}{endpoint}?{query_string}", headers=HEADERS)
    return response

print(get_data(PAYLOAD, '/api/v3/account').json())

# from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
# client = Client('txcBeyOztLYTy3or6l1Hdya9TCpZhK5AQ7FF0rk1mrxqE8xCr2ml8j9wFVKXIj3G', 'bzloGwx1kZ6A5WT3pUpz3hAGMxigWL9Tmd9AFdPHnzJVichOg8BM5rKrdtAB14OU')

# # get market depth
# depth = client.get_account()
# print(depth)