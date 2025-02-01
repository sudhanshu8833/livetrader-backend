from data_provider import BaseDataProvider, LiveDataProvider, BacktestDataProvider
from broker import BinanceBroker
import dotenv
import os
dotenv.load_dotenv()

class LiveTrader:
    def __init__(self):
        self.current_position = None

    def next_candle(self, kline):
        print(f"New kline received: {kline}")

if __name__ == "__main__":
    data_provider_broker = BinanceBroker(os.getenv("BINANCE_API_KEY"), os.getenv("BINANCE_API_SECRET"))
    logic_class_instance = LiveTrader()
    # data_provider_instance = BacktestDataProvider(broker_instance = data_provider_broker, logic_instance = logic_class_instance)
    data_provider_instance = LiveDataProvider(broker_instance = data_provider_broker, logic_instance = logic_class_instance)
    data_provider_instance.start_data_feed()