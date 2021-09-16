import numpy as np
import pandas as pd

class BIGIndicators():
    def __init__(self):
        pass

    def sma(self, DF, sma_length=10):
        df = DF.copy()
        df["SMA"] = round(df['close'].rolling(window=sma_length, min_periods=sma_length).mean(),5)
        return df

    def ema(self, DF, ema_length=10, adjust=True):
        #adjust=False will calculate the Wilder's MA (Used in ATR)
        df = DF.copy()
        df["EMA"] = round(df['close'].ewm(span=ema_length, min_periods=ema_length, adjust=adjust).mean(),5)
        return df

    def bollingerBands(self, DF, bb_ma_length=20, bb_ma_type="sma"):
        df = DF.copy()

        if bb_ma_type == "sma":
            df["BB_MA"] = round(df['close'].rolling(bb_ma_length).mean(),5)
        else:
            df["BB_MA"] = round(df['close'].ewm(span=bb_ma_length, min_periods=bb_ma_length).mean(),5)

        df["BB_up"] = round(df["BB_MA"] + 2 * df['close'].rolling(bb_ma_length).std(ddof=0),5)
        df["BB_down"] = round(df["BB_MA"] - 2 * df['close'].rolling(bb_ma_length).std(ddof=0),5)
        df["BB_width"] = df["BB_up"] - df["BB_down"]
        df["BB_percentage"] = (df['close'] - df["BB_down"]) / (df["BB_up"] - df['BB_down'])

        return df

    def keltnerChannel(self, DF, kc_ma_length=20, kc_atr_length=20, kc_atr_multiplier=1.5, kc_ma_type="sma"):
        df = DF.copy()
        atr_df = pd.DataFrame()
        atr_df["ATR"] = self.atr(df, kc_atr_length, kc_ma_type)["ATR"]

        if kc_ma_type == "sma":
            df["KC_MA"] = round(df['close'].rolling(kc_ma_length).mean(),5)
        else:
            df["KC_MA"] = round(df['close'].ewm(span=kc_ma_length, min_periods=kc_ma_length).mean(), 5)

        df["KC_up"] = df["KC_MA"] + atr_df["ATR"] * kc_atr_multiplier
        df["KC_down"] = df["KC_MA"] - atr_df["ATR"] * kc_atr_multiplier

        return df

    def rsi(self, DF, rsi_length=14):
        df = DF.copy()
        df['delta'] = df['close'] - df['close'].shift(1)
        df['gain'] = np.where(df['delta'] >= 0, df['delta'], 0)
        df['loss'] = np.where(df['delta'] < 0, abs(df['delta']), 0)
        avg_gain = []
        avg_loss = []
        gain = df['gain'].tolist()
        loss = df['loss'].tolist()

        for i in range(len(df)):
            if i < rsi_length:
                avg_gain.append(np.NaN)
                avg_loss.append(np.NaN)
            elif i == rsi_length:
                avg_gain.append(df['gain'].rolling(rsi_length).mean()[rsi_length])
                avg_loss.append(df['loss'].rolling(rsi_length).mean()[rsi_length])
            elif i > rsi_length:
                avg_gain.append(((rsi_length - 1) * avg_gain[i - 1] + gain[i]) / rsi_length)
                avg_loss.append(((rsi_length - 1) * avg_loss[i - 1] + loss[i]) / rsi_length)

        df['avg_gain'] = np.array(avg_gain)
        df['avg_loss'] = np.array(avg_loss)
        df['RS'] = df['avg_gain'] / df['avg_loss']
        df['RSI'] = round(100 - (100 / (1 + df['RS'])),5)
        return df

    def atr(self, DF, atr_length=14, atr_ma_type="ema", adjust=False):
        df = DF.copy()
        df['H-L'] = abs(df['high'] - df['low'])
        df['H-PC'] = abs(df['high'] - df['close'].shift(1))
        df['L-PC'] = abs(df['low'] - df['close'].shift(1))
        df['TR'] = df[['H-L', 'H-PC', 'L-PC']].max(axis=1, skipna=False)

        if atr_ma_type == "sma":
            df['ATR'] = round(df['TR'].rolling(atr_length).mean(),5)
        else:
            df['ATR'] = round(df['TR'].ewm(min_periods=atr_length, alpha=1/atr_length, adjust=adjust).mean(),5)

        return df

    def MACD(self, DF, fast_ma=12, slow_ma=26, signal_ma=9):
        df = DF.copy()
        df['MA_Fast'] = df['close'].ewm(span=fast_ma, min_periods=fast_ma).mean()
        df['MA_Slow'] = df['close'].ewm(span=slow_ma, min_periods=slow_ma).mean()
        df['MACD'] = df['MA_Fast'] - df['MA_Slow']
        df['Signal'] = df['MACD'].ewm(span=signal_ma, min_periods=signal_ma).mean()
        df['Direction'] = np.where(df['MACD'] >= df['Signal'], "Bullish", "Bearish")

        return df