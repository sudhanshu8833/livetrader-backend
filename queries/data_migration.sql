
-- INSERT INTO options_data (
--     contract,
--     time,
--     open,
--     high,
--     low,
--     close,
--     volume,
--     oi,
--     token
-- )
WITH first_timestamps AS (
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
        LAST_VALUE(po.open) OVER w AS open,
        LAST_VALUE(po.high) OVER w AS high,
        LAST_VALUE(po.low) OVER w AS low,
        LAST_VALUE(po.close) OVER w AS close,
        COALESCE(po.volume, 0) AS volume,
        LAST_VALUE(po.oi) OVER w AS oi,
        LAST_VALUE(po.token) OVER w AS token
        -- po.token
    FROM time_series ts
    LEFT JOIN prepared_options po
    ON po.contract = ts.contract
    AND po.time = ts.time
    WINDOW w AS (
        PARTITION BY ts.contract, ts.time 
        ORDER BY po.time
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    )
    -- WINDOW w1 AS (
    --     PARTITION BY ts.contract, ts.time 
    --     ORDER BY po.time DESC
    --     ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW IGNORE NULLS
    -- )
)
SELECT * FROM ohlc_data order by time limit 100;
-- ON CONFLICT DO NOTHING;