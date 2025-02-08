***TODO'S***
1. we need to have the binance client completely ready
    - should have the websocket option
    - historical data
    - lets go for a single file for both websockets and rest-client(simpler)
    - everything to be asyncronous
2. After that focus on backtesting, and calling back to the logic class, we can't give asyncronous call to each of the candle, since its a stateful activity
3. so we will need to go 1 by 1, 
4. if there are multiple symbols involved we can definitely do the calls, more then once

5. For live trading we will place a middleware between the logic class and the broker class, to save the data to disk (postgres)
    - since in backtesting, we do not want to save the positions, and orders to the disk, 
    - although this can also be solved by having a variable , like if backtesting (no writing on db)
7. should we learn vim later???
6. Never try to Learn multiple things at a time, suppose building a Go project in vim, wouldn't be good, since you would have to learn Go and vim together
8. Or since it is a good project we should start coding in neovim only
9. Huh, there is copilot here though, if we go there this is the main issue, so lets keep it here for now
10. we will map the api keys


***TODO'S***
1. we are going to try build the backtesting model, The backtesting for options, by keeping in mind the stocks
2. There are bascically two types of backtesting 
    - linear -> analysis on 1 symbol -> order on same symbol
    - non-linear -> run analysis on 1 symbol, order on the other contract (other, can be anything)
    - squaring off positions can have two basis 
    - will maintain a contracts thing, and in the code we will signify a special type of contract
3. specially just for backtesting, we just need the historical data (like for index and stocks)
4. right now, will only focus on NIFTY, BANKNIFTY etc, 


- Right now I will just have the data, just need to figure-out how will have this data
- there will be a datafeeder, whose whole responsiblity will be to take the instance object as argument, and call on_data update call, 
- will figure out what should be the data fields necessary (make the data compatible for both backtesting and live trading)
- Whole state will be managed by the Logic class, Logic class will import from a parent class, which will have some functions defined, for buying selling, and statemanagement
- The data, we are updating can be an array, of the positions taken, and the initial spot, (we are building something lightweight)

*TASKS*
- Figureout how we will we get the data in the price-feeder
- Make the the base-library LTStrategy
    Functions in the base-library
    - order_function
    - indicators
    - get_holdings
    - get_orders
    - data-management
        - so add the data as soon as the function is called
        - the global data, for this will be a object, (an array of objects maybe)
        - so in an object we will be able to signify, self.data.high(0), self.data.volume(-1) # will try to keep the python standards
    - pnl - Example (self.pnl([self.option_call, self.option_sell], percentage, 5)) similar kind of functions
    - self.profit
    - self.loss etc, faltu ke aur bhi functions add kar sakte hai
    - self.state - {
        'positions':[],
        'orders':[],
        'realized_pnl':,
        'unrealized_pnl':
        etc etc.
    }
- reports making
    - after analysis, in case of backtesting, right now, we are only considering MARKET ORDERS
    - the orders, again will be a object, as well as positions
    - maybe make a object on the contract-level, 
        - so a contract in the backtesting can have following things
            - orders
            - positions
            - candles
            - price

    - before on-data we will update the data - (data variable will be stored in price_feeder, and sent as argument)
    - when we will get the update, self.data.high(0) etc, this will be of spot only,
    - in the positions taken in the options, we should be able to do this things as well,
    - so while opening the position, on a contract, if there are no objects created for that particular symbol, we will create a object for that symbol, and that will be saved in a variable
    - user can name them, such as self.option_call, or self.option_call_hedge, etc
    - and when we get the update, all the created positions, should also get updated, so that these objects has the latest data
    - no run time_errors, that suppose in some cases if the self.option_call is referenced before assignment, since the position is not being created right now, that will be a users error, honestly, 
    - but since a single function is responsible for all the data, when we write a function, he can put write like 

    function on_data(self, data){
        if self.data.high(0) > self.data.low(0):
            symbol = {
                expiry: self.get_expiry(0) # latest expiry
                strike: self.data.ltp + self.price
                option_type: ce
            }
            contracts = {
                type: percentage / amount
                value: 20
            }
            self.option_ce_buy = self.order(symbol, buy, contracts)

        if self.data.high(0) < self.data.low(0):
            square_off = {
                type: percentage / amount
                value
            }

            # now the question is, if the self.option_ce_buy isn't declared yet
            we can add __get_attribute__ function for this
            self.option_ce_buy.close(5/square_off)

        # if self.option_ce_buy isn't declared, is there a possibility that we can ignore this, it would just consider it false by default
        else if self.option_ce_buy.pnl(5):
            self.option_ce_buy.close()
    }

    - should add the option for stoploss, and take profit at the starting the position
    - maybe later we can give them the option, that they can input a range of parameters to test
    - Provide reasonable defaults so users don’t have to define every detail for simple strategies.
    - How we will store the data and fetch the data
    - so right now, what i think is right is, so, there will be a startime, and end time, we will start iterating from starttime, and with loops every 60 secs, we will try to make as less queries as possible, so we will get the data at once, in memory, and suppose if we make a new position, whose data is not there in options, we will again make a query, 
    - we will index the data on the basis of timestamp, so that we will be able to get the range queries fastly, 
    - questions in context of timescale db is, should we make 1000's of table for each contract, right now, I think its a good idea, we will be able to fetch the table we want on the basis of contracts information, okay good idea and range queries, then we will probably iterate over that data, which will already be in, and we should probably have a key:value store in memory, since if we are going to iterate over time, we should be able to call a timestamp to get the value, having (open, high, low, close, volume), 
    - and then we should call the on_data callback, with latest array of data, with the spot and indices

    data fields 
    {
        open:
        high:
        low:
        close:
        volume:
        candle_close :True/False
        ... other_fundamental_data
    }

    - when going live, only a live-price feeder will be used instead of a loop
    - and in the order section, the logic class, will also be tied to a broker (optionally), if the self.backtest is false, and self.broker is setup, we will throw that order on live


    TILL WE GET THE DATA, WHAT SHOULD WE DO

    - get the posgressql, timescale db, setup, 
    - we will be making an application, for price feeder
    - that will have multiple endpoints related to price feeder


    ***IDEAS***
    1. we can just make a custom logic class, to give a UI to the users to backtest there system
    2. we can give users an ability to give a range of indicators input range, to test on multiple values at once, This might take longer to perform
    3. while coding we have to understand and test, which part is taking more time, such as memory allocation, memory reference, object creation, function putting in stack, and those kind of things
    4. we can think of integrating other python libraries to give more functionality for testing a algorithm
    5. writing a function like `self.distance_from_expiry()`, or `self.is_expiry(0)` etc
    8. and if today is expiry need to close the position, when the day ends, if any positions are opened


    ***class_setup***
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


    - so the problem is, people will ask for 5 min candles,
    
    - lets explain the functinality I will need, 
    - 1 min- I would need candle_close - false, along with the 1 min open-high-low-close-volume data.
    - 2 min - I would need 2 min last 2 min open, high, low, close data
    - 3 min - I would need 3 min last 3 min open, high, low close data
    - 4 min - I would need 4 min, last 5 min, open high low close 
    - 5 min, I would need 5 min, last open high low close data, 
    - and I would need to handle non-availability of data, 


***THOUGHTS***
1. we can have two types of candles
    - Index
    - Options
    - for both we will have a pydantic class, and we will return a list of objects of that class, 
    - so that price feeder can iterate over those class
    - there are two types of queries, one which just sending the candles, the other which is sending rolling integrated things, 
    - for backtesting we will have the rolling thing,
    - where should we have objects
        - definitely candle level
        - then we will have a contract level - which will have all the candles, and indicators above those candles, indicators will be calculated at this level, the candles will come on each iteration.
        - contracts will be a property of Logic class
        - the base strategy, will maintain a state where, it will have a contracts section, about which are the active contracts we need to keep looking at, 
        - then above that we will have a backtest level class
            - this class, will have raw data first of all, got from initial fetching through db, and saved in ram
            - and whenever there is a new contract addition in strategy, we will fetch that contract as well from the db and save it in mem

    - we should try to give range inputs in indicators
    - we should try to leverage numba capabilities
    - maybe for UI I can build a more optimised program
        - UI -> similar to vectorBT
        - code -> similar to backtrader


backtest feeder -
    - candles fetch from db
    - new candles fetching
    - updating the state of the active contracts
    - interating over candles, on 60 sec interval

    - is backtest-feeder a stateful thing, no??
    - it kind of is, but active contracts should belong to Strategy, since Strategy is managing all the active states
    - though the state of contracts is updated by backtest-feeder, the contracts should belong to Strategy
    - whoever it belong to, we atleast have to call two functions, 
        - first, to update the contracts, which will map a Strategy class function to update the contracts with new data, 
        - second, to call the callback_function, with no arguments, since the state is already been updated
    - in the contract updation, we can either add a candle, or update the existing latest candles price, since that will be responsible for ltp as well,

strategy -> contracts -> candles 

- now, the order and positions, will also belong to a contract, along with trades, pnl,


        ***FUNCTIONALITIES OF THE LOGIC CLASS***
        open, high, low, close, volume, oi,
        order

        > time, < time
        is_position_opened
        is_candle_closed
        get_atm_strike
        get_high_oi_strike (option chain based calculations)
        get_open positions.
        get_pnl
        roll_position_to_next_expiry
        stoploss, and takeprofit orders in place.
        get_orders
        is_trading_day

        # index to be connected to the option, contracts
        # the problem is right now, we only have access to indexes, and not options
        # we will have to save all the expiries in memory, while loading
        # so it will be like expiries = {
            'NIFTY' : [],
            'BANKNIFTY, [], 
            etc:
        }

        # should make bunch of functions which return expiries
        1. self.index.current_expiry
        2. self.index.next_expiry
        3. self.index.coming_expiries[2]
        4. self.index.monthly_expiry
        4. self.contract.has_expired
        5. self.contract.is_expiry_today

        # then make wrapper functions on those
        1. self.distance_from_expiry(takes expiry date)


        1. self.get_option_chain()
            here, we can loop over the option_chain, to get the strike price we want, we only fetch the option, chains if we need it
        2. roll to next expiry


        1. One thing we need to stop doing, is speculating, that this is going to be faster, and it is going to be slower, we just dont know until we tried, it, so fucking try it, 
        2. Now my prime focus is getting the basic backtesting program ready.


*** need to manage gaps in candles ***
1. 1 problem can be if there are gaps in time, we need just add the last candle with updated timestamp, will try to handle it on db level only
2. holidays handeling

(***HANDELLED***)


### BUSINESS IDEAS ###
1. we can price our backtest on the basis of compute time
(instead of number of backtests)
2. and on the basis of db calls

1. Blocking operation


1. Have a read of vectorbt, I am sure there are a lot of things we can leverage for speed and functionality, not only that, there are many new low level ideas to work on


1. how do we give enough options in a strategy, for them to really make it
    - after main configs selection what are there in options strategy
    - Entry condition
        - can be based on time
        - can be based on indicator value
        - can be based on if we already have a positions open
        - can be based on candles
        - can be based on pnl values (daily pnl)
        - can we based on if we have a hard limit on the number of positions
        - can be based on some other projects we registered
        - Add custom scripting for advanced users (if (close > open && rsi > 60) { enterTrade(); })
    - add position condition
        - similar to the entry condition
    - exit condition
        - pnl and every thing

To make this process simpler, I think we shouldn't ask for so many information at once

1. first we should take information amount the flavous of the strategy
    - like what timeframe to select (or we don't need it at all)
    - what index do we select
    - backtesting start time, end time
    - pnl limits (position wise, daily, weekly, monthly) (blocked if crosses)
    - initial cash
    - lot size
        - on the basis of percentage of portfolio
        - straign number
        - on the basis of investment on each entry

    - stoploss, takeprofits, and trailing stoploss, we can have a default value for all this

2. Then we go to the next tab
    - how do we enter a trade
    - Here we need to make a formula maker
        - should be able to select multiple conditions
        - like if close>open and atr>3
    - Then there will be a trigger
    - In trigger itself
        - either we can trigger a buy/sell on the same contract
        - or we can get a new contract to trigger the orders on

3. Exit a trade
    - again a formula maker
    - and then trigger, just here, we are going to exit the opened position
    - although there can be positions opened on multiple contracts
    - so we will need to give an option to select which contract to sell


