from pydantic import BaseModel
from enum import Enum
from typing import Literal, Optional, Any
from datetime import datetime

class OrderType(Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP_LOSS_MARKET = "STOP_LOSS_MARKET"

class OrderStatus(Enum):
    OPEN = "OPEN"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"

class Order(BaseModel):
    position: Any
    order_id: str
    time: datetime
    side: Literal['BUY', 'SELL']
    quantity_ordered: float
    quantity_executed: float = 0
    average_executed_price: Optional[float] = None
    price: Optional[float] = None # for all limit containing orders
    trigger_price: Optional[float] = None# for stop loss and take profit orders
    status: OrderStatus = OrderStatus.OPEN
    fees: float = 0

    def _fill_order(self, price: float):
        self.quantity_executed = self.quantity_ordered
        self.status = OrderStatus.FILLED
        self.average_executed_price = price
    
    def cancel_order(self):
        if self.status == OrderStatus.OPEN:
            self.status = OrderStatus.CANCELLED
        raise ValueError("Order is already filled or cancelled")

    def check_order_fill(self) -> bool:
        if self.status == OrderStatus.FILLED:
            raise ValueError("Order is already filled")

        price = self.position.contract.ltp
        if self.order_type == OrderType.LIMIT:
            if self.side == 'BUY':
                if price <= self.price:
                    return True
            else:
                if price >= self.price:
                    return True

        elif self.order_type == OrderType.STOP_LOSS_MARKET:
            if self.side == 'BUY':
                if price >= self.trigger_price:
                    return True
            else:
                if price <= self.trigger_price:
                    return True

        return False

class OptionOrder(Order):
    time_in_force: Literal['DAY','GTC', 'IOC', 'FOK'] = 'GTC'
    order_type: OrderType