from big_algo_framework.data.yf import YFData


ticker = "TSLA"
ptype = "mo"
p = "1"
ftype = "d"
f = "1"

hist = YFData(ticker,ptype,p,ftype,f) 
histData = hist.get_historic_stock_data()

print(histData)