from .logic import Strategy
from backtest.models import Index, Options
from .child_classes.contract import OptionContract, IndexContract
from .child_classes.candle import IndexCandle, OptionCandle
from pydantic import BaseModel
from typing import List, Union
from .db_query import query_for_backtest
from datetime import timedelta

class BacktestFeeds:

    contracts: List[Union[OptionContract, IndexContract]] = []
    def __init__(self, strategy: Strategy):
        self.strategy = strategy
        self.main_contract_data = query_for_backtest(self.strategy.index, self.strategy.start_time.date(), self.strategy.end_time.date()+ timedelta(days=1))
        self.strategy.main_contract = self.strategy.index
        self.strategy.children_contracts = {}
        self.children_contracts_data = {}
        self.strategy.feeder = self

    def start_feeds(self):
        for candle in self.main_contract_data:
            if self.strategy.panic_mode:
                break
            candle_dict = {
                'time': candle[0],
                'symbol': candle[1],
                'open': candle[2],
                'high': candle[3],
                'low': candle[4],
                'close': candle[5],
                'volume': candle[6],
                'exchange': candle[7],
                'token': candle[8],
                'candle_close': candle[9]
            }

            if candle_dict['symbol'] == None:
                continue

            self.strategy._update_contracts(candle_dict) #update_candles should update candles param in self.strategy.main_contract
            self.strategy.on_data()

if __name__=='__main__':
    strategy = Strategy()
    backtest_feeds = BacktestFeeds(strategy)
