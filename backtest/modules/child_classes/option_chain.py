from pydantic import BaseModel

class OptionChain(BaseModel):
    pass 


'''
look the problem is, we can probably index, the symbol in options, and that should give up the options, we are requesting, pretty efficintly

    first of all what operations, might user want on the basis of options, chain
    - get the strike price, in ce which is closest to premium 100, <80, etc

    - if a person asking for any data related to contract it is easy, which has already been defined
    - the active contracts are updated everytime

    - if we go for a similar solution, here, and get the option chains, it would be tough
    - it would be like updating 1000's of contracts at once

    - but we need to give this functionality, 

    - consider List[optionchain] to be a property of a index
    - now, if we need to maintain all the option chain on each candle update it would be tough
    - so, we are going to do lazy loading
    - now, we can't get all the option, chains at once, with all the 1m candles data, (100's millions rows)
    - but in-memory, we can have all the contracts, that was possible, like a contracts manager


    start with the user, what functionality we want to give to the user, write the code
    1. self.index.get_option_chain(self.index.get_current_expiry())
        - Index: List[OptionChain]
        - OptionChain: List[Contracts]

        each contract is going to have this values,
            - ltp, oi, volume, 
            - no candles for this contracts, (100% sure, unnecessary)
            - 

            - kal ko koi aisa na aajaye jo bole, ki option chain m aisa option, nikalo jisme sma 14 50 se upar ho :crying
            - we can't fix all the things, anyways

    for live trading this is easy, but for backtesting, updating the contracts, on each price, is difficult,

    so, if we see that someone is requiring the option chain in backtesting, they are going to be requiring it for a good part, so we should just fetch all the option, chains in the specific period, 
    and make all the option chains, as the preprocessing (maybe will take 3-4 seconds extra)
    we should design it in a way, that, we do not need the candles price, 

    but this Contracts would be like this -

    'time_stamp': {
        'expiry': {
            'strike_price': {
                'option_type': {
                    'ltp': 100,
                    'oi': 100,
                    'volume': 100
            }
        }
    }
'''
