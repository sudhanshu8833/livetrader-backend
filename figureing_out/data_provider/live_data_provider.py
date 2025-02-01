from data_provider.base_data_provider import BaseDataProvider

class LiveDataProvider(BaseDataProvider):
    def __init__(self, broker_instance = None, logic_instance = None):
        super().__init__()

        self.broker = broker_instance
        self.logic = logic_instance
        self.data = self.broker.get_historical_data()
        self.current_index = 0

    def start_data_feed(self):
        if self.broker.KLINE_STREAM:
            self.broker.subscribe_to_kline_stream(callback = self.logic.next_candle)
        else:
            pass
