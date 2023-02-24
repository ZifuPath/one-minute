import datetime

from fivepaisa import *
from data_controller import *
from message import *
from model import *
from angel_login import *
import warnings
import time
warnings.filterwarnings('ignore')



def order_check(client,condition,scr,stop_loss,target):
    while condition:
        df = get_candl(client,scr,"N","D",0)
        strike_ltp = df.Close.iloc[-1]
        if strike_ltp>target:
            telegram_bot_sendtext(f'TARGET REACHED', BOT_ID2, BOT_TOKEN1)
            condition=False
        elif strike_ltp<stop_loss:
            telegram_bot_sendtext(f'STOPLOSS HIT', BOT_ID2, BOT_TOKEN1)
            condition=False
        time.sleep(0.3)



def main_code(client,options,symbol,exchange,exchtype,scripcode,tick,obj,token,expiry1):
    global count
    ltp = get_future_ltp(client,exchange,exchtype,scripcode)
    strikes = get_strikes(ltp,symbol)
    df_opt = options[options.StrikePrice.isin(strikes)].to_dict('record')
    for row in df_opt:
        try:
            df = get_candl(client, row['Scripcode'],row['Exch'], row['ExchType'],7)
            df = check_cond(df)
            df = channel_breakout_strategy(df,200,tick)
            df.loc[(df.VWAP > df.Close), 'COND'] = False
            df['COND'] = df['COND'].ffill()
            #df.to_csv(f'{row["Name"]}.csv',index=False)
            #print(f'{df.Close.iloc[-1]} {row["Name"]} {df["Close"].iloc[-1]} BUY {df["BUY"].iloc[-1]} COND {df["COND"].iloc[-1]}')
            if df["BUY"].iloc[-1] == True and df['COND'].iloc[-1] == True:
                telegram_bot_sendtext(f'CONDITION REACHED', BOT_ID2, BOT_TOKEN1)
                count +=1
                buy_value = df.Close.iloc[-1]
                stop_loss = buy_value - 30 if symbol.__contains__('BANK') else buy_value - 15
                target = buy_value + 30 if symbol.__contains__('BANK') else buy_value + 15
                strike = (math.ceil(ltp / 100) * 100) - 200 if row['Name'].__contains__('CE') else (math.ceil(ltp / 100) * 100) + 100
                condition = 'BUY' if row['Name'].__contains__('CE') else 'SELL'
                buy1 = order_exe(strike, condition, expiry1,symbol)
                tk = token[token.symbol == buy1]
                tk = tk['token'].iloc[0]
                order_entry(buy1, obj, tk)
                cond = True
                telegram_bot_sendtext(f'{row["Name"]} BOUGHT AT {buy_value} TARGET {target} SL {stop_loss}', BOT_ID2, BOT_TOKEN1)
                order_check(client, cond, row['Scripcode'], stop_loss, target)
                order_exit(buy1, obj, tk)
        except BaseException as e:
            print(row['Name'])


def app(symbol,exchange,exchtype):
    exch, extype, scripcode, tick, name = get_future_script(symbol, exchange, exchtype)
    expiry = get_expiry_date(symbol, exchange, exchtype)
    options = get_token(expiry, symbol, exchange, exchtype)
    return options,scripcode


def run(stock,e,asset):
    global count
    client = get_client()
    options,scripcode = app(stock,e,asset )
    obj= order()
    token,expiry1= get_expiry_tokens(stock)
    while datetime.time(9, 11) < datetime.datetime.now().time() < datetime.time(15, 28):
        if datetime.datetime.now().second == 1:
            telegram_bot_sendtext(datetime.datetime.now().minute)
            if count>= 2:
                pass
            main_code(client,options,stock,e,asset,scripcode,2,obj,token,expiry1)

if __name__ == '__main__':
    count = 0
    today = datetime.datetime.now().weekday()
    stock,e,asset= 'BANKNIFTY','N','D'
    if today not in [6, 7]:
        run(stock,e,asset)

