from pydantic import BaseModel, Field
from .candle import IndexCandle, OptionCandle
from datetime import date, time
from typing import List, Literal, Union, Callable, Any, Optional, ClassVar
from lt_types import TimeFrame, OptionType
from enum import Enum
from datetime import datetime
from .position import OptionPosition, PositionStatus
from LIVE_TRADER.config import STATIC_DATA_INDEX
from lt_types.index import IndexStaticData
from backtest.serialize import BaseSerializer

class ContractStatus(Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    EXPIRED = "EXPIRED"


class Contract(BaseModel, BaseSerializer):
    strategy: Any
    is_master: bool = False
    symbol: str
    exchange: str
    time_frame: TimeFrame = TimeFrame.MINUTE_1
    ltp: float = None
    time: datetime = None
    previous_ltp: float = None
    status: ContractStatus = ContractStatus.INACTIVE
    pnl: float = 0 

    _serialize: ClassVar[list[str]] = [
        'symbol',
        'exchange',
        'time_frame',
        'status',
        'is_master',
        'ltp',
        'pnl',
    ]

    def get_candle(self, attribute: str, index: int = 0):
        if index >= len(self.candles):
            return None
        return getattr(self.candles[-1 * index - 1], attribute)

    def _update_candles(self, candle: Union[IndexCandle, OptionCandle]):
        self.ltp = float(candle.close or self.ltp or candle.open)
        self.time = candle.time
        if not self.candles:
            self.candles.append(candle)
        else:
            if self.candles[-1].candle_close:
                self.candles.append(candle)
            else:

                    self.candles[-1].open = float(candle.open or self.ltp)
                    self.candles[-1].high = float(candle.high  or self.ltp)
                    self.candles[-1].low = float(candle.low or self.ltp)
                    self.candles[-1].close = float(candle.close or self.ltp)
                    self.candles[-1].candle_close = candle.candle_close

                    if isinstance(candle, OptionCandle):
                        self.candles[-1].volume = int(candle.volume)
                        self.candles[-1].oi = int(candle.oi or self.candles[-1].oi)

    def has_contract_expired(self):
        return self.status == ContractStatus.EXPIRED

    def has_opened_position(self):
        return self.status == ContractStatus.ACTIVE

    def expire_contract(self):
        self.exit(exit_percentage = 100)
        self.status = ContractStatus.EXPIRED
    
    def remove_candles(self):
        self.candles = []

    def get_active_position(self):
        return self.positions.active
    
    def active_position_closed(self):
        self.pnl += self.positions.active.realized_pnl
        self.positions.closed.append(self.positions.active)
        self.positions.active = None
        self.status = ContractStatus.INACTIVE

    def get_unrealised_pnl(self):
        if self.positions.active:
            return self.positions.active.unrealized_pnl
        return 0

    def get_realised_pnl(self):
        if self.position.active:
            return self.pnl + self.positions.active.realized_pnl
        else:
            return self.pnl

class PositionByStatus(BaseModel, BaseSerializer):
    active: Optional[OptionPosition] = None
    closed: List[OptionPosition] = []

    _serialize: ClassVar[list[str]] = [
        'active',
        'closed'
    ]

class OptionContract(Contract):
    expiration_date: date
    strike_price: float
    option_type: OptionType
    candles: List[OptionCandle] = []
    is_tradable: bool = True
    lot_size: int = 50
    positions: PositionByStatus = PositionByStatus()

    table: Literal['options_temp'] = 'options_temp'
    permanent: Literal[False] = False

    _serialize: ClassVar[list[str]] = Contract._serialize + [
        'positions',
        'expiration_date',
        'strike_price',
        'option_type',
        'lot_size',
        'permanent',
        'table'
    ]


    def __hash__(self):
        return hash((self.symbol, self.expiration_date, self.strike_price, self.option_type, self.exchange, self.time_frame))
    
    def __eq__(self, other):
        return hash(self) == hash(other)

    def __getattr__(self, name: str) -> Callable[ [int] , Any]:
        if name in {"close", "open", "high", "low", "volume", "oi"}:
            def attribute(index: int = 0) -> Any:
                return self.get_candle(name, index)
            return attribute
        raise AttributeError(f"{self.table} contract doesn't have access to: {name}")

    def enter(self, 
                side: Literal['BUY', 'SELL'], 
                quantity: int,
                order_type: Literal['MARKET', 'LIMIT', 'STOP_LOSS_MARKET', 'STOP_LOSS_LIMIT'] = 'MARKET', 
                price: Optional[float] = None, 
                trigger_price: Optional[float] = None, 
                time_in_force: Literal['DAY','GTC','IOC','FOK'] = 'GTC',
                fees: float = 0,
                stop_loss: Optional[float] = None,
                take_profit: Optional[float] = None,
                trailing_stop_loss: Optional[float] = None, 
            ) -> Optional[OptionPosition]:

        if self.strategy._block_:
            return None

        position = OptionPosition(
            contract = self,
            position_id =str(len(self.positions.closed) + 1),
            entry_orders = [],
            exit_orders = [],
            status = PositionStatus.OPEN,
            direction = 'LONG' if side == 'BUY' else 'SHORT',
            realized_pnl = 0,
            unrealized_pnl = 0,
            current_price = self.ltp,
            current_quantity = 0,
            start_time = self.time,
            stop_loss = (self.ltp - stop_loss if side == 'BUY' else self.ltp + stop_loss) if stop_loss else None,
            take_profit = (self.ltp + take_profit if side == 'BUY' else self.ltp - take_profit) if take_profit else None,
            trailing_stop_loss = (self.ltp - trailing_stop_loss if side == 'BUY' else self.ltp + trailing_stop_loss) if trailing_stop_loss else None
        )

        position.add(
            quantity = quantity,
            order_type = order_type,
            price = price,
            trigger_price = trigger_price,
            time_in_force = time_in_force,
            fees = fees
        )
        self.positions.active = position

        self.status = ContractStatus.ACTIVE
        return position

    def exit(self,
                exit_percentage: float = 100,
                quantity: Optional[int] = None,
                order_type: Literal['MARKET', 'LIMIT', 'STOP_LOSS_MARKET', 'STOP_LOSS_LIMIT'] = 'MARKET', 
                price: Optional[float] = None, 
                trigger_price: Optional[float] = None, 
                time_in_force: Literal['DAY','GTC','IOC','FOK'] = 'GTC',
                fees: float = 0,
            ) -> OptionPosition:

        position = self.positions.active
        position.exit(exit_percentage = exit_percentage, quantity = quantity, order_type = order_type, price = price, trigger_price = trigger_price, time_in_force = time_in_force, fees = fees)

        return self.positions.active

    def add(self,
                quantity: int,
                order_type: Literal['MARKET', 'LIMIT', 'STOP_LOSS_MARKET'] = 'MARKET',
                price: Optional[float] = None,
                trigger_price: Optional[float] = None,
                time_in_force: Literal['DAY','GTC','IOC','FOK'] = 'GTC',
                fees: float = 0
            ) -> Optional[OptionPosition]:

        if not self.positions.active:
            return self.enter(side = 'BUY', 
                                quantity = quantity, 
                                order_type = order_type, 
                                price = price, 
                                trigger_price = trigger_price, 
                                time_in_force = time_in_force, 
                                fees = fees
                            )
        else:
            return self.positions.active.add(
                quantity = quantity,
                order_type = order_type,
                price = price,
                trigger_price = trigger_price,
                time_in_force = time_in_force,
                fees = fees
            )

    def order(self,
                quantity: int,
                side: Literal['BUY', 'SELL'],
                order_type: Literal['MARKET', 'LIMIT', 'STOP_LOSS_MARKET'] = 'MARKET',
                price: Optional[float] = None,
                trigger_price: Optional[float] = None,
                time_in_force: Literal['DAY','GTC','IOC','FOK'] = 'GTC',
                fees: float = 0
                ) -> OptionPosition:

        position = self.positions.active
        if position:
            CONDITIONS = {
                'LONG': {
                    'BUY': 'entry',
                    'SELL': 'exit',
                },
                'SHORT': {
                    'BUY': 'exit',
                    'SELL': 'entry',
                }
            }

            if CONDITIONS[position.direction][side] == 'entry':
                return self.add(quantity = quantity, order_type = order_type, price = price, trigger_price = trigger_price, time_in_force = time_in_force, fees = fees)
            else:
                return self.exit(quantity = quantity, order_type = order_type, price = price, trigger_price = trigger_price, time_in_force = time_in_force, fees = fees)
        else:
            return self.enter(side = side, quantity = quantity, order_type = order_type, price = price, trigger_price = trigger_price, time_in_force = time_in_force, fees = fees)

    def _update_positions(self):
        position = self.positions.active
        position._calculate_unrealized_pnl()

        position._update_orders()
        position.check_exit_conditions()

        if position.trailing_stop_loss:
            position.update_trailing_stop_loss()

        position.update_current_price()
        self.previous_ltp = self.ltp

    def distance_from_expiry(self, days: int = True, hours: int = False, minutes: int = False) -> int:
        if days:
            return (self.expiration_date - self.time.date()).days

        expiry_time = datetime.combine(self.expiration_date, time(15, 30))
        if hours:
            return (expiry_time - self.time).total_seconds() // 3600
        if minutes:
            return (expiry_time - self.time).total_seconds() // 60
        return (expiry_time - self.time).total_seconds()

    def is_expiry_today(self) -> bool:
        return self.expiration_date == self.time.date()

    def has_expired(self) -> bool:
        return self.expiration_date < self.time.date()

    def cancel_and_exit(self):
        self.cancel_all_pending_orders()
        self.exit(exit_percentage = 100)

    def cancel_all_pending_orders(self):
        if self.positions.active:
            self.positions.active.cancel_all_pending_orders()

class IndexContract(Contract):
    candles: List[IndexCandle] = []
    is_tradable: bool = False
    table: Literal['index'] = 'index'
    permanent: Literal[True] = True
    options_expiry: Optional[List[date]] = []
    futures_expiry: Optional[List[date]] = [] 
    lot_size: int = 50
    strike_gap: float = 100
    static_data: Optional[IndexStaticData] = None


    _serialize: ClassVar[list[str]] = Contract._serialize + [
        'candles',
        'lot_size',
        'strike_gap',
        'options_expiry',
        'futures_expiry',
        'table'
    ]

    class Config:
        extra = "allow"

    def __init__(self, **data):
        super().__init__(**data)
        self.static_data = STATIC_DATA_INDEX[self.symbol]

    def __hash__(self):
        return hash((self.symbol, self.exchange, self.time_frame))

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __getattr__(self, name: str) -> Callable[ [int] , Any]:
        try:
            return super().__getattribute__(name)
        except AttributeError:
            if name in {"close", "open", "high", "low"}:
                def attribute(index: int = 0) -> Any:
                    return self.get_candle(name, index)
                return attribute
            raise AttributeError(f"{self.table} contract doesn't have access to: {name}")

    def current_expiry(self) -> date:
        return self.static_data.get_current_expiry(self.time)

    def is_expiry_today(self) -> bool:
        return self.static_data.get_current_expiry(self.time) == self.time.date()

    def monthly_expiry(self) -> date:
        return self.static_data.get_monthly_expiry(self.time)
    
    def next_expiry(self) -> date:
        return self.static_data.get_current_expiry(self.time, index=True)
    
    def next_monthly_expiry(self) -> date:
        return self.static_data.get_next_monthly_expiry(self.time)

    def get_all_expiry(self) -> List[date]:
        current_expiry = self.static_data.get_current_expiry(self.time, index=True)
        return self.static_data.options_expiry[current_expiry:]

    def get_nth_expiry(self, n: int) -> date:
        current_expiry = self.static_data.get_current_expiry(self.time, index=True)

        if current_expiry + n >= len(self.static_data.options_expiry):
            return self.static_data.options_expiry[-1]
        return self.static_data.options_expiry[current_expiry + n]

    def get_atm(self):
        return round(self.ltp / self.static_data.strike_gap) * self.static_data.strike_gap

