INSERT INTO options_contract_temp (
    contract,available_from , index, expiration_date, strike_price, option_type, exchange, token
)
SELECT DISTINCT
    symbol || '_' || TO_CHAR(expiration_date, 'YYMMDD') || '_' || strike_price::int || '_' || option_type AS contract,
    MIN(time) AS available_from,
    symbol AS index,
    expiration_date,
    strike_price,
    option_type,
    exchange,
    token
FROM options_temp
GROUP BY symbol, expiration_date, strike_price, option_type, exchange, token
ON CONFLICT DO NOTHING;

