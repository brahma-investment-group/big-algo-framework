import pandas as pd

class strategyRules():
    def __init__(self, ticker, df):
        self.ticker = ticker
        self.df = df

    def becomes_ftfc_at_price(self, price):
        open1 = self.df['open'].iloc[-1]

        if price >= open1:
            return "Bullish"

        if price <= open1:
            return "Bearish"

    def is_not_ib(self, higher_price, lower_price):
        close1 = self.df['close'].iloc[-1]

        if close1 > higher_price or close1 < lower_price:
            return True
        else:
            return False

    def get_strat_scenarios(self):
        scenarios = []
        scenario = ""

        for i in range(1, 4):
            open1 = self.df['open'].iloc[-i]
            high1 = self.df['high'].iloc[-i]
            low1 = self.df['low'].iloc[-i]
            close1 = self.df['close'].iloc[-i]

            high2 = self.df['high'].iloc[-i-1]
            low2 = self.df['low'].iloc[-i-1]



            if high1 <= high2 and low1 >= low2:
                if close1 > open1:
                    scenario = "insidebargreen"

                elif close1 < open1:
                    scenario = "insidebarred"

            elif high1 > high2 and low1 < low2:
                if close1 > open1:
                    scenario = "outsidebargreen"

                elif close1 < open1:
                    scenario = "outsidebarred"

            elif high1 > high2 and low1 > low2:
                if close1 > open1:
                    scenario = "twoupgreen"

                elif close1 < open1:
                    scenario = "twoupred"

            elif high1 < high2 and low1 < low2:
                if close1 > open1:
                    scenario = "twodowngreen"

                elif close1 < open1:
                    scenario = "twodownred"

            else:
                scenario = "Not A Valid Scenario"

            scenarios.append(scenario)

        return scenarios

    def get_bullish_strat_pattern(self):
        scenarios = self.get_strat_scenarios()

        datetime1 = self.df['date_time'].iloc[-1]
        dict = {}

        if (scenarios[2] == "insidebargreen" or scenarios[2] == "insidebarred") and \
                (scenarios[1] == "insidebargreen" or scenarios[1] == "insidebarred"):
        #and \ (scenarios[0] == "twoupgreen" or scenarios[0] == "outsidebargreen"):

            dict = {"pattern": "BullishDoubleInside",
                    "patternType": "reversal",
                    "direction": "Bullish",
                    "dt": datetime1}

        elif (scenarios[2] == "twodowngreen" or scenarios[2] == "twodownred") and \
                (scenarios[1] == "insidebargreen" or scenarios[1] == "insidebarred"):

            dict = {"pattern": "Bullish212",
                    "patternType": "reversal",
                    "direction": "Bullish",
                    "dt": datetime1}

        elif (scenarios[1] == "twodowngreen" or scenarios[1] == "twodownred"):

            dict = {"pattern": "Bullish22",
                    "patternType": "reversal",
                    "direction": "Bullish",
                    "dt": datetime1}

        elif (scenarios[2] == "outsidebarred") and \
                (scenarios[1] == "insidebargreen" or scenarios[1] == "insidebarred"):

            dict = {"pattern": "Bullish312",
                    "patternType": "reversal",
                    "direction": "Bullish",
                    "dt": datetime1}

        elif (scenarios[2] == "insidebargreen" or scenarios[2] == "insidebarred") and \
                (scenarios[1] == "twodowngreen" or scenarios[1] == "twodownred"):

            dict = {"pattern": "Bullish122",
                    "patternType": "reversal",
                    "direction": "Bullish",
                    "dt": datetime1}

        elif scenarios[1] == "twoupgreen":
            dict = {"pattern": "Bullish2U2U",
                    "patternType": "continuation",
                    "direction": "Bullish",
                    "dt": datetime1}

        elif (scenarios[1] == "insidebargreen" or scenarios[1] == "insidebarred"):
            dict = {"pattern": "Bullish12U",
                    "patternType": "continuation",
                    "direction": "Bullish",
                    "dt": datetime1}

        elif scenarios[1] == "outsidebargreen":
            dict = {"pattern": "Bullish32U",
                    "patternType": "continuation",
                    "direction": "Bullish",
                    "dt": datetime1}

        elif scenarios[1] == "outsidebarred":
            dict = {"pattern": "Bullish32D",
                    "patternType": "reversal",
                    "direction": "Bullish",
                    "dt": datetime1}

        else:
            dict = {"pattern": "",
                    "patternType": "",
                    "direction": "",
                    "dt": datetime1}

        return dict

    def get_bearish_strat_pattern(self):
        scenarios = self.get_strat_scenarios()

        datetime1 = self.df['date_time'].iloc[-1]
        dict = {}

        if (scenarios[2] == "insidebargreen" or scenarios[2] == "insidebarred") and \
                (scenarios[1] == "insidebargreen" or scenarios[1] == "insidebarred"):
                # and \ (scenarios[0] == "twodownred" or scenarios[0] == "outsidebarred"):

            dict = {"pattern": "BearishDoubleInside",
                    "patternType": "reversal",
                    "direction": "Bearish",
                    "dt": datetime1}

        elif (scenarios[2] == "twoupgreen" or scenarios[2] == "twoupred") and \
              (scenarios[1] == "insidebargreen" or scenarios[1] == "insidebarred"):

            dict = {"pattern": "Bearish212",
                    "patternType": "reversal",
                    "direction": "Bearish",
                    "dt": datetime1}

        elif (scenarios[1] == "twoupgreen" or scenarios[1] == "twoupred"):

            dict = {"pattern": "Bearish22",
                    "patternType": "reversal",
                    "direction": "Bearish",
                    "dt": datetime1}

        elif (scenarios[2] == "outsidebargreen") and \
                (scenarios[1] == "insidebargreen" or scenarios[1] == "insidebarred"):

            dict = {"pattern": "Bearish312",
                    "patternType": "reversal",
                    "direction": "Bearish",
                    "dt": datetime1}

        elif (scenarios[2] == "insidebargreen" or scenarios[2] == "insidebarred") and \
                (scenarios[1] == "twoupgreen" or scenarios[1] == "twoupred"):

            dict = {"pattern": "Bearish122",
                    "patternType": "reversal",
                    "direction": "Bearish",
                    "dt": datetime1}

        elif scenarios[1] == "twodownred":
            dict = {"pattern": "Bearish2D2D",
                    "patternType": "continuation",
                    "direction": "Bearish",
                    "dt": datetime1}

        elif (scenarios[1] == "insidebargreen" or scenarios[1] == "insidebarred"):
            dict = {"pattern": "Bearish12D",
                    "patternType": "continuation",
                    "direction": "Bearish",
                    "dt": datetime1}

        elif scenarios[1] == "outsidebarred":
            dict = {"pattern": "Bearish32D",
                    "patternType": "continuation",
                    "direction": "Bearish",
                    "dt": datetime1}

        elif scenarios[1] == "outsidebargreen":
            dict = {"pattern": "Bearish32U",
                    "patternType": "reversal",
                    "direction": "Bearish",
                    "dt": datetime1}

        else:
            dict = {"pattern": "",
                    "patternType": "",
                    "direction": "",
                    "dt": datetime1}

        return dict

    def isRevStratPattern(self, atr):
        open1 = self.df['open'].iloc[-1]

        high1 = self.df['high'].iloc[-1]
        high2 = self.df['high'].iloc[-2]
        high3 = self.df['high'].iloc[-3]
        high4 = self.df['high'].iloc[-4]

        low1 = self.df['low'].iloc[-1]
        low2 = self.df['low'].iloc[-2]
        low3 = self.df['low'].iloc[-3]
        low4 = self.df['low'].iloc[-4]

        close1 = self.df['close'].iloc[-1]

        datetime1 = self.df['date_time'].iloc[-1]

        bullishGap = abs(open1 - high2)
        bearishGap = abs(open1 - low2)
        dict = {}

        if low3 > low2 and high3 > high2 and low2 < low1 and high2 < high1 and high2 < close1:
            dict = {"pattern": "Bullish22",
                    "patternType": "reversal",
                    "direction": "Bullish",
                    "entry": high2 + 0.01,
                    "sl": low2 - 0.01,
                    "dt": datetime1}

            if bullishGap < 0.5 * atr:
                dict["entry"] = round(open1 + 0.01, 2)

            return dict

        elif low3 > low2 and high3 > high2 and high2 < close1 and high2 < high1 and low2 > low1:
            dict = {"pattern": "Bullish23",
                    "patternType": "reversal",
                    "direction": "Bullish",
                    "entry": high2 + 0.01,
                    "sl": low1 - 0.01,
                    "dt": datetime1}

            return dict

        elif low4 > low3 and high4 > high3 and low3 < low2 and high3 > high2 and high2 < high1 and high2 < close1 and low2 < low1:
            dict = {"pattern": "Bullish212",
                    "patternType": "reversal",
                    "direction": "Bullish",
                    "entry": high2 + 0.01,
                    "sl": low2 - 0.01,
                    "dt": datetime1}

            if bullishGap < 0.5 * atr:
                dict["entry"] = open1 + 0.01

            return dict

        elif high4 < high3 and low4 > low3 and high3 > high2 and low3 < low2 and high2 < high1 and low2 < low1 and high2 < close1:
            dict = {"pattern": "Bullish312",
                    "patternType": "reversal",
                    "direction": "Bullish",
                    "entry": high2 + 0.01,
                    "sl": low2 - 0.01,
                    "dt": datetime1}

            if bullishGap < 0.5 * atr:
                dict["entry"] = open1 + 0.01

            return dict

        elif low3 < low2 and high3 > high2 and low2 > low1 and high2 < close1 and high2 < high1 and close1 > open1:
            dict = {"pattern": "Bullish13",
                    "patternType": "reversal",
                    "direction": "Bullish",
                    "entry": high2 + 0.01,
                    "sl": low1 - 0.01,
                    "dt": datetime1}

            return dict

        elif high4 < high3 and low4 < low3 and high3 > high2 and low3 < low2 and high2 < close1 and high2 < high1 and low2 < low1 and close1 > open1:
            dict = {"pattern": "Bullish2U12U",
                    "patternType": "continuation",
                    "direction": "Bullish",
                    "entry": high2 + 0.01,
                    "sl": low2 - 0.01,
                    "dt": datetime1}

            if bullishGap < 0.5 * atr:
                dict["entry"] = open1 + 0.01

            return dict

        elif low3 < low2 and high3 < high2 and high2 < high1 and low2 < low1 and high2 < close1 and close1 > open1:
            dict = {"pattern": "Bullish2U2U",
                    "patternType": "continuation",
                    "direction": "Bullish",
                    "entry": high2 + 0.01,
                    "sl": low2 - 0.01,
                    "dt": datetime1}

            return dict

        elif low3 > low2 and high3 < high2 and low2 < low1 and high2 < high1:
            dict = {"pattern": "Bullish32U",
                    "patternType": "continuation",
                    "direction": "Bullish",
                    "entry": high2 + 0.01,
                    "sl": low2 - 0.01,
                    "dt": datetime1}

            if bullishGap < 0.5 * atr:
                dict["entry"] = open1 + 0.01

            return dict

        elif low3 < low2 and high3 < high2 and low2 > low1 and low2 > close1 and high2 > high1:
            dict = {"pattern": "Bearish22",
                    "patternType": "reversal",
                    "direction": "Bearish",
                    "entry": low2 - 0.01,
                    "sl": high2 + 0.01,
                    "dt": datetime1}

            if bearishGap < 0.5 * atr:
                dict["entry"] = open1 - 0.01

            return dict

        elif low3 < low2 and high3 < high2 and high2 < high1 and low2 > close1 and low2 > low1:
            dict = {"pattern": "Bearish23",
                    "patternType": "reversal",
                    "direction": "Bearish",
                    "entry": low2 - 0.01,
                    "sl": high1 + 0.01,
                    "dt": datetime1}

            return dict

        elif low4 < low3 and high4 < high3 and high3 > high2 and low3 < low2 and low2 > low1 and low2 > close1 and high2 > high1:
            dict = {"pattern": "Bearish212",
                    "patternType": "reversal",
                    "direction": "Bearish",
                    "entry": low2 - 0.01,
                    "sl": high2 + 0.01,
                    "dt": datetime1}

            if bearishGap < 0.5 * atr:
                dict["entry"] = open1 - 0.01

            return dict

        elif high4 < high3 and low4 > low3 and high3 > high2 and low3 < low2 and low2 > low1 and low2 > close1 and high2 > high1:
            dict = {"pattern": "Bearish312",
                    "patternType": "reversal",
                    "direction": "Bearish",
                    "entry": low2 - 0.01,
                    "sl": high2 + 0.01,
                    "dt": datetime1}

            if bearishGap < 0.5 * atr:
                dict["entry"] = open1 - 0.01

            return dict

        elif low3 < low2 and high3 > high2 and low2 > low1 and low2 > close1 and high2 < high1 and close1 < open1:
            dict = {"pattern": "Bearish13",
                    "patternType": "reversal",
                    "direction": "Bearish",
                    "entry": low2 - 0.01,
                    "sl": high1 + 0.01,
                    "dt": datetime1}

            return dict

        elif low4 > low3 and high4 > high3 and low3 < low2 and high3 > high2 and low2 > low1 and high2 > high1 and low2 > close1 and close1 < open1:
            dict = {"pattern": "Bearish2D12D",
                    "patternType": "continuation",
                    "direction": "Bearish",
                    "entry": low2 - 0.01,
                    "sl": high2 + 0.01,
                    "dt": datetime1}

            if bearishGap < 0.5 * atr:
                dict["entry"] = open1 - 0.01

            return dict

        elif low3 > low2 and high3 > high2 and high2 > high1 and low2 > close1 and low2 > low1 and close1 < open1:
            dict = {"pattern": "Bearish2D2D",
                    "patternType": "continuation",
                    "direction": "Bearish",
                    "entry": low2 - 0.01,
                    "sl": high2 + 0.01,
                    "dt": datetime1}

            return dict

        elif high3 < high2 and low3 > low2 and high2 > high1 and low2 > low1:
            dict = {"pattern": "Bearish32D",
                    "patternType": "continuation",
                    "direction": "Bearish",
                    "entry": low2 - 0.01,
                    "sl": high2 + 0.01,
                    "dt": datetime1}

            if bearishGap < 0.5 * atr:
                dict["entry"] = open1 - 0.01

            return dict

        else:
            dict = {"pattern": "",
                    "patternType": "",
                    "direction": "",
                    "entry": 0,
                    "sl": 0,
                    "dt": datetime1}

            return dict

    def isRevStratOutsidePattern(self):
        open1 = self.df['open'].iloc[-1]

        high1 = self.df['high'].iloc[-1]
        high2 = self.df['high'].iloc[-2]
        high3 = self.df['high'].iloc[-3]
        high4 = self.df['high'].iloc[-4]

        low1 = self.df['low'].iloc[-1]
        low2 = self.df['low'].iloc[-2]
        low3 = self.df['low'].iloc[-3]
        low4 = self.df['low'].iloc[-4]

        close1 = self.df['close'].iloc[-1]

        dict = {}

        if low2 > low1 and high2 < high1:
            dict = {"pattern": "Outside3",
                    "direction": "Bullish"}
            return dict

        elif high3 < close1 and low3 > low2 and high3 > high2 and high3 < high1 and low2 < low1 and high2 < close1 and close1 > open1:
            dict = {"pattern": "BullishCompund3",
                    "direction": "Bullish"}
            return dict


        elif high3 < high2 and low3 < low2 and low3 > low1 and low3 > close1 and low2 > close1 and low2 > low1 and close1 < open1:
            dict = {"pattern": "BearishCompund3",
                    "direction": "Bearish"}

            return dict

        else:
            dict = {"pattern": "",
                    "direction": ""}

            return dict

    def getOptionRatios(self, options_df, direction, oi_ratio, volume_ratio, volume_oi_ratio, min_otm_perc, max_otm_perc, days_to_exiration):
        close1 = self.df['close'].iloc[-1]
        eligible_options = pd.DataFrame()

        if direction == "Bullish":
            eligible_options = options_df.loc[(options_df['call_put_oi'] >= oi_ratio) &
                                            (options_df['call_put_volume'] >= volume_ratio) &
                                            (options_df['call_volume_oi'] >= volume_oi_ratio) &
                                            (options_df['strikePrice'] >= close1 + (close1 * min_otm_perc / 100)) &
                                            (options_df['strikePrice'] <= close1 + (close1 * max_otm_perc / 100)) &
                                            (options_df['daysToExpiration'] <= days_to_exiration)]

        if direction == "Bearish":
            eligible_options = options_df.loc[(options_df['call_put_oi'] >= oi_ratio) &
                                            (options_df['call_put_volume'] >= volume_ratio) &
                                            (options_df['call_volume_oi'] >= volume_oi_ratio) &
                                            (options_df['strikePrice'] >= close1 + (close1 * min_otm_perc / 100)) &
                                            (options_df['strikePrice'] <= close1 + (close1 * max_otm_perc / 100)) &
                                            (options_df['daysToExpiration'] <= days_to_exiration)]

        return eligible_options

    def isMinAvgVolume(self, period, min_avg_vol):
        df_vol = self.df[['volume']].tail(period)
        avg_volume = df_vol["volume"].mean()

        if avg_volume > min_avg_vol:
            return avg_volume
        else:
            return 0

    def isAtrAbovePricePercent(self, price_percent):
        atr = self.df['ATRe_14'].iloc[-1]
        close_price = self.df['close'].iloc[-1]

        if atr > close_price * price_percent/100:
            return atr
        else:
            return 0

    def getClosePrice(self, days):
        days_back = -(days + 1)
        close_price = self.df['close'].iloc[days_back]

        return close_price

    def isPriceGreaterThanNumber(self, number):
        close_price = self.df['close'].iloc[-1]

        if close_price > number:
            return close_price
        else:
            return 0

    def isPriceLesserThanNumber(self, number):
        close_price = self.df['close'].iloc[-1]

        if close_price < number:
            return close_price
        else:
            return 0

    def isMinGapUpPercent(self, gap_percent):
        previous_high_price = self.df['high'].iloc[-2]
        current_close_price = self.df['close'].iloc[-1]

        if current_close_price > previous_high_price + (1 + (gap_percent/100)):
            return current_close_price
        else:
            return 0

    def isRSIGreaterThanNumber(self, number):
        rsi = self.df['RSI_14'].iloc[-1]

        if rsi > number:
            return rsi
        else:
            return 0

    def isPriceBelowUBB(self):
        close_price = self.df['close'].iloc[-1]
        ubb = self.df['UBB'].iloc[-1]

        if ubb > close_price:
            return ubb
        else:
            return 0

    def isPriceAboveLBB(self):
        close_price = self.df['close'].iloc[-1]
        lbb = self.df['LBB'].iloc[-1]

        if lbb < close_price:
            return lbb
        else:
            return 0

    def isPriceBelowBbMa(self):
        close_price = self.df['close'].iloc[-1]
        bb_ma = self.df['MBB'].iloc[-1]

        if bb_ma > close_price:
            return bb_ma
        else:
            return 0

    def isBbKcSqueeze(self):
        for i in range(1, len(self.df)):
            self.df.at[i, 'bb_kc_squeeze'] = "No"

            # Squeeze is present if:
            # Upper Bollinger Band is below the Upper Keltner Channel and
            # Lower Bollinger Band is above the Lower Keltner Channel
            if self.df.at[i, 'UBB'] < self.df.at[i, 'UKC'] and self.df.at[i, 'LBB'] > self.df.at[i, 'LKC']:
                self.df.at[i, 'bb_kc_squeeze'] = "Yes"

        bb_kc_squeeze = self.df['bb_kc_squeeze'].iloc[-1]

        if bb_kc_squeeze == "Yes":
            return bb_kc_squeeze
        else:
            return False

    def isBbMaLongSqueeze(self):
        # If either Cond 1 or Cond 2 is met, then there is squeeze, otherwise no squeeze
        for i in range(1, len(self.df)):
            self.df.at[i, 'bb_ma_long_squeeze'] = "No"

            # Cond 1a: Check if the current Bollinger Bands MA is greater than the current 34EMA
            # Cond 1b: Check if the Bollinger Bands MA is lesser than the 34EMA within the last 8 candles and
            if self.df.loc[i, 'MBB'] > self.df.loc[i, 'EMA_34']:
                for n in range(8, 0, -1):
                    if i > n:
                        if self.df.loc[i - n, 'MBB'] < self.df.loc[i - n, 'EMA_34']:
                            self.df.at[i, 'bb_ma_long_squeeze'] = "Y - 34 - " + str(n)

            # We check condition 2 ONLY IF the squeeze is still false, or else we can skip it entirely.
            if self.df.at[i, 'bb_ma_long_squeeze'] == "No":
                # Cond 2a: Check if the current Bollinger Bands MA is greater than the current 50SMA
                # Cond 2b: Check if the Bollinger Bands MA is lesser than the 50SMA within the last 15 candles and
                if self.df.loc[i, 'MBB'] > self.df.loc[i, 'SMA_50']:
                    for n in range(15, 0, -1):
                        if i > n:
                            if self.df.loc[i - n, 'MBB'] < self.df.loc[i - n, 'SMA_50']:
                                self.df.at[i, 'bb_ma_long_squeeze'] = "Y - 50 - " + str(n)

        bb_ma_long_squeeze = self.df['bb_ma_long_squeeze'].iloc[-1]

        if bb_ma_long_squeeze[0] == "Y":
            return bb_ma_long_squeeze
        else:
            return False

    def isBbMaShortSqueeze(self):
        # If either Cond 1 or Cond 2 is met, then there is squeeze, otherwise no squeeze
        for i in range(1, len(self.df)):
            self.df.at[i, 'bb_ma_short_squeeze'] = "No"

            # Cond 1a: Check if the current Bollinger Bands MA is lesser than the current 34EMA
            # Cond 1b: Check if the Bollinger Bands MA is greater than the 34EMA within the last 8 candles and
            if self.df.loc[i, 'MBB'] < self.df.loc[i, 'EMA_34']:
                for n in range(8, 0, -1):
                    if i > n:
                        if self.df.loc[i - n, 'MBB'] > self.df.loc[i - n, 'EMA_34']:
                            self.df.at[i, 'bb_ma_short_squeeze'] = "Y - 34 - " + str(n)

            # We check condition 2 ONLY IF the squeeze is still false, or else we can skip it entirely.
            if self.df.at[i, 'bb_ma_short_squeeze'] == "No":
                # Cond 2a: Check if the current Bollinger Bands MA is lesser than the current 50SMA
                # Cond 2b: Check if the Bollinger Bands MA is greater than the 50SMA within the last 15 candles and
                if self.df.loc[i, 'MBB'] < self.df.loc[i, 'SMA_50']:
                    for n in range(15, 0, -1):
                        if i > n:
                            if self.df.loc[i - n, 'MBB'] > self.df.loc[i - n, 'SMA_50']:
                                self.df.at[i, 'bb_ma_short_squeeze'] = "Y - 50 - " + str(n)

        bb_ma_short_squeeze = self.df['bb_ma_short_squeeze'].iloc[-1]

        if bb_ma_short_squeeze[0] == "Y":
            return bb_ma_short_squeeze
        else:
            return False

    def maCross(self, lower_ma, higher_ma, ma_type, direction):
        LowerMA = min(lower_ma, higher_ma)
        HigherMA = max(lower_ma, higher_ma)

        if ma_type == "sma":
            self.df['LowerEMA'] = self.df.ta.sma(close=self.df["close"], length=LowerMA)
            self.df['HigherEMA'] = self.df.ta.sma(close=self.df["close"], length=HigherMA)

        elif ma_type == "ema":
            self.df['LowerEMA'] = self.df.ta.ema(close=self.df["close"], length=LowerMA, adjust=False)
            self.df['HigherEMA'] = self.df.ta.ema(close=self.df["close"], length=HigherMA, adjust=False)

        if direction == "Bullish":
            for i in range(len(self.df)-1, 0, -1):
                if self.df.loc[i, 'LowerEMA'] > self.df.loc[i, 'HigherEMA'] and \
                        self.df.loc[i-1, 'LowerEMA'] < self.df.loc[i-1, 'HigherEMA']:
                    return self.df['HigherEMA'][i]

        elif direction == "Bearish":
            for i in range(len(self.df)-1, 0, -1):
                if self.df.loc[i, 'LowerEMA'] < self.df.loc[i, 'HigherEMA'] and \
                        self.df.loc[i-1, 'LowerEMA'] > self.df.loc[i-1, 'HigherEMA']:
                    return self.df['HigherEMA'][i]

    # def MACDCross(self, fast_ma, slow_ma, signal_ma, direction):
    #     macd_df = self.df.ta.macd(close=self.df["close"], fast=fast_ma, slow=slow_ma, signal=signal_ma)
    #     macd_df = macd_df.rename(columns={f"MACD_{fast_ma}_{slow_ma}_{signal_ma}": "MACD",
    #                                       f"MACDh_{fast_ma}_{slow_ma}_{signal_ma}": "History",
    #                                       f"MACDs_{fast_ma}_{slow_ma}_{signal_ma}": "Signal"})
    #
    #     self.df['MACD'] = macd_df["MACD"]
    #     self.df['Signal'] = macd_df["Signal"]
    #
    #     if direction == "Bullish":
    #         for i in range(len(self.df) - 1, 0, -1):
    #             if self.df.loc[i, 'MACD'] > self.df.loc[i, 'Signal'] and \
    #                     self.df.loc[i - 1, 'MACD'] < self.df.loc[i - 1, 'Signal']:
    #                 return self.df['low'][i - 1]
    #
    #     elif direction == "Bearish":
    #         for i in range(len(df) - 1, 0, -1):
    #             if self.df.loc[i, 'MACD'] < self.df.loc[i, 'Signal'] and \
    #                     self.df.loc[i - 1, 'MACD'] > self.df.loc[i - 1, 'Signal']:
    #                 return self.df['low'][i - 1]

    def getHighestHigh(self):
        col_high = self.df["high"]
        max_value = col_high.max()

        return max_value

