import requests
import hmac
import hashlib
import websocket
import ccxt


BASE_URL = 'https://api.binance.com'

HEADERS = {
    'X-MBX-APIKEY': 'txcBeyOztLYTy3or6l1Hdya9TCpZhK5AQ7FF0rk1mrxqE8xCr2ml8j9wFVKXIj3G',
    # 'content-type': 'application/x-www-form-urlencoded'
}
SECRET_KEY = 'bzloGwx1kZ6A5WT3pUpz3hAGMxigWL9Tmd9AFdPHnzJVichOg8BM5rKrdtAB14OU'

def get_signature(payload):
    return hmac.new(SECRET_KEY.encode('utf-8'),payload.encode('utf-8'),hashlib.sha256).hexdigest()

def create_listen_key():
    response = requests.post(f"{BASE_URL}/api/v3/userDataStream", headers=HEADERS)
    return response.json()

listen_key = create_listen_key()
print(listen_key)

WS_USER_STREAM = f'wss://stream.binance.com:9443/ws/{listen_key["listenKey"]}'


def on_message(ws, message):
    print(message)

def on_error(ws, error):
    print(error)

def on_close(ws):
    print("closed")

def on_open(ws):
    print("opened")

def start_websocket():
    ws = websocket.WebSocketApp(
        WS_USER_STREAM,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
        on_open=on_open
    )
    ws.run_forever()

if __name__ == "__main__":
    start_websocket()