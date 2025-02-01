from .logic import Strategy
from backtest.models import Index, Options
from .child_classes.contract import OptionContract, IndexContract
from .child_classes.candle import IndexCandle, OptionCandle
from pydantic import BaseModel
from typing import List, Union
from .db_query import query_for_backtest

class BacktestFeeds:

    contracts: List[Union[OptionContract, IndexContract]] = []
    def __init__(self, strategy: Strategy):
        self.strategy = strategy
        self.strategy.main_contract_data = query_for_backtest(self.strategy.index, self.strategy.start_time, self.strategy.end_time)
        self.strategy.main_contract = self.strategy.index
        self.strategy.children_contracts = {}
        self.strategy.children_contracts_data = {}
        self.start_feeds()

    def start_feeds(self):
        for candle in self.strategy.main_contract_data:
            if self.strategy.panic_mode:
                break

            candle_dict = candle.__dict__
            if candle_dict['symbol'] == None:
                continue

            candle = IndexCandle(**candle_dict)
            self.strategy._update_contracts(candle) #update_candles should update candles param in self.strategy.main_contract
            self.strategy.on_data()

if __name__=='__main__':
    strategy = Strategy()
    backtest_feeds = BacktestFeeds(strategy)
