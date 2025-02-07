WITH first_timestamps AS (
    SELECT 
        contract,
        available_from,
        expiration_date
    FROM options_contract
    LIMIT 1
),
time_series AS (
    SELECT 
        ft.contract,
        ts.time AT TIME ZONE 'Asia/Kolkata' AS time
    FROM first_timestamps ft
    CROSS JOIN LATERAL 
    (
        SELECT time_new
        FROM generate_series(
            ft.available_from, 
            ft.expiration_date + TIME '10:00:00', 
            '1 minute'::interval
        ) AS time_new
        WHERE EXTRACT(DOW FROM time_new) NOT IN (0, 6)
        AND time_new::time >= TIME '03:45:00'
        AND time_new::time <= TIME '10:00:00'
        AND time_new::date NOT IN (SELECT date FROM holidays WHERE exchange = 'NSE')
    ) AS ts(time)
),
prepared_options AS (
    SELECT
        symbol || '_' || TO_CHAR(expiration_date, 'YYMMDD') || '_' || strike_price::int || '_' || option_type AS contract,
        time AT TIME ZONE 'Asia/Kolkata' AS time,
        symbol,
        open,
        high,
        low,
        close,
        volume,
        oi,
        token
    FROM options_temp 
    ORDER BY contract
),
ohlc_data AS (
    SELECT
        ts.contract,
        ts.time,
        -- Forward-fill open
        COALESCE(
            po.open,
            LAST_VALUE(po.open) OVER (PARTITION BY ts.contract ORDER BY ts.time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
        ) AS open,
        -- Forward-fill high
        COALESCE(
            po.high,
            LAST_VALUE(po.high) OVER (PARTITION BY ts.contract ORDER BY ts.time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
        ) AS high,
        -- Forward-fill low
        COALESCE(
            po.low,
            LAST_VALUE(po.low) OVER (PARTITION BY ts.contract ORDER BY ts.time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
        ) AS low,
        -- Forward-fill close
        COALESCE(
            po.close,
            LAST_VALUE(po.close) OVER (PARTITION BY ts.contract ORDER BY ts.time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
        ) AS close,
        -- Forward-fill volume (default to 0 if NULL)
        COALESCE(po.volume, 0) AS volume,
        -- Forward-fill oi
        COALESCE(
            po.oi,
            LAST_VALUE(po.oi) OVER (PARTITION BY ts.contract ORDER BY ts.time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
        ) AS oi,
        -- Forward-fill token
        COALESCE(
            po.token,
            LAST_VALUE(po.token) OVER (PARTITION BY ts.contract ORDER BY ts.time ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
        ) AS token
    FROM time_series ts
    LEFT JOIN prepared_options po
    ON po.contract = ts.contract
    AND po.time = ts.time
)
SELECT * 
FROM ohlc_data 
ORDER BY time 
LIMIT 100;