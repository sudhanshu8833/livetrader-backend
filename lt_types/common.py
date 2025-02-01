from enum import Enum

class TimeFrame(Enum):
    MINUTE_1 = 60
    MINUTE_3 = 180
    MINUTE_5 = 300
    MINUTE_10 = 600
    MINUTE_15 = 900
    MINUTE_30 = 1800
    HOUR_1 = 3600
    HOUR_2 = 7200
    HOUR_4 = 14400
    DAY_1 = 86400
    WEEK_1 = 604800
    MONTH_1 = 2592000

class OptionType(Enum):
    CALL = 'CE'
    PUT = 'PE'

class AssetType(Enum):
    INDEX = 'index'
    OPTION = 'options'

