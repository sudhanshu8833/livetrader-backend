from pydantic import BaseModel
from typing import List, Union, Optional
from datetime import date, datetime, timedelta
import bisect

class IndexStaticData(BaseModel):
    options_expiry: List[date] = []
    futures_expiry: List[date] = []
    symbol: str
    exchange: str
    lot_size: int
    strike_gap: int
    holidays: List[date] = []

    # binary search to get the current expiry

    def get_current_expiry(self, time_now: Optional[Union[datetime, date]], index: Optional[int] = None, offset: Optional[int] = 0) -> date:
        if isinstance(time_now, datetime):
            time_now = time_now.date()

        left = 0
        right = len(self.options_expiry) - 1
        while left <= right:
            mid = (left + right) // 2
            if self.options_expiry[mid] == time_now:
                if index:
                    return mid + offset
                return self.options_expiry[mid + offset]
            elif self.options_expiry[mid] < time_now:
                left = mid + 1
            else:
                right = mid - 1

        if index:
            return right + 1 + offset
        return self.options_expiry[right + 1 + offset]

    def get_monthly_expiry(self, time_now: Optional[Union[datetime, date]]) -> date:
        current_expiry = self.get_current_expiry(time_now, index=True)

        for expiry in self.options_expiry[current_expiry:]:
            if expiry.month != time_now.month:
                return last_expiry
            last_expiry = expiry

    def get_next_monthly_expiry(self, time_now: Optional[Union[datetime, date]]) -> date:
        next_month_time = time_now + timedelta(days=30)
        return self.get_monthly_expiry(next_month_time)
    
