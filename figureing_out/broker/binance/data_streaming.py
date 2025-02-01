import websocket
import json
import threading
import time
import ssl

BINANCE_WS_URL = "wss://stream.binance.com:9443/stream?streams=btcusdt@aggTrade/btcusdt@depth"

# WebSocket message handler
def on_message(ws, message):
    data = json.loads(message)
    if 'ping' in data or 'ping' in message:
        print(data)
        print("Received ping")
        ws.send('pong')
    print(f"Received message: {data}")

# WebSocket error handler
def on_error(ws, error):
    print(f"Error: {error}")

# WebSocket close handler
def on_close(ws, close_status_code, close_msg):
    print("WebSocket closed")

def on_ping(ws, message):
    ws.send(message, opcode = websocket.ABNF.OPCODE_PONG)
# WebSocket open/connection handler
def on_open(ws):
    print("WebSocket connection opened")

def start_websocket():
    ws = websocket.WebSocketApp(
        BINANCE_WS_URL,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
        on_open=on_open,
        on_ping=on_ping
    )
    ws.run_forever()


if __name__ == "__main__":
    start_websocket()