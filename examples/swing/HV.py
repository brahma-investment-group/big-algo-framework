from big_algo_framework.data.td import TDData
import asyncio
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

async def calculate_hv():
    x = TDData("ANFJZCL8HLAOEJERGC9CJENJPGUVFU60")
    ticker = "DKNG"

    stock_data = await x.get_historic_stock_data(symbol=ticker, period_type="month", period=1, frequency_type="daily", frequency=1)
    stk_df = pd.DataFrame.from_dict(stock_data['candles'])
    stk_df['Log returns'] = np.log(stk_df['close']/stk_df['close'].shift())
    print(stk_df)
    volatility = stk_df['Log returns'].std()*252**.5
    print(stk_df['Log returns'].std())
    print(stk_df['Log returns'].std()*10**.5)
    print(stk_df['Log returns'].std()*20**.5)
    print(stk_df['Log returns'].std()*30**.5)

    # PLOT
    # str_vol = str(round(volatility, 4) * 100)
    #
    # fig, ax = plt.subplots()
    # stk_df['Log returns'].hist(ax=ax, bins=50, alpha=0.6, color='b')
    # ax.set_xlabel("Log return")
    # ax.set_ylabel("Freq of log return")
    # ax.set_title(ticker + " volatility: " + str_vol + " % ")
    #
    # plt.show()

if __name__ == "__main__":
    asyncio.run(calculate_hv())