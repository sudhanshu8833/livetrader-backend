from .lt_strategy import LTStrategy
from lt_types.backtest import OptionCandle, IndexCandle
from .child_classes.contract import OptionContract, IndexContract
from typing import Union, List
from datetime import datetime, timedelta
from lt_types import TimeFrame, LossProfitLimit, PositionSizing
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

        self._auto_block_by: List[LossProfitLimit] = {
            'pnl_limit': [
                LossProfitLimit(
                    mode = 'percentage',
                    value = 1, 
                    calculation= 'daily',
                    type = 'loss'
                ),
                LossProfitLimit(
                    mode = 'percentage',
                    value = 1,
                    calculation= 'daily',
                    type = 'profit'
                ),
                LossProfitLimit(
                    mode = 'percentage',
                    value = 5, 
                    calculation= 'monthly', 
                    type = 'profit'
                ),
                LossProfitLimit(
                    mode = 'absolute',
                    value = 1,
                    calculation= 'monthly',
                    type = 'loss'
                ),
                LossProfitLimit(
                    mode = 'percentage',
                    value = 2,
                    calculation= 'weekly',
                    type = 'profit'

                ),
                LossProfitLimit(
                    mode = 'percentage',
                    value = 1,
                    calculation= 'weekly',
                    type = 'loss'
                )
            ],
            # 'max_orders': 3,
            # 'max_positions_entry': 1
        } 

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
                position_size=50,
                order_type='MARKET',
                take_profit = 100,
                stop_loss = 50
            )