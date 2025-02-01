from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Candle(BaseModel):
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