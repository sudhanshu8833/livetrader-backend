explain analyze WITH first_timestamps AS (
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
-- select * from time_series;
prepared_options AS (
    SELECT
        symbol || '_' || TO_CHAR(expiration_date, 'YYMMDD') || '_' || strike_price::int || '_' || option_type AS contract,
        time AT TIME ZONE 'Asia/Kolkata' AS time,
        symbol,
        open,
        high,
        low,
        close
    FROM options_temp order by contract
)
,
ohlc_data AS (
    SELECT
        ts.contract,
        ts.time,
        po.symbol,
        po.open,
        po.high,
        po.low,
        po.close
    FROM time_series ts
    LEFT JOIN prepared_options po
    ON po.time = ts.time
    AND po.contract = ts.contract
)
SELECT * FROM ohlc_data order by time;


