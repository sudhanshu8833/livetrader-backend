from enum import Enum

class TimeFrame(Enum):
    MINUTE_1 = 1
    MINUTE_5 = 5
    MINUTE_15 = 15
    MINUTE_30 = 30
    HOUR_1 = 60
    DAY_1 = 1440
    WEEK_1 = 10080
    MONTH_1 = 43200

print(type(TimeFrame.MINUTE_1))
timeframe = TimeFrame.MINUTE_1

if isinstance(timeframe, TimeFrame):
    print("Yes")