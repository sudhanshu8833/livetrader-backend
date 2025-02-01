# from sortedcontainers import SortedDict
# from datetime import datetime, timedelta
# data = SortedDict()

# data[datetime.now().date()] = 1
# data[(datetime.now()-timedelta(days=1)).date()] = 2
# data[(datetime.now()-timedelta(days=2)).date()] = 3
# data[(datetime.now()-timedelta(days=3)).date()] = 4
# data[(datetime.now()-timedelta(days=4)).date()] = 5

# values = data.irange(datetime.now().date(), (datetime.now()-timedelta(days=3)).date(), inclusive=(True, True))
# print(sum([data[value] for value in values]))

# print(data)


from sortedcontainers import SortedDict
from datetime import date, timedelta

class LTStrategy:
    def __init__(self):
        self.realised_pnl_map = SortedDict()  # Keeps keys sorted for fast access

    def get_pnl_for_date_range(self, start_date: date, end_date: date) -> float:
        pnl_values = self.realised_pnl_map.irange(start_date, end_date, inclusive=(True, True))
        return sum(self.realised_pnl_map[d] for d in pnl_values)

# ✅ Usage
strategy = LTStrategy()
strategy.realised_pnl_map[date(2024, 2, 1)] = 100.0
strategy.realised_pnl_map[date(2024, 2, 10)] = 200.0
strategy.realised_pnl_map[date(2024, 1, 15)] = -50.0

print(strategy.get_pnl_for_date_range(date(2024, 1, 15), date(2024, 2, 10)))  # ✅ 300.0

print(strategy.__dict__)