
        WITH market_time_series AS (
            SELECT time
            FROM generate_series(
                    date_trunc('day', TIMESTAMP '2024-01-27 07:31:41.400980') + INTERVAL '9 hours 15 minutes',
                    date_trunc('day', TIMESTAMP '2024-12-27 07:31:41.400987') + INTERVAL '15 hours 30 minutes',
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
            
            token,
            FLOOR((EXTRACT(EPOCH FROM time) + 1800) / 300) AS minute_group
        FROM index
        WHERE time >= '2024-01-27 07:31:41.400980'
        AND time < '2024-12-27 07:31:41.400987'
        AND symbol = 'NIFTY'
        
        
        
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
    