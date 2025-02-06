import json
from ingest_in_db import base_ingest_data, INSERT_INTO_HOLIDAYS

with open('../static_data/index.json') as f:
    data = json.load(f)

holidays = data['NIFTY']['holidays']

def prepare_data(holidays):
    data = []
    for holiday in holidays:
        data.append(('NSE',holiday,))
    return data

if __name__ == '__main__':
    data = prepare_data(holidays)
    print(data)
    base_ingest_data(INSERT_INTO_HOLIDAYS, data)

