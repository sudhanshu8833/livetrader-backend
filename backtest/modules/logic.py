from .lt_strategy import LTStrategy
from lt_types.backtest import OptionCandle, IndexCandle
from .child_classes.contract import OptionContract, IndexContract
from typing import Union, List
from datetime import datetime, timedelta
from lt_types import TimeFrame
from datetime import time
class Strategy(LTStrategy):
    def __init__(self):
        self.initial_cash = 10000000
        self.start_time = datetime.now() - timedelta(days = 365)
        self.end_time = self.start_time + timedelta(days = 90)
        self.index = IndexContract(
            strategy = self,
            symbol = 'NIFTY',
            exchange = 'NSE',
            time_frame = TimeFrame.MINUTE_5,
            is_master = True
        )
        super().__init__() 

    def on_data(self):
        if not self.is_position_opened() and self.time.time() > time(10,30):
            atm = self.index.get_atm()
            self.pe_buy = self.get_contract(
                symbol = self.index.symbol,
                strike_price=atm,
                option_type='PE',
                expiration_date=self.index.current_expiry()
            )
            self.pe_buy.enter(
                side = 'BUY',
                quantity=50,
                order_type='MARKET',
                take_profit = 100,
                stop_loss = 50
            )


'''
asset_type, is a fundamental knowledge, 
and since later we are going to be adding, crypto and forex,
therefore this distinctions, are really crucial to be made
assettype -> index, option, crypto, forex
for each asset_type, exchange can be different
each asset type will have different candle class, 
and different contract class
but for now, positions, orders, and trades are a common class, shared by anyone, maybe later will also have to change this, 
explain me some reasons why we might have to do it
'''