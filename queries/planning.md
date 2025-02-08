1. we generate a time series, having all the perminute data, except saturday, sunday, and holidays(got from holidays table)
    - we have the data for unique contracts, probably we can make series on all of them, and then left join on both contracts, and time, 
2. we get the data of ohlc for all the contracts, and start left joining on all those contracts
3. now if some contracts do not have inbetween data, we will do coalesce probably to make the middle data