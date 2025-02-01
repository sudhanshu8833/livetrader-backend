from pydantic import BaseModel, Field
from typing import Optional, Literal, Dict, Union
from broker.constants.broker import BrokerConstants

class CreateOrderParams(BaseModel):
    symbol: str
    side: Literal["BUY", "SELL"]
    order_type: Literal["MARKET", "LIMIT", "STOP_LOSS", "STOP_LOSS_LIMIT"]
    quantity: Optional[float]
    price: Optional[float]
    time_in_force: Optional[Literal["GTC", "IOC", "FOK"]]
    broker_specific: Optional[Dict[str, str]]
    # trigger price, timestamp, etc

class CreateOrderResponse(BaseModel):
    order_id: Union[str, int]
    symbol: str
    execution_time: int
    executed_quantity: float
    average_executed_price: Optional[float]
    status: Literal['OPEN', 'PARTIALLY_FILLED', 'FILLED', 'CANCELLED']
    time_in_force: Literal['GTC', 'IOC', 'FOK']
