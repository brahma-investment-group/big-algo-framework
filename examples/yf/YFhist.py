from big_algo_framework.data.yf import YFData

hist = YFData(symbol="TSLA",
              period_type="mo",
              period="1",
              frequency_type="d",
              frequency="1")
histData = hist.get_historic_stock_data()

print(histData)