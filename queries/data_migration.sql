explain analyze INSERT INTO options_data (contract, time, open, high, low, close, volume, oi, token)

WITH RECURSIVE filled_data AS (
    SELECT 
        contract,
        time,
        open,
        high,
        low,
        close,
        volume,
        oi,
        token,
        close AS last_close
    FROM (
        SELECT *,
            ROW_NUMBER() OVER (PARTITION BY contract ORDER BY time) as rn
        FROM ohlc_data
        WHERE close IS NOT NULL
    ) t
    WHERE rn = 1
    UNION ALL

    SELECT 
        o.contract,
        o.time,
        COALESCE(o.open, f.last_close) AS open,
        COALESCE(o.high, f.last_close) AS high,
        COALESCE(o.low, f.last_close) AS low,
        COALESCE(o.close, f.last_close) AS close,
        COALESCE(o.volume, 0) AS volume,
        COALESCE(o.oi, f.oi) AS oi,
        o.token,
        COALESCE(o.close, f.last_close) AS last_close
    FROM filled_data f
    INNER JOIN ohlc_data o 
    ON f.contract = o.contract
    AND o.time > f.time
    AND NOT EXISTS (
        SELECT 1 
        FROM ohlc_data o2
        WHERE o2.contract = o.contract
        AND o2.time > f.time 
        AND o2.time < o.time
    )
),
first_timestamps AS (
    SELECT 
        contract,
        available_from,
        expiration_date
    FROM options_contract
    limit 1
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
    FROM options_temp order by contract
),
ohlc_data AS (
    SELECT
        ts.contract,
        ts.time,
        po.open as open,
        COALESCE(po.high,po.open) as high,
        COALESCE(po.low, po.open) as low,
        COALESCE(po.close, po.open) as close,
        COALESCE(po.volume, 0) AS volume,
        po.oi as oi,
        po.token as token
    FROM time_series ts
    LEFT JOIN prepared_options po
    ON po.contract = ts.contract
    AND po.time = ts.time
    ORDER BY ts.contract, ts.time
)

SELECT contract, time, open, high, low, close, volume, oi, token 
FROM filled_data
ON CONFLICT DO NOTHING;