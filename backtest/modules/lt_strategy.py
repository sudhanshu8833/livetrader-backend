from pydantic import Field
from typing import Union,  List, Dict, Optional, Literal
from sortedcontainers import SortedDict
from backtest.modules.child_classes.candle import IndexCandle, OptionCandle
from backtest.modules.child_classes.contract import IndexContract, OptionContract, ContractStatus
from .db_query import query_for_backtest
from datetime import timedelta, date, datetime, time
import warnings
import time as time_now
import sys
from backtest.serialize import BaseSerializer

class LTStrategy(BaseSerializer):
    _serialize = [
        'expired_contracts',
        'current_portfolio',
        'realised_pnl_map',
        'time_taken',
        'children_contracts',
        'start_time',
        'end_time',
        'initial_cash',
        'main_contract',
    ]

    def __init__(self):
        self.time = self.start_time
        self.children_contracts: Dict[str, Union[IndexContract, OptionContract]] = {}
        self.expired_contracts:  List[Union[IndexContract, OptionContract]] = []
        self.current_portfolio = self.initial_cash
        self.realised_pnl_map = SortedDict()
        self.time_taken = 0
        self._block_ = False
        self.block_till = None
        self.panic_mode = False
        self.brokerage_per_order: Dict = Field({'mode':'absolute','value':10}, description="By default Brokerrage is per order, other wise you can define a custom brokerage according to percentage")
        # self.brokerage_per_order = {'mode': 'percentage', 'value': 0.01}

    def __getattr__(self, name):
        if name == 'time':
            return self.time.time()
        if name == 'date':
            return self.time.date()
        return False

    def _update_contracts(self, candle: Union[IndexCandle, OptionCandle]):
        if self._block_:
            if self.time > self.block_till:
                self.unblock()
        self.index._update_candles(candle)
        self.time = candle.time
        for key, contract in self.children_contracts.items():
            if contract.status == ContractStatus.ACTIVE:
                children_candle = self.children_contracts_data.get(contract, {}).get(candle.time)
                if children_candle:
                    contract._update_candles(children_candle)
                    contract._update_positions()
                else:
                    if self.time.date() > contract.expiration_date:
                        contract.expire_contract()
                        contract.remove_candles()
                        self.expired_contracts.append(contract)
                        self.children_contracts.pop(key)
                        self.children_contracts_data.pop(contract)
                        return
                    print("Data not found for children contracts")
        self._auto_block()

    def is_position_opened(self) -> bool:
        for item in self.children_contracts.values():
            if item.has_opened_position():
                return True
        return False

    def close_all_positions(self):
        for item in self.children_contracts.values():
            item.exit()

    def get_opened_opened(self) -> List[Union[OptionContract, IndexContract]]:
        return [item.get_active_position() for item in self.children_contracts.values() if item.has_opened_position()]

    def get_contract(self,
                            symbol: str,
                            expiration_date: str = None,
                            strike_price: float = None,
                            option_type: str = None,
                            time_frame: str = None,
                            asset_type: str = 'options',
                            exchange: str = None,
                            ) -> Union[OptionContract, IndexContract]:

        if asset_type == 'options':
            contract = OptionContract(
                strategy = self,
                symbol = symbol,
                exchange = exchange if exchange else self.index.exchange,
                expiration_date = expiration_date,
                strike_price = strike_price,
                option_type = option_type,
                time_frame = time_frame if time_frame else self.index.time_frame
            )
            if str(contract) not in self.children_contracts:
                self.children_contracts[str(contract)] = contract
                time1 = time_now.time()
                self.children_contracts_data[contract] = {
                    row.time: row for row in query_for_backtest(contract, self.time.date() - timedelta(days=1), min(self.end_time.date(), contract.expiration_date) + timedelta(days=1))
                }
                print(self.time_taken + (time_now.time() - time1))
                self.time_taken += (time_now.time() - time1)
            else:
                contract = self.children_contracts[str(contract)]
                contract.candles = []

        else:
            contract = IndexContract(
                symbol = symbol,
                time_frame = time_frame if time_frame else self.index.time_frame
            )
            if str(contract) not in self.children_contracts:
                self.children_contracts[str(contract)] = contract
                self.children_contracts_data[contract] = {
                    row.timestamp: row for row in query_for_backtest(contract, self.time.date() - timedelta(days=3), self.end_time)
                }
            else:
                contract = self.children_contracts[str(contract)]
                contract.candles = []

        children_candle = self.children_contracts_data.get(contract, {}).get(self.time)
        if children_candle:
            try:
                contract._update_candles(children_candle)
            except Exception as e:
                print(str(e))
        else:
            if self.time.time() > time(15, 30) or self.time.time() < time(9, 15):
                return contract
            raise Exception(f'Data not found for children contracts {contract}: {self.time}')
        return contract

    def get_pnl_for_date_range(self, start_date: date, end_date: date) -> float:
        pnl_values = self.realised_pnl_map.irange(start_date, end_date, inclusive=(True, True))
        return sum(self.realised_pnl_map[d] for d in pnl_values)

    def get_todays_pnl(self):
        return self.realised_pnl_map.get(self.time.date(), 0) + self.get_unrealised_pnl()

    def get_weeks_pnl(self):
        return self.get_pnl_for_date_range(self.time.date() - timedelta(days=self.time.weekday()), self.time.date())

    def get_months_pnl(self):
        return self.get_pnl_for_date_range(self.time.date().replace(day=1), self.time.date())

    def get_years_pnl(self):
        return self.get_pnl_for_date_range(self.time.date().replace(month=1, day=1), self.time.date())

    def _update_realised_pnl(self, pnl):
        if self.time.date() not in self.realised_pnl_map:
            self.realised_pnl_map[self.time.date()] = pnl
        else:
            self.realised_pnl_map[self.time.date()] += pnl

    def _auto_block(self):
        todays_pnl = self.get_todays_pnl()
        months_pnl = self.get_months_pnl()
        weeks_pnl = self.get_weeks_pnl()

        CONDITIONS = {
            'daily': {
                'percentage': (todays_pnl / (todays_pnl + self.current_portfolio)) * 100,
                'absolute': todays_pnl
            },
            'monthly': {
                'percentage': (months_pnl / (months_pnl + self.current_portfolio)) * 100,
                'absolute': months_pnl
            },
            'weekly': {
                'percentage': (weeks_pnl / (weeks_pnl + self.current_portfolio)) * 100,
                'absolute': weeks_pnl
            }
        }

        for value in self._auto_block_by['pnl_limit']:
            pnl = CONDITIONS[value.calculation][value.mode]
            if value.type == 'loss':
                if pnl < value.value:
                    self._block_for(value.calculation)
            if value.type == 'profit':
                if pnl > value.value:
                    self._block_for(value.calculation)

    def get_unrealised_pnl(self):
        unrealised_pnl = 0
        for item in self.children_contracts.values():
            unrealised_pnl += item.get_unrealised_pnl()
        return unrealised_pnl

    def _get_pnl(self, date: date):
        return self.realised_pnl_map.get(date, 0)


    def distance_from_expiry(self, expiry: date, days: int = True, hours: int = False, minutes: int = False) -> int:
        if days:
            return (expiry - self.time.date()).days

        expiry_time = datetime.combine(expiry, time(15, 30))
        if hours:
            return (expiry_time - self.time).total_seconds() // 3600
        if minutes:
            return (expiry_time - self.time).total_seconds() // 60
        return (expiry_time - self.time).total_seconds()

    def cancel_all_pending_orders(self):
        for item in self.children_contracts.values():
            item.cancel_all_pending_orders()

    def _block(self, block_time: datetime) -> datetime:
        if self._block_:
            self.block_till = max(self.block_till, block_time)
            return
        self._block_ = True
        self.block_till = block_time
        return self.block_till

    def _block_for(self, type: Literal['daily','weekly','monthly']) -> datetime:
        if type == 'daily':
            return self.block_for_day()
        if type == 'weekly':
            return self.block_for_week()
        if type == 'monthly':
            return self.block_for_month() 

    def block_for_day(self) -> datetime:
        return self._block(datetime.combine(self.time.date(), time(0, 0)) + timedelta(days=1))

    def block(self, block_time: Optional[Union[datetime, date]]) -> datetime:
        if isinstance(block_time, date):
            block_time = datetime.combine(block_time, time(0, 0)) + timedelta(days=1)
        if block_time:
            return self._block(block_time)
        else:
            return self._block(self.end_time + timedelta(days=1))

    def block_for_week(self):
        return self._block(datetime.combine(self.time.date(), time(0, 0)) + timedelta(days=7 - self.time.weekday()))

    def block_for_month(self) -> datetime:
        next_month = self.time.replace(month = self.time.month + 1, day = 1)
        block_till = datetime.combine(next_month.date(), time(0, 0))
        return self._block(block_till)

    def unblock(self):
        self._block_ = False
        self.block_till = None

    def panic_button(self):
        self.cancel_all_pending_orders()
        self.close_all_positions()
        self.panic_mode = True

    def update_portfolio(self, amount: float):
        self.current_portfolio += amount
    

