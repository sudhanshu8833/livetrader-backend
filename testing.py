import talib
import numpy as np
import time
c = np.random.randn(100000000)
start_time = time.time()

# this is the library function
k, d = talib.STOCHRSI(c)

# this produces the same result, calling STOCHF
rsi = talib.RSI(c)
k, d = talib.STOCHF(rsi, rsi, rsi)

# you might want this instead, calling STOCH
rsi = talib.RSI(c)
k, d = talib.STOCH(rsi, rsi, rsi)
print("--- %s seconds ---" % (time.time() - start_time))
