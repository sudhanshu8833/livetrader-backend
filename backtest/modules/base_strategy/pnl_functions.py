from datetime import timedelta, date

class PNLManagement:
    def __init__(self):
        pass

    def get_pnl_for_date_range(self, start_date: date, end_date: date) -> float:
        pnl_values = self.realised_pnl_map.irange(start_date, end_date, inclusive=(True, True))
        return sum(self.realised_pnl_map[d] for d in pnl_values)

    def get_todays_pnl(self):
        return self.realised_pnl_map.get(self.time.date(), 0) + self.get_unrealised_pnl()

    def get_weeks_pnl(self):
        return self.get_pnl_for_date_range(self.time.date() - timedelta(days=self.time.weekday()), self.time.date())

    def get_months_pnl(self):
        return self.get_pnl_for_date_range(self.time.date().replace(day=1), self.time.date())

    def get_years_pnl(self):
        return self.get_pnl_for_date_range(self.time.date().replace(month=1, day=1), self.time.date())
    
    def get_unrealised_pnl(self):
        unrealised_pnl = 0
        for item in self.children_contracts.values():
            unrealised_pnl += item.get_unrealised_pnl()
        return unrealised_pnl
    
    def _get_pnl(self, date: date):
        return self.realised_pnl_map.get(date, 0)