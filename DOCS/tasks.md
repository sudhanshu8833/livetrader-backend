
*** OUR FIRST TARGET IS TO BUILD WORLDS BEST BACKTESTER, THE LITERAL BEST ***

1. adding a functions, for quering db and write db
    - a class object on a table level
    - writing queries for adding data asyncronously, and getting
    - used the existing django environment for this.

1. classes needed for the setup
    - logic class
    - logic base class
    - price feeder class, 

    - now logic class has everything
        - all the obvious logic for strategy
        - base logic, of how to order, and create a entry in db
        - has all the associated value related to state of the operation, positions, orders, pnls etc.
    - logic base class, 
        - just an extension of logic class, only imported by logic class
    - price feeder class
        - gets a logic class object as an argument, 
        - then the price feeder class, make a call to db, to get the index required
        - then it starts iterating on that index, and the instance is stored in db
        - now suppose a position is create on 1-1 relation (on same symbol)=> then no db calls
        - other wise, if other contract, or stock, make that db call, and will be saved in ram
        - now that new contract will have all the properties and methods that the spot contract has, 
        - state will be managed by the base-logic class, 
        - price feeder will only make all the calls, and then have post analysis on the basis of orders/trades.

    - broker class (NOT RIGHT NOW)
        - if we have have broker class object, then the broker should be sent as an argument to base_logic_class, and we will have to probably do it through super method,

    - The query resolution took too much time, which wasn't too much expected, honestly
    
    Next tasks - 
        - backtest feeder class, complete


1. for backtesting, contracts object would be unique for each backtest.
    - since its a temp storage, it gets destroyed, as the backtesting ends
    - for live trading, we can think of reusing the same contract for multiple livetrading sessions, since they have the same data, we do not have to change this, 
    - and everyone will be able to use the same contract
    - yeah, we will have to take some of the properties to the user-space, like is_master, if we want to reuse contract

***todos***
1. correct the index schema, it should only have a indexes, and not stocks, hence remove volume
2. remove positions behind contracts (done)
3. add different orders on the basis of asset_type (done)
4. start making functions to be used in the code.
    - expiries in memory
5. DB recomputation, on the basis of 1 month time chunks
6. try to see if we can generate the timestamp more efficiently, if generating is too expensive, maybe fetching will help
7. precomputation logic for indicators.
8. post analysis, computations.

9. In the frontend as well, we will have to have a sort of error checker, so that if the code, is sort of not correct, the call wouldn't go to the backend.


***GOTO TESTING QUICLY***
1. is_position_opened
2. get_active_position
3. get_atm()
4. contracts, active, inactive, expired
5. pnl handeling


***POSITION MONITORING FUNTIONS***
1. get_opened_positions
2. get_orders
3. cancel_order
4. modify_order

5. get_pnl -> on contract and on portfolio
6. get_realized_pnl
7. get_unrealized_pnl
8. is_position_opened
9. today_pnl, 
10. this_weeks_pnl
11. this_month_pnl
12. this_year_pnl 

1. expiry related functions
    - add all the expiry dates, for nifty and banknifty, in bank nifty
    - functions
        - get closest expiry
        - base binary search function


1. we do not want to loopover everything to calculate the pnl, and not pass the argument as well.
2. One of the ways to calculate the pnl, is to go through all the orders, and get the pnl,
3. or whenever a order, gets filled, we either decrease the protfolio


***TODO'S***
1. restructure a bit of code (2 hours)
    - getting the exit, order, add functions on position level as well, call that function from the contract
    - making the special order functions
    - update positions, logic in positions as well
    - this way we will be able to write this in base positions as well, and would be able to implement the same in other assets also
1. pnl functions (2 hours)
2. expiry functions (2 hours)
4. testing the arch (4 hours)
    - test the pnl calcualtions    
5. options chain (2 hours)
6. db optimisation (2 hours)
    - testing multiple configurations
    - sql optimisation
        - trying to see latency of getting all the options data for index at once
            - configs like, the data through only 4 chunks, make a single index chunk, and then make as many chunks as indexes. (see the efficiency)
            - if not, will go to partial queryies, like getting all the data for a index in 3 months(lifetime of a option)
            - if not, then we can try to get the option contract for a month, with multi expiries (like partial stuffs)
            - if not then we will have to go for individual contracts.

QUERY PLANNING OPTMISATION
1. getting all the data for start to end time
    - time(1 year), symbol
    - or if we can somehow make this really efficient, this would be good as well
2. getting data for 3 months chunk for a symbol
    - time(3 months), symbol
    - what can be the reason for time based chunking
        - ram not being able to get so much data, 
        - so will try to store the data in a python dict object or something, to see the size, (if the ram usage is too high, then only will go for this)
        - we are going to have the data anyways so, its fine
3. getting data for a range
    - getting data for all strike price for a symbol and expiration
        - time(1 year), symbol, expiry
    - getting data for all expiry for a strike price, (not doing, will have queries)
    - getting data, for closest 10 strikes, for all coming expiries
        (maybe this is the wisest honestly, not sure, who would like to go so deep in the money or out the money, not usual atleast)
        - time(1 year), symbol, strike

2. what if we do not have a time on the index, and just getting all the data for a contract, without tim, anyways in options, we want to get all the data
4. getting data for individual strikes, when needed
    - time(chunking)


# NEW IDEA
1. we can probably make a decorator, like @send_to_broker, something like that, or we can use __attr__, when connecting the broker
1. use columnar structure
2. use a 4 prices for each timestamp, for open, high, low, close instead of 4 different columns, (SAVING STORAGE WITH NO problems), we can calculate this easily, we can have the open, price a second before and close price, a second after, for aggregation functions
3. while inserting data, we make sure all the timestamps are available, if there are some none, values somewhere in data, we fill it with appropriate values, data at first to be sanetized, not directly inserting
    - if close is none, but open is not none
    - if all the ohlc is none, 
    - if at the start of the contract the price is none
    - if some timestamps in middle are missing
    (this way we will not have to have the overhead of having holidays in between)
4. create materialized view, maybe the overhead is not too much
5. for options chain, maybe have an additional json column with contract, to get the timestamp data.

1. we are going to index, on the basis of contract_id, 
1. lets make the new schema, completely, for options
    - 1. options_contract
        - contract_id, index, expiration_date, strike_price, option_type, exchange, token
    - 2. options_data
        - contract_id, time, price, volume, oi
    - 3. index_data
        - contract_id, time, price

1. have the raw hyper table in memory, 
    - make materialized views, (maybe)

1. making the schema for new db
    - making the schema
    - making the hypertable
    - adding compression policy
2. then, make the logic to insert data, for 1 month first, and inspect the data
    - if close is none, but open is not none
    - if all the ohlc is none, 
    - if at the start of the contract the price is none
    - if some timestamps in middle are missing
(keep the insert running, will take some seconds)
3. see the latency, have potential improvements
4. then go for in memory optemisation


1. blocking operation (on the basis of if statmen)
    - block_for_day
    - block_till_monthly_expiry
    - block_for_n_days
    - block_this_week
    - block_for_month
    - deactivate the opened the positions

    - block all the functionality, apart from sls, but yeah, cancel all open orders
    - after blocking, all the exit operations, are still allowed, exiting will happen, but no entries

1. functionality to roll a contract, positions, to next expiry
2. pnl functionality, realized pnl, unrealized pnl, correction
    - on buy orders, just subtract (quantity * price - fee)
    - on sell order, just add (quantity * price - fee)

    - other is we are tracking pnls, for tracking pnls, its good enough
    - for tracking pnls, really, we should also account for unrealized profits
    - so portfoilio, values only change when buy/sell order

1. frontend
    - integrate the dashboard we are going to use
    - add the tradingview charts, 
    - I think have an api folder, for the backend apis


1. getting the timestamps, and pricescale.
2. Feature required in charts - 
    - labels (which chart, timeframe change)
    - price scale, timescale
    - hover functionality in orders
    - two types of additions, overlay line charts & other pane line charts 

3. Backend tasks
    - indicators
    - options chain
    - data cleaning
    - pnl limits on strategy level
    - percentage of balance option.