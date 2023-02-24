import pandas as pd
import math
import pandas_ta as ta

def channel_breakout_strategy(df,length,tick):
    upBound = df['High'].rolling(length).max()
    downBound = df['Low'].rolling(length).min()
    df['ChBrkLE'] = pd.Series(index=df.index)
    df['ChBrkSE'] = pd.Series(index=df.index)
    for i in range(length, len(df)):
        if not pd.isna(df['Close'][i - length]):
            df.at[df.index[i], 'ChBrkLE'] = upBound[i] + tick  # add mintick value
        df.at[df.index[i], 'ChBrkSE'] = downBound[i] - tick  # subtract mintick value
    df.loc[df.ChBrkLE.shift(1) < df.Close, 'BUY'] = True
    df.loc[df.ChBrkSE.shift(1) > df.Close, 'SELL'] = True
    return df

def get_strikes(ltp, symbol):
    adict = {'BANKNIFTY':100,"NIFTY":50,'USDINR':0.25,'CRUDEOIL':50}
    step = adict.get(symbol)
    atm = math.ceil(ltp / step) * step
    return [atm - 3*step, atm - 2*step, atm, atm + 1*step, atm , atm+step]

def check_cond(df):
    if isinstance(df, pd.DataFrame):
        df.Datetime = pd.to_datetime(df.Datetime)
        if min == df.Datetime.iloc[-1].minute:
            df = df.head(-1)
        df = df.set_index(df.Datetime)
        df['200EMA'] = ta.ema(df.Close, 200)
        df['VWAP'] = ta.vwap(df.High, df.Low, df.Close, df.Volume)
        # df.loc[:, 'COND'] = False
        df.loc[((df['200EMA'] > df['VWAP']) &
                (df.Close.shift(8) > df['200EMA']) &
                (df.Close.shift(7) > df['200EMA']) &
                (df.Close.shift(6) > df['200EMA']) &
                (df.Close.shift(5) > df['200EMA']) &
                (df.Close.shift(4) > df['200EMA']) &
                (df.Close.shift(3) > df['200EMA']) &
                (df.Close.shift(2) > df['200EMA']) &
                (df.Close.shift(1) > df['200EMA']) &
                (df.Close > df.VWAP)),
               'COND'] = True
        df.loc[df['200EMA'] < df['VWAP'],"COND"] = False
        return df

