from datetime import datetime, date
from typing import List, Literal, Union
from backtest.modules.child_classes.contract import OptionContract, IndexContract
from enum import Enum

if __name__ != '__main__':
    from lt_types import TimeFrame, OptionType, AssetType
    from backtest.models import Index, Options

def query_for_backtest(contract: Union[OptionContract, IndexContract], start_time: date, end_time: date):
    query = f"""
        WITH market_time_series AS (
            SELECT time
            FROM generate_series(
                    date_trunc('day', TIMESTAMP '{start_time}') + INTERVAL '9 hours 15 minutes',
                    date_trunc('day', TIMESTAMP '{end_time}') + INTERVAL '15 hours 30 minutes',
                    INTERVAL '1 minute'
                ) AS time
        WHERE EXTRACT(DOW FROM time) NOT IN (6, 0)
            AND time::time >= TIME '09:15:00'       
            AND time::time <= TIME '15:30:00'           
        ),
        candle_group AS (
        SELECT
            time AT TIME ZONE 'Asia/Kolkata' AS time,
            symbol,
            open,
            high,
            low,
            close,
            volume,
            exchange,
            {f"expiration_date, strike_price, option_type, oi," if contract.table == 'options_temp' else ""}
            token,
            FLOOR((EXTRACT(EPOCH FROM time) + 1800) / {contract.time_frame.value}) AS minute_group
        FROM {contract.table}
        WHERE time >= '{start_time}'
        AND time < '{end_time}'
        AND EXTRACT(DOW FROM time) NOT IN (6, 0)
        AND symbol = '{contract.symbol}'
        {f"AND expiration_date = '{contract.expiration_date}'" if contract.table == 'options_temp' else ""}
        {f"AND strike_price = {contract.strike_price}" if contract.table == 'options_temp' else ""}
        {f"AND option_type = '{contract.option_type.value}'" if contract.table == 'options_temp' else ""}
        ),
        full_time_series AS (
            SELECT DISTINCT time FROM market_time_series
            UNION
            SELECT DISTINCT time FROM candle_group
        ),
        processed_data AS (
            SELECT
                time,
                symbol,
                token,
                {f"expiration_date, strike_price, option_type, " if contract.table == 'options_temp' else ""}
                {f"AVG(oi) OVER (PARTITION BY MINUTE_GROUP ORDER BY TIME ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS oi, " if contract.table == 'options_temp' else ""}
                FIRST_VALUE(open) OVER (PARTITION BY minute_group ORDER BY time) AS open,
                MAX(high) OVER (PARTITION BY minute_group ORDER BY time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS rolling_high,
                MIN(low) OVER (PARTITION BY minute_group ORDER BY time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS rolling_low,
                close,
                SUM(volume) OVER (PARTITION BY minute_group ORDER BY time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS total_volume,
                ROW_NUMBER() OVER (PARTITION BY minute_group ORDER BY time DESC) AS row_rank,
                exchange
            FROM candle_group
        )
        SELECT
            ts.time as time,
            pd.symbol as symbol,
            {f"pd.expiration_date as expiration_date, pd.strike_price as strike_price, pd.option_type as option_type, pd.oi as oi," if contract.table == 'options_temp' else ""}
            COALESCE(pd.open, LAG(pd.close) OVER (ORDER BY ts.time)) AS open,
            COALESCE(pd.rolling_high, pd.open) AS high,
            COALESCE(pd.rolling_low, pd.open) AS low,
            COALESCE(pd.close, pd.open) AS close,
            COALESCE(pd.total_volume, 0) AS volume,
            pd.exchange as exchange,
            pd.token as token,
            CASE WHEN pd.row_rank = 1 THEN true ELSE false END AS candle_close
        FROM full_time_series ts
        LEFT JOIN processed_data pd
        ON ts.time = pd.time
        ORDER BY ts.time;
    """
    with open('query.sql', 'w') as f:
        f.write(query)
    if contract.table == 'options_temp':
        return Options.objects.raw(query)
    else:
        return Index.objects.raw(query)

def get_candles_query(contract: Union[OptionContract, IndexContract], start_time: datetime, end_time: datetime):

    query = f"""
        with candles_1m as (SELECT
            time,
            symbol,
            open,
            high,
            low,
            close,
            volume,
            exchange,
            {f"expiration_date, strike_price, option_type, oi" if contract.table == 'options_temp' else ""}
            token,
            FLOOR((EXTRACT(EPOCH FROM time) + 1800) / {contract.time_frame}) AS minute_group
        FROM {contract.table}
        WHERE time >= '{start_time}'
        AND time < '{end_time}'
        AND symbol = '{contract.symbol}'
        {f"AND expiration_date = '{contract.expiration_date}'" if contract.table == 'options_temp' else ""}
        {f"AND strike_price = {contract.strike_price}" if contract.table == 'options_temp' else ""}
        {f"AND option_type = '{contract.option_type}'" if contract.table == 'options_temp' else ""}
        aggregated_data AS (
            SELECT
                *,
                FIRST_VALUE(open) OVER (PARTITION BY minute_group ORDER BY time) AS first_open,
                LAST_VALUE(close) OVER (PARTITION BY minute_group ORDER BY time RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_close
            FROM candles_1m
        )
        SELECT
            MIN(time) AS time,
            symbol,
            {f"expiration_date, strike_price, option_type, AVG(oi)" if contract.table == 'options_temp' else ""}
            token,
            MIN(first_open) AS open,
            MAX(high) AS high,
            MIN(low) AS low,
            MAX(last_close) AS close,
            SUM(volume) AS volume,
            exchange
        FROM aggregated_data
        GROUP BY
            symbol, 
            {f"expiration_date, strike_price, option_type, " if contract.table == 'options_temp' else ""}
            token,
            exchange,
            minute_group
        ORDER BY time;
    """

    with open('query.sql', 'w') as f:
        f.write(query)

    if contract.table == 'options_temp':
        return Options.objects.raw(query)
    else:
        return Index.objects.raw(query)

def testing():

    start_time = datetime(2024, 1, 1)
    end_time = datetime(2024, 12, 4)

    contract = OptionContract(
        symbol='NIFTY',
        exchange='NSE',
        time_frame=TimeFrame.MINUTE_5,
        expiration_date=date(2024, 1, 4),
        strike_price=21750,
        option_type=OptionType.CALL,
    )
    result = query_for_backtest(contract=contract, start_time=start_time, end_time=end_time)
    print(result)
    return result
    # return get_candles_query(table, start_time, end_time, symbol, time_arg, expiration_date, strike_price, option_type)

if __name__ == '__main__':
    testing()
