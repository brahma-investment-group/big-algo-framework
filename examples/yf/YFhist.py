from big_algo_framework.data.yf import YFData

ticker = "TSLA"
hPeriod = "1y"
hInterval = "1d"

#hist = YFData(ticker)
histData = YFData.get_historic_stock_data(ticker, period=hPeriod, interval=hInterval)

#hist = ticker.history(period=hPeriod, interval=hInterval, start=None, end=None)

print(histData)