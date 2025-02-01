from data_provider.base_data_provider import BaseDataProvider

class BacktestDataProvider(BaseDataProvider):
    def __init__(self, broker_instance = None, logic_instance = None):
        super().__init__()

        self.broker = broker_instance
        self.logic = logic_instance
        self.data = self.broker.get_historical_data()
        self.current_index = 0

    def start_data_feed(self):
        """Iterate over backtest data and trigger the event for each new data point"""
        while self.current_index < len(self.data):
            new_data = self.data[self.current_index]
            self.current_index += 1
            self.logic.next_candle(new_data)
