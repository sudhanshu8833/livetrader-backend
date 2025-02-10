1. python never deals with timezone, whole responsibility of timezone is on psql (because we can handle it there, okay)
2. even during migrations, make sure we are getting time in IST, so that we have consistency in python


# USABLE ||
SELECT time::date AS last_trading_day
FROM options_data
WHERE time < '2024-03-07'
AND EXTRACT(DOW FROM time) NOT IN (6, 0)
AND time::date NOT IN (SELECT holiday_date FROM market_holidays)  -- Exclude holidays
ORDER BY time DESC
LIMIT 1;


# POSSIBLE OPTIMIZATIONS
1. no timestamp series making (maybe 1-2 seconds saved)
2. not converting all the candles to objects (1-2 seconds saved)
3. prefetching data through heuristics (2-3 seconds saved)
4. having bulk updates(like 10 candles at once) -> since some of the functions do not requires per minute updates
5. getting some ideas from vectorbt

FROM HERE WE CAN HAVE LOSSY LATENCY IMPROVEMENTS
1. having less data to process(lossy resolution) -> speed increment



# TODO'S 04/FEB/2024
1. serialization issue resolution
2. analysis dashboard, basic completion with
    - a couple of good looking graphs
    - a couple of good looking cards for data points

    1. adding candles and orders on the chart
    2. making some good graphs, and all
    3. making some good data points
3. Debugging the results
4. data migration and cleaning, if time range needed okay

# TODO'S 06/FEB/2024
1. Data cleaning (IMP)
    - holidays table making (EXCHANGE, DATE)
    - filling important data
        - in between ohlc data
            (try to do everything within psql) (we have every information to do that)

so the problem, is when the data starts, and we do not have any prior data, but the logic asks it, we will have to handle this situation, by not doing anything related tasks, so a buy/sell etc wont happen, probably add a warning message somehow
1. if a trade has happened on that, we will try to fill, all the mid values, with previous close, okay (a straight line) (with no holidays)
2. if there are some nan values in the row, open is there but not close, 
    - we are assuming, this can only happen to open, so if there is open, but not other we will fill other with the same value

1. giving 1 hours to data cleaning (hopefully we will be able to atleast get the data in the table)
2. giving 2 hours to writing more functions except options_chain.
3. giving 2 hours to frontend 
    - getting the tables ready for positions/orders
    - getting tables ready for analysis results (like max drawdown, calmars, w/L)
    - component to show the profits or loss in a very attractive way

1. need to fill null values now
    - so if a row is missing, fill the values with previous close
    - if open is present, fill the other column of same row with the open price
    - if volume is not present set the value to 0
    - if oi is not present set the value to previous oi


# TODO'S 07th FEB
1. adding some function in the logic

1. Categories of functions we have
    - CORE FUNCTIONS (_update_contract, get_contract, panic_button, update_portfolio)
    - PNL functions (get_todays_pnl, all_time_pnl, pnl_maps management, realized unrealized pnl)
    - Blocking functions (block_for_day, block, block_for_week, block_for_month, unblock)
    - expiry functions (all the expiry functions)

***NEW-FUNCTIONS***
1. pnl-limits daily, weekly, monthly
2. 

1. Dont think much of comparison overheads for now, will later refactor it, right now only look to try keeping the execution in O(n) 


# INDICATOR 
1. we should build a class called IndicatorFactory
2. we can probably use, self.sma.value(0/1/2)
3. so, we should make methods like, get_indicator()
4. and after initiating the strategy object, we will be able to get the names of all the indicators with the argument, 
5. Then will go to indicatorFactory, which will convert the output of db into array, and then will convert it to df, on that df, will run the indicators needed, 
6. lets try to integrate TA-Lib and vectorbt, so this way we will have support of a lot of indicators along with the power to have a lot of instances of indicators

