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
),
ohlc_data AS (
    SELECT
        ts.contract,
        ts.time,
        po.symbol,
        
        -- First step: If open exists, use it to fill missing values in the same row
        po.open,
        COALESCE(po.high, po.open) AS high,
        COALESCE(po.low, po.open) AS low,
        COALESCE(po.close, po.open) AS close,
        COALESCE(po.volume, 0) AS volume,
        po.oi,
        po.token
    FROM time_series ts
    LEFT JOIN prepared_options po
    ON po.time = ts.time
    AND po.contract = ts.contract
),
recursive_fill AS (
    -- Base case: First available row
    SELECT 
        contract, 
        time, 
        symbol,
        open,
        high,
        low,
        close,
        volume,
        oi,
        token
    FROM ohlc_data
    WHERE close IS NOT NULL
    UNION ALL
    -- Recursive case: Fill missing values with last known value
    SELECT 
        r.contract, 
        o.time, 
        r.symbol,
        
        -- Forward-fill using previous row
        COALESCE(o.open, r.close) AS open,
        COALESCE(o.high, r.close) AS high,
        COALESCE(o.low, r.close) AS low,
        COALESCE(o.close, r.close) AS close,

        -- Set volume to 0 if missing
        COALESCE(o.volume, 0) AS volume,

        -- Forward-fill OI
        COALESCE(o.oi, r.oi) AS oi,

        o.token
    FROM recursive_fill r
    JOIN ohlc_data o 
    ON r.contract = o.contract AND r.time < o.time
)
SELECT * FROM recursive_fill ORDER BY contract, time;
