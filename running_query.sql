with candle_group AS (
SELECT
    time AT TIME ZONE 'Asia/Kolkata' AT TIME ZONE 'UTC' AS time,
    symbol,
    open,
    high,
    low,
    close,
    volume,
    exchange,
    token,
    FLOOR((EXTRACT(EPOCH FROM time) + 1800) / 300) AS minute_group
FROM index
WHERE time >= '2024-12-25 05:49:01.472086'
AND time < '2024-12-30 05:49:01.472092'
AND symbol = 'NIFTY'
),
processed_data AS (
    SELECT
        time,
        symbol,
        token,
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
    time,
    symbol,
    token,
    open,
    rolling_high    AS high,
    rolling_low     AS low,
    close,
    total_volume    AS volume,
    exchange
from processed_data
ORDER BY time;