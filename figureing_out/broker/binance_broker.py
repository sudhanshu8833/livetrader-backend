import time
from broker.base_broker import BaseBroker
import dotenv
import os
import logging
dotenv.load_dotenv()
logging.basicConfig(
    level=logging.INFO,  # Set the logging level
    format='%(asctime)s - %(levelname)s - %(message)s',  # Set the logging format
    handlers=[
        logging.FileHandler("app.log"),  # Log to a file
        logging.StreamHandler()  # Log to the console
    ]
)
from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager

def testing(depth_cache):
    print(f"symbol {depth_cache.symbol}")
    print("top 5 bids")
    print(depth_cache.get_bids()[:5])
    print("top 5 asks")
    print(depth_cache.get_asks()[:5])
    print("last update time {}".format(depth_cache.update_time))


class BinanceBroker(BaseBroker):
    KLINE_STREAM = False
    def __init__(self, api_key, api_secret):
        super().__init__()
        try:
            self.client = Client(api_key, api_secret)
        except:
            raise ValueError("Invalid API key or secret")

    def get_historical_data(self, symbol = 'BTCUSDT', interval='1h', start_time=None, end_time=None):
        if start_time is None:
            start_time = int(time.time() * 1000) - 86400000
        if end_time is None:
            end_time = int(time.time() * 1000)
        return self.client.get_historical_klines(symbol, interval, start_time, end_time)

    def get_live_data(self, symbol):
        return self.client.get_orderbook_ticker(symbol)

    def _get_headers(self):
        return {}

    def get_account_info(self):
        return None

    def place_order(self, symbol, side, quantity, price=None):
        return None

    def get_order_status(self, order_id, symbol):
        return None

    def get_live_positions(self):
        return None

    def subscribe_to_kline_stream(self, symbol='BTCUSDT', interval='1m', callback=None):
        self.twm = ThreadedWebsocketManager(api_key=os.getenv("BINANCE_API_KEY"), api_secret=os.getenv("BINANCE_SECRET_KEY"))
        self.twm.start()
        self.twm.start_kline_socket(callback=testing, symbol=symbol, interval=interval)

    def subscribe_to_depth_stream(self, symbol='BTCUSDT', callback=None):
        self.dcm = ThreadedDepthCacheManager(api_key=os.getenv("BINANCE_API_KEY"), api_secret=os.getenv("BINANCE_SECRET_KEY"))
        self.dcm.start()
        self.dcm.start_depth_cache(callback=testing, symbol=symbol)

    def stop_websockets(self):
        self.twm.stop()

if __name__ == "__main__":
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_SECRET_KEY")
    
    broker = BinanceBroker(api_key, api_secret)
    
    symbol = "BTCUSDT"
    interval = "1h"
    start_time = int(time.time() * 1000) - 86400000
    end_time = int(time.time() * 1000)
    historical_data = broker.get_historical_data(symbol, interval, start_time, end_time)
    print("Historical Data:", historical_data)