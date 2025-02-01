from ingest_in_db import get_options_data, ingest_from_db
from datetime import timedelta, time as dt_time, datetime
import pytz
import time as t
option_candles = get_options_data()
ist = pytz.timezone('Asia/Kolkata')

def get_contract(index, expiry, strike, option_type):
    expiry = expiry.strftime('%y%m%d')
    strike = str(int(strike))
    return f"{index}_{expiry}_{strike}_{option_type}"


contract_inserts = set()
option_inserts = set()


last_contract = {}
inserted = 0

def get(contract, l = []):
    if last_contract.get(contract, {}).get(l[0]):
        return last_contract[contract][l[0]]
    elif last_contract.get(contract, {}).get(l[1]):
        return last_contract[contract][l[1]]
    elif last_contract.get(contract, {}).get(l[2]):
        return last_contract[contract][l[2]]
    elif last_contract.get(contract, {}).get(l[3]):
        return last_contract[contract][l[3]]
    return None

time1 = t.time()
for candle in option_candles:
    time = candle[0]
    index = candle[1]
    expiry = candle[2]
    strike = candle[3]
    option_type = candle[4]
    contract = get_contract(index, expiry, strike, option_type)

    open = candle[5] or get(contract, ['close', 'open', 'low', 'high'])
    high = candle[6] or get(contract, ['high', 'close', 'open', 'low'])
    low = candle[7] or get(contract, ['low', 'close', 'open', 'high'])
    close = candle[8] or get(contract, ['close', 'open', 'low', 'high'])
    volume = candle[9] or last_contract.get(contract,{}).get('volume') or 0
    oi = candle[10] or last_contract.get(contract,{}).get('oi')
    exchange = candle[11]
    token = candle[12]

    while(True):
        if not last_contract.get(contract):
            break
        if last_contract[contract]['time'] + timedelta(seconds=60) == time:
            break
        if time.time() == dt_time(3, 45):
            break

        new_time = last_contract[contract]['time']
        ist_time = new_time.astimezone(ist)

        if ist_time.time() > dt_time(15, 30) or ist_time.time() < dt_time(9, 15):
            continue
        elif last_contract[contract]['time'].date() != time.date():
            last_contract[contract]['time'] = time.replace(hour=3, minute=45, second=0)
            new_time = last_contract[contract]['time'] - timedelta(seconds=60)

        new_time = new_time + timedelta(seconds=60)
        option_inserts.add((contract, new_time, open, 0, oi))
        option_inserts.add((contract, new_time + timedelta(seconds=20), high, 0, oi))
        option_inserts.add((contract, new_time + timedelta(seconds=30), low, 0, oi))
        option_inserts.add((contract, new_time + timedelta(seconds=59), close, 0, oi))
        last_contract[contract]['time'] = new_time

    contract_inserts.add((contract, index, expiry, strike, option_type, exchange, token))

    if time.time() == dt_time(10, 0):
        option_inserts.add((contract, time, open, volume, oi))
    else:
        option_inserts.add((contract, time, open, volume, oi))
        option_inserts.add((contract, time + timedelta(seconds=20), high, 0, oi))
        option_inserts.add((contract, time + timedelta(seconds=30), low, 0, oi))
        option_inserts.add((contract, time + timedelta(seconds=59), close, 0, oi))

    if len(option_inserts) > 10000:
        ingest_from_db(contracts_data=list(contract_inserts), options_data=list(option_inserts))
        print(f"ingested time: {t.time() - time1}: for {len(option_inserts) + inserted} records")
        inserted += len(option_inserts)
        contract_inserts = set()
        option_inserts = set()

    last_contract[contract] = {
        'open': open,
        'high': high,
        'low': low,
        'close': close,
        'volume': volume,
        'oi': oi,
        'time': time
    }

print(f"looping time: {t.time() - time1}: for {len(option_inserts)} records")
time2 = t.time()
ingest_from_db(contracts_data=list(contract_inserts), options_data=list(option_inserts))

print(f"ingested time: {t.time() - time2}")