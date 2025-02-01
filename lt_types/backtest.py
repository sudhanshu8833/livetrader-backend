from pydantic import BaseModel, Field
from typing import Literal
from datetime import datetime

class OptionCandle(BaseModel):
    time: datetime
    symbol: str 
    expiration_date: datetime
    strike_price: float
    option_type: Literal['CE', 'PE']
    open: float
    high: float
    low: float
    close: float
    volume: int
    oi: int
    exchange: str
    token: str = None
    candle_close: bool

    class Config:
        orm_mode = True

class IndexCandle(BaseModel):
    time: datetime
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: int
    exchange: str
    token: str = None
    candle_close: bool

    class Config:
        orm_mode = True