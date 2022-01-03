import numpy as np
import pandas as pd
import pandas_ta as ta

class BIGIndicators():
    def __init__(self):
        pass

    def sma(self, DF, length=10):
        df = DF.copy()
        df = df.ta.sma(close=df["close"], length=length)
        return df

    def ema(self, DF, length=10, adjust=True):
        #adjust=False will calculate the Wilder's MA (Used in ATR)
        df = DF.copy()
        df = df.ta.ema(close=df["close"], length=length, adjust=adjust)
        return df

    def bollingerBands(self, DF, length=20, std=2, mamode="sma"):
        df = DF.copy()

        df = df.ta.bbands(length=length, std=std, mamode=mamode)
        df = df.rename(columns={"BBL_{}_{:.1f}".format(length, std, 1): "LBB",
                                "BBM_{}_{:.1f}".format(length, std, 1): "MBB",
                                "BBU_{}_{:.1f}".format(length, std, 1): "UBB",
                                "BBB_{}_{:.1f}".format(length, std, 1): "BBW",
                                "BBP_{}_{:.1f}".format(length, std, 1): "BBP"})
        return df

    def keltnerChannel(self, DF, length=20, scalar=2, mamode="sma", tr=True):
        df = DF.copy()

        df = df.ta.kc(length=length, scalar=scalar, mamode=mamode, tr=tr)
        df = df.rename(columns={"KCLs_{}_{:.1f}".format(length, scalar, 1): "LKC",
                                "KCBs_{}_{:.1f}".format(length, scalar, 1): "MKC",
                                "KCUs_{}_{:.1f}".format(length, scalar, 1): "UKC"})

        return df

    def rsi(self, DF, length=14):
        df = DF.copy()
        df = df.ta.rsi(length=length)
        return df

    def atr(self, DF, length=14, mamode="ema"):
        df = DF.copy()
        df = df.ta.atr(length=length, mamode=mamode)
        return df

    def MACD(self, DF, fast_ma=12, slow_ma=26, signal_ma=9):
        df = DF.copy()
        df['MA_Fast'] = df['close'].ewm(span=fast_ma, min_periods=fast_ma).mean()
        df['MA_Slow'] = df['close'].ewm(span=slow_ma, min_periods=slow_ma).mean()
        df['MACD'] = df['MA_Fast'] - df['MA_Slow']
        df['Signal'] = df['MACD'].ewm(span=signal_ma, min_periods=signal_ma).mean()
        df['Direction'] = np.where(df['MACD'] >= df['Signal'], "Bullish", "Bearish")

        return df