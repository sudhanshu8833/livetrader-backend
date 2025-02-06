from pydantic import BaseModel
from datetime import datetime
from typing import Optional, ClassVar
from backtest.serialize import BaseSerializer
class Candle(BaseModel, BaseSerializer):

    _serialize: ClassVar[list[str]] = [
        "time",
        "open",
        "high",
        "low",
        "close",
        "token",
        "candle_close"
    ]

    time: datetime
    open: float
    high: float
    low: float
    close: float
    token: Optional[str] = None
    candle_close: bool = False

    class Config:
        orm_mode = True
        extra = "allow"

class IndexCandle(Candle):
    pass

class OptionCandle(Candle):
    oi: int
    volume: int