from pydantic import BaseModel
from typing import List, Literal, Optional, Any
from .order import OrderStatus, OptionOrder
from enum import Enum
from datetime import datetime
# from .contract import OptionContract

class PositionStatus(Enum):
    PENDING = "PENDING"
    OPEN = "OPEN"
    CLOSED = "CLOSED"


class Position(BaseModel):
    position_id: str
    status: PositionStatus
    direction: Literal['LONG', 'SHORT']
    realized_pnl: float = 0
    unrealized_pnl: float = 0
    current_price: Optional[float]
    current_quantity: float
    start_time: Optional[datetime]
    end_time: Optional[datetime] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    trailing_stop_loss: Optional[float] = None

    def _calculate_realized_pnl(self, quantity: float, price: float) -> float:
        already_exited_quantity = 0
        for order in self.exit_orders:
            if order.status == OrderStatus.FILLED:
                already_exited_quantity += order.quantity_executed

        trades = []
        pending_trades = []

        for order in self.entry_orders:
            if order.status == OrderStatus.FILLED:
                if order.quantity_executed <= already_exited_quantity:
                    already_exited_quantity -= order.quantity_executed

                elif order.quantity_executed > already_exited_quantity:
                    quantity_left_to_exit = order.quantity_executed - already_exited_quantity
                    if quantity > quantity_left_to_exit or quantity == 0:
                        trades.append({
                            'quantity': quantity_left_to_exit,
                            'price': order.average_executed_price,
                        })
                        if quantity == 0:
                            pending_trades.append({
                                'quantity': order.quantity_executed,
                                'price': order.average_executed_price,
                            })
                        already_exited_quantity = 0
                    else:
                        trades.append({
                            'quantity': quantity,
                            'price': order.average_executed_price,
                        })
                        pending_trades.append({
                            'quantity': quantity_left_to_exit - quantity,
                            'price': order.average_executed_price,
                        })
                        quantity = 0

        realized_pnl = 0
        for trade in trades:
            if self.direction == 'LONG':
                realized_pnl += (price - trade['price']) * trade['quantity']
            else:
                realized_pnl += (trade['price'] - price) * trade['quantity']

        return realized_pnl, pending_trades

    def _recalculate_unrealized_pnl(self, trades: List[dict]):
        for trade in trades:
            if self.direction == 'LONG':
                self.unrealized_pnl += (self.contract.ltp - trade['price']) * trade['quantity']
            else:
                self.unrealized_pnl += (trade['price'] - self.contract.ltp) * trade['quantity']

    def _calculate_unrealized_pnl(self) -> float:
        if self.direction == 'LONG':
            self.unrealized_pnl += (self.contract.ltp - self.current_price) * self.current_quantity
        else:
            self.unrealized_pnl += (self.current_price - self.contract.ltp) * self.current_quantity

    def cancel_all_pending_orders(self):
        for order in self.entry_orders:
            if order.status == OrderStatus.OPEN:
                order.cancel_order()

        for order in self.exit_orders:
            if order.status == OrderStatus.OPEN:
                order.cancel_order()

    def subtract_from_position(self, order: OptionOrder):
        realized_pnl, pending_trades = self._calculate_realized_pnl(order.quantity_executed, order.average_executed_price)
        self.unrealized_pnl -= realized_pnl
        self.realized_pnl += (realized_pnl - order.fees)

        amount = order.quantity_executed * order.average_executed_price - order.fees
        if order.side == 'BUY':
            amount *= -1
        self.contract.strategy.update_portfolio(amount)
        self.contract.strategy._update_realised_pnl(realized_pnl - order.fees)

        self.current_quantity -= order.quantity_executed
        if self.current_quantity == 0:
            self.status = PositionStatus.CLOSED
            self.end_time = self.contract.time

            self.cancel_all_pending_orders()
            self.contract.active_position_closed()

    def add_to_position(self, order: OptionOrder):
        if self.status == PositionStatus.PENDING:
            self.status = PositionStatus.OPEN

        amount = order.quantity_executed * order.average_executed_price - order.fees
        if order.side == 'BUY':
            amount *= -1

        self.contract.strategy.update_portfolio(amount)

        self.current_quantity += order.quantity_executed
        self.realized_pnl -= order.fees

    def exit(self,
                exit_percentage: float = 100,
                quantity: Optional[int] = None,
                order_type: Literal['MARKET', 'LIMIT', 'STOP_LOSS_MARKET', 'STOP_LOSS_LIMIT'] = 'MARKET', 
                price: Optional[float] = None, 
                trigger_price: Optional[float] = None, 
                time_in_force: Literal['DAY','GTC','IOC','FOK'] = 'GTC',
                fees: float = 0
            ):

        quantity = quantity if quantity else int(self.current_quantity * (exit_percentage / 100))
        order = self._order(
            quantity = quantity,
            side = 'SELL' if self.direction == 'LONG' else 'BUY',
            order_type = order_type,
            price = price,
            trigger_price = trigger_price,
            time_in_force = time_in_force,
            fees = fees
        )

        if order.status == OrderStatus.FILLED:
            self.subtract_from_position(order)

        self.exit_orders.append(order)
        return self

    def _order(self,
                quantity: float,
                side: Literal['BUY', 'SELL'],
                order_type: Literal['MARKET', 'LIMIT', 'STOP_LOSS_MARKET', 'STOP_LOSS_LIMIT'],
                price: Optional[float],
                trigger_price: Optional[float],
                time_in_force: Literal['DAY','GTC','IOC','FOK'],
                fees: float,
            ) -> OptionOrder:

        status = OrderStatus.OPEN
        if order_type == 'MARKET':
            status = OrderStatus.FILLED
        order = OptionOrder(
            position=self,
            order_id = str(len(self.entry_orders) + len(self.exit_orders) + 1),
            time = self.contract.time,
            side = side,
            quantity_ordered = quantity,
            quantity_executed = quantity if status == OrderStatus.FILLED else 0,
            average_executed_price = self.contract.ltp if status == OrderStatus.FILLED else None,
            price = price,
            trigger_price = trigger_price,
            time_in_force = time_in_force,
            order_type = order_type,
            fees = fees,
            status = status
        )
        return order

    def add(self,
                quantity: int,
                order_type: Literal['MARKET', 'LIMIT', 'STOP_LOSS_MARKET'] = 'MARKET',
                price: Optional[float] = None,
                trigger_price: Optional[float] = None,
                time_in_force: Literal['DAY','GTC','IOC','FOK'] = 'GTC',
                fees: float = 0
            ) -> Optional['OptionPosition']:

        if self.contract.strategy._block_:
            return None

        order = self._order(
            quantity = quantity,
            side = 'BUY' if self.direction == 'LONG' else 'SELL',
            order_type = order_type,
            price = price,
            trigger_price = trigger_price,
            time_in_force = time_in_force,
            fees = fees
        )

        self.entry_orders.append(order)

        if order.status == OrderStatus.FILLED:
            self.add_to_position(order)
        return self

    def update_trailing_stop_loss(self):
        delta_price = self.contract.ltp - self.current_price

        trailing_conditions = {
            'LONG': delta_price > 0,
            'SHORT': delta_price < 0
        }

        if trailing_conditions.get(self.direction, False):
            self.trailing_stop_loss += delta_price

    def update_current_price(self):
        self.current_price = self.contract.ltp

    def check_exit_conditions(self):
        if self.take_profit or self.stop_loss or self.trailing_stop_loss:
            EXIT_CONDITIONS = {
                'LONG': {
                    'take_profit': self.take_profit and self.contract.ltp >= self.take_profit,
                    'stop_loss': self.stop_loss and self.contract.ltp <= self.stop_loss,
                    'trailing_stop_loss': self.trailing_stop_loss and self.contract.ltp <= self.trailing_stop_loss
                },
                'SHORT': {
                    'take_profit': self.take_profit and self.contract.ltp <= self.take_profit,
                    'stop_loss': self.stop_loss and self.contract.ltp >= self.stop_loss,
                    'trailing_stop_loss': self.trailing_stop_loss and self.contract.ltp >= self.trailing_stop_loss
                }
            }

            for condition in EXIT_CONDITIONS[self.direction].values():
                if condition:
                    self.exit()

    def _update_orders(self):
        for order in self.entry_orders:
            if order.status == OrderStatus.OPEN:
                if order.check_order_fill():
                    if self.contract.strategy._block_:
                        order.cancel_order()
                        continue

                    order._fill_order(self.contract.ltp)
                    self.add_to_position(order)

        for order in self.exit_orders:
            if order.status == OrderStatus.OPEN:
                if order.check_order_fill():
                    order._fill_order(self.contract.ltp)
                    self.subtract_from_position(order)

    def is_closed(self):
        return self.status == PositionStatus.CLOSED

class OptionPosition(Position):
    contract: Any
    entry_orders: List[OptionOrder] = []
    exit_orders: List[OptionOrder] = []