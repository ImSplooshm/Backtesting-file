from tqdm import tqdm
import pandas as pd
import math
import matplotlib.pyplot as plt
import signals
from data import *

def backtest(method, path, balance = 1000, risk = 0.1):
    initial_balance = balance

    balance_arr = []
    
    trades, profitable_trades = [0] * 2

    tickers = read_pickle('tickers.pickle')

    for ticker in tqdm(tickers):
        current_trade = None

        main_df = pd.read_csv(f'{path}{ticker}.csv')
        for i in tqdm(range(50, len(main_df))):
            balance_arr.append(balance)
            df = main_df[:i]

            signal, tp, sl = method(df)

            risk_amount = balance * risk

            if current_trade == None and signal == 'BUY':
                volume = risk_amount / df['close'].iloc[-1]
                trades += 1
                current_trade = {
                    'type': 'LONG',
                    'entry_price': df['close'].iloc[-1],
                    'stop_loss': sl,
                    'take_profit': tp,
                    'position_size': volume,
                    'entry_index': i,
                }
            elif current_trade == None and signal == 'SELL':
                volume = risk_amount / df['close'].iloc[-1]
                trades += 1
                current_trade = {
                    'type': 'SHORT',
                    'entry_price': df['close'].iloc[-1],
                    'stop_loss': sl,
                    'take_profit': tp,
                    'position_size': volume,
                    'entry_index': i,
                }
            elif current_trade != None:
                if df['low'].iloc[-1] <= current_trade['stop_loss'] and current_trade['type'] == 'LONG':
                    loss = current_trade['position_size'] * ((current_trade['entry_price'] - current_trade['stop_loss']))
                    balance -= loss

                    current_trade = None 
                elif df['high'].iloc[-1] >= current_trade['take_profit'] and current_trade['type'] == 'LONG':
                    profit = current_trade['position_size'] * ((current_trade['take_profit'] - current_trade['entry_price']))
                    balance += profit

                    current_trade = None
                    profitable_trades += 1
                elif df['high'].iloc[-1] >= current_trade['stop_loss'] and current_trade['type'] == 'SHORT':
                    loss = current_trade['position_size'] * ((current_trade['entry_price'] - current_trade['stop_loss']))
                    balance -= loss

                    current_trade = None
                elif df['low'].iloc[-1] <= current_trade['take_profit'] and current_trade['type'] == 'SHORT':
                    profit = current_trade['position_size'] * ((current_trade['take_profit'] - current_trade['entry_price']))
                    balance += profit

                    profitable_trades += 1
                    current_trade = None

    overall_return = (balance - initial_balance) / initial_balance * 100
    profitable_percentage = profitable_trades / trades * 100
    avg_return = math.log(overall_return, trades) if overall_return > 0 else None

    plt.plot(balance_arr)
    
    results = {
        'initial balance': initial_balance,
        'resulting balance': balance,
        'trades': trades,
        'return': overall_return,
        'average return': avg_return,
        'success rate': profitable_percentage
    }

    return results, plt

results, plt = backtest(method = signals.m_10, path = 'inplace_data/')
print(results)
plt.show()