import pandas as pd
import datetime
import os

def get_expiry_date(symbol,exchange,extype):
    df = pd.read_csv('scripmaster-csv-format.csv')
    df = df[(df.Root==symbol) &(df.Exch==exchange) & (df.ExchType==extype) & ~(df.CpType=='XX')]
    df.Expiry = pd.to_datetime(df.Expiry)
    df = df[df.Expiry > datetime.datetime.now()]
    df = df.sort_values('Expiry')
    expiry = df.Expiry.iloc[0].strftime('%Y-%m-%d')
    return expiry

def get_future_script(symbol,exchange,extype):
    df = pd.read_csv('scripmaster-csv-format.csv')
    df = df[(df.Root==symbol) &(df.Exch==exchange) & (df.ExchType==extype) & (df.CpType=='XX')]
    df.Expiry = pd.to_datetime(df.Expiry)
    df = df[df.Expiry > datetime.datetime.now()]
    df = df.sort_values('Expiry')
    df = df.head(1).reset_index()
    return df.Exch.iloc[0],df.ExchType.iloc[0],df.Scripcode.iloc[0],df.TickSize.iloc[0],df.Name.iloc[0]

def get_candl(client, scr, exchange,exchtype,day):
    t1 = datetime.datetime.today().strftime('%Y-%m-%d')
    t2 = (datetime.datetime.today() - datetime.timedelta(days=day)).strftime('%Y-%m-%d')
    try:
        df1 = client.historical_data(exchange,exchtype, scr, '1m', t2, t1)

        return df1
    except:
        return None

def get_future_ltp(client,exchange,extype,scripcode):
    df = get_candl(client,scripcode,exchange,extype,2)
    if isinstance(df,pd.DataFrame):
        return df.Close.iloc[-1]
    else:
        return None

def get_token(exp1,symbol,exchange,exchtype):
    if not os.path.exists(f'{symbol}_options_{exp1}.csv'):
        df = pd.read_csv(r'scripmaster-csv-format.csv')
        df = df[(df.Root==symbol) & (df.Exch == exchange) & (df.ExchType == exchtype) & df.Expiry.str.contains(exp1) & ~(df.CpType=='XX')]
        feature = ['Exch', 'ExchType', 'Scripcode', 'Name', 'Expiry']
        df1 = df[feature]
        df1['StrikePrice'] = df1.Name.str.split(' ', expand=True)[5]
        # df1['StrikePrice'] = df1['StrikePrice'].astype('int')
        df1 = df1.dropna()
        df1.to_csv(f'{symbol}_options_{exp1}.csv', index=False)
        df1 = pd.read_csv(f'{symbol}_options_{exp1}.csv')
        return df1
    else:
        return pd.read_csv(f'{symbol}_options_{exp1}.csv')



if __name__ == '__main__':
    exchange,exchtype,scripcode,tick,name = get_future_script('USDINR','N','U')
    from fivepaisa import *
    client = get_client()
    df1 = get_candl(client,scripcode,exchange,exchtype,2)
    print(df1.head())