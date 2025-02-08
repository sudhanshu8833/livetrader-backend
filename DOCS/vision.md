1. I also want to have hands on experience with go
2. so I was thinking of writing one of the service in go, 
3. I was thinking of writing a pricefeeder in go,
so the responsibility of the price feeder is going to be to update the the timescale db, with new connections, 
4. I know there is going to issues about brokers, since initially i was thinking of writing a brokers module, which I am going to be needing in python for order management, but looks like I would have to take the websockets connection, part from there, and write it in go, 
5. so the responsibility, is going to be to maintain 1000's of tokens stream and add that to timescale db
6. It might seem illogical, since whole of the project is being written in python, and writing this small micronservice in go, can be much worse
7. I am not honestly completely sure, if go would honestly help a lot in this, case, although yeah, loops are super fast in go, .recv() and post processing and getting waiting for new message might be faster, 
8. I just want to write it in go, just for this

9. Some of the parts can't be written in go, because we want the users to code the bot in python, 
10. and the class, which we are going to ask the users to write would be deeply tied to the python objects, though it would be great if we could loop over the candles in go, and then in each loop would be able to check the conditions, in python, since that is the code written by users, dont think there is going to be a way honestly, 
11. the problem, might come when we are trying to analyze 1000's of possible combinations of indicators, go might be magical for those use cases but I dont think we can loop over in go, and check the conditions in python
12. we have solution for this, that we do not analyze each datapoint, but more sparsely distributed inputs, and that way we can significantly reduce the calculations
13. Other idea i have is, giving normal backtest to the user, and then alerting him, that a particular input parameter could have given him this much better results, but for that he will have to subscribe (doing this only 3-4 times per user, most of times we want to tell him, on an average how much better he could have gone if he had used our system)
14. Making prebuilt feature of some regularly used strategy, like straddle, strangle, etc. and giving small input parameters