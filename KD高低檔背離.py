# -*- coding: utf-8 -*-
"""
Created on Mon May 20 15:52:16 2019

@author: Susan
"""
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def profit_show(profit):
    profit = np.array(profit)
    print('總損益點數: %d' % np.sum(profit))
    print('勝率: %f' % (np.sum(profit > 0) / len(profit)))
    print('賺錢平均點數: %f' % (np.mean(profit[profit > 0])))
    print('輸錢平均點數: %f' % (np.mean(profit[profit <= 0])))
    plt.title('Daily Accumulated Points')
    plt.plot(np.cumsum(profit))
    plt.show()
    plt.title('Histogram of daily profits and losses')
    plt.hist(profit, bins=100)
    plt.show()
    

# Data process
taiex_df = pd.read_csv('TXF20112015_original.csv')
del taiex_df['dCode']
trade_day = np.unique(taiex_df['dDateTime']//10000)

#%%
'''RSV-M-mins'''
M = 30
alpha = 1/3
taiex_df['RSV'] = 100* (( taiex_df['dClose'] - taiex_df['dLowest'].rolling(window=M).min() ) / (taiex_df['dHighest'].rolling(window=M).max() - taiex_df['dLowest'].rolling(window=M).min()))

#%%
plt.plot(taiex_df['dClose'][:300], label='Price', color = 'k')
plt.legend()
plt.show()

plt.plot(taiex_df['RSV'][:300], label='RSV', color = 'r')
plt.axhline(20)
plt.axhline(80)
plt.ylim((0,100))
plt.legend()
plt.show()
#%%
print('=====策略1 RSV=====')
start = time.time()
profit_arr1 = []
for date in trade_day:
    dayData = taiex_df[taiex_df['dDateTime']//10000 == date].reset_index(drop=True)
    profit = 0
    isBought = False
    for i in range(len(dayData)):
        if dayData['RSV'].iloc[i] <= 20 and not isBought:
            isBought = True
            buy_price = dayData['dClose'].iloc[i]
        elif dayData['RSV'].iloc[i] >= 80 and isBought:
            isBought = False
            sell_price = dayData['dClose'].iloc[i]
            profit += sell_price - buy_price
    if isBought:
        sell_price = dayData['dClose'].iloc[-1]
        profit += sell_price - buy_price
    profit_arr1.append(profit)
profit_show(profit_arr1)
end = time.time()
print('Time : %d' % (end-start))

#%%
'''RSV，K_line,D_line'''
taiex_df['K_line'] = 0
taiex_df['D_line'] = 0
k = np.zeros(len(taiex_df))
d = np.zeros(len(taiex_df))
k[:M-2] = np.nan
d[:M-2] = np.nan
rsv = taiex_df['RSV'].values
k[M-2] = 50
d[M-2] = 50
for i in range(M-1, len(taiex_df)):
    k[i] = alpha * rsv[i] + (1 - alpha) * k[i-1]
    d[i] = alpha * k[i] + (1 - alpha) * d[i-1]
taiex_df['K_line'] = k
taiex_df['D_line'] = d

#%%

plt.plot(taiex_df['K_line'][M:M+60], label='K')
plt.plot(taiex_df['D_line'][M:M+60], label='D')
plt.axhline(20)
plt.axhline(80)
plt.ylim((0,100))
plt.legend()
plt.show()

#%%
def cross(df):
    # 判斷是否在>=80 或 <=20之間
    df['above_80'] = (df['K_line'].values>=80) & (df['D_line'].values>=80)
    df['below_20'] = (df['K_line'].values<=20) & (df['D_line'].values<=20)
    
    # 找交叉
    diff = df['K_line'] - df['D_line'] # 計算「K線」減去「D線」之差
    asign = np.sign(diff) # asign 會在這個數大於 0 時回傳 +1，小於 0 時回傳-1
    asign[np.where(asign==0)[0]] = 1 # 換句話說，asign 裡的 +1 就是當短線高於長線時，而 -1 就是長線高於短線時
    
    # 而黃金交叉（短線從長線下面穿越到長線）就是在 -1 到 +1 之時
    cross_signal = (np.where(np.roll(asign, 1)<asign))[0] 
    df['golden_cross'] = 0
    df['golden_cross'][cross_signal] = 1 # 把結果存到 golden_cross 裡面
    
    # 而死亡交叉（短線從長線上面跌落到長線）就是在 +1 到 -1 之時
    death_signal = (np.where(np.roll(asign, 1)>asign))[0]  
    df['death_cross'] = 0
    df['death_cross'][death_signal] = 1 # 把結果存到 death_cross 裡面
    
    df['Golden_80'] = (df['above_80']) & (df['golden_cross'])
    df['Death_80'] = (df['above_80']) & (df['death_cross'])
    df['Golden_20'] = (df['below_20']) & (df['golden_cross'])
    df['Death_20'] = (df['below_20']) & (df['death_cross'])
    
    print("Golden Cross 黃金交叉總共有:",df['golden_cross'].sum(),"次")
    print("Death Cross 死亡交叉總共有:",df['death_cross'].sum(),"次")
    df = df.drop(columns = ['golden_cross', 'death_cross'])
    return df

taiex_df = cross(taiex_df)

#%%
plt.plot(taiex_df['K_line'][M:M+60], label='K')
plt.plot(taiex_df['D_line'][M:M+60], label='D')
golden = np.where(taiex_df['Golden_20'][:M+60])[0]
death = np.where(taiex_df['Death_80'][:M+60])[0]
for i in golden:
    plt.axvline(i, color='red')
for j in death:
    plt.axvline(j, color='g')
plt.axhline(20)
plt.axhline(80)
plt.legend()
plt.show()

#%%

print('=====策略2.1 KD，20G作多，80D平倉 =====')
profit_arr21 = []
for date in trade_day:
    dayData = taiex_df[taiex_df['dDateTime']//10000 == date].reset_index(drop=True)
    profit = 0
    isBought = False
    
    if np.all(dayData['Golden_20'] == 0) and np.all(dayData['Death_80'] == 0):
        #plt.show()
        profit_arr21.append(0)
        continue
    for i in range(len(dayData)):
        minute_data = dayData.iloc[i]
        if minute_data['Golden_20'] and not isBought:
            isBought = True
            buy_price = minute_data['dClose']
        elif minute_data['Death_80'] and isBought:
            isBought = False
            sell_price = minute_data['dClose']
            profit += sell_price - buy_price
            
    if isBought:
        sell_price = dayData['dClose'].iloc[-1]
        profit += sell_price - buy_price
    profit_arr21.append(profit)
profit_show(profit_arr21)

#%%
def L_depart(df):
    df['Price_Uptrend'] = np.clip(np.sign(np.ediff1d(df['dClose'], to_begin=0)), 0, 1)
    df['KD_Uptrend'] = np.clip(np.sign(np.ediff1d(df['K_line'], to_begin=0)), 0, 1) * \
                       np.clip(np.sign(np.ediff1d(df['D_line'], to_begin=0)), 0, 1)
    df['L_depart'] = (1 - df['Price_Uptrend']) & (df['KD_Uptrend']) & (df['below_20'])
    return df

taiex_df = L_depart(taiex_df)

#%%
def H_depart(df):
    df['Price_Uptrend'] = np.clip(np.sign(np.ediff1d(df['dClose'], to_begin=0)), 0, 1)
    df['KD_Downtrend'] = (1 - np.clip(np.sign(np.ediff1d(df['K_line'], to_begin=0)), 0, 1)) * \
                       (1 - np.clip(np.sign(np.ediff1d(df['D_line'], to_begin=0)), 0, 1))
    df['H_depart'] = (df['Price_Uptrend']) & (df['KD_Downtrend']) & (df['above_80'])
    return df

taiex_df = H_depart(taiex_df)
#%%

print('=====策略3=====')
#（G20 ＋無背離＋沒買） →作多！
#（D80 ＋無背離＋有買）→平倉！
profit_arr3 = []
for date in trade_day:
    dayData = taiex_df[taiex_df['dDateTime']//10000 == date].reset_index(drop=True)
    profit = 0
    isBought = False
    
    for i in range(len(dayData)) :
        if dayData['Golden_20'].iloc[i] and not dayData['L_depart'].iloc[i] and not isBought:
            isBought = True
            buy_price = dayData['dClose'].iloc[i]
        elif dayData['Death_80'].iloc[i] and not dayData['H_depart'].iloc[i] and isBought :
            isBought = False
            sell_price = dayData['dClose'].iloc[i]
            profit += sell_price - buy_price
    if isBought :
        sell_price = dayData['dClose'].iloc[-1]
        profit += sell_price - buy_price
    profit_arr3.append(profit)
profit_show(profit_arr3)

#%%
print('====HW-策略4=====')
#（D80 ＋無背離＋沒買） →作空！
#（G20 ＋無背離＋有買）→平倉！
profit_arr4 = []
for date in trade_day:
    dayData = taiex_df[taiex_df['dDateTime']//10000 == date].reset_index(drop=True)
    profit = 0
    isBought = False
    
    for i in range(len(dayData)) :
        if dayData['Death_80'].iloc[i] and not dayData['H_depart'].iloc[i] and not isBought:
            isBought = True
            buy_price = dayData['dClose'].iloc[i]
        elif dayData['Golden_20'].iloc[i] and not dayData['L_depart'].iloc[i] and isBought :
            isBought = False
            sell_price = dayData['dClose'].iloc[i]
            profit += buy_price - sell_price
    if isBought :
        sell_price = dayData['dClose'].iloc[-1]
        profit += buy_price - sell_price
    profit_arr4.append(profit)
profit_show(profit_arr4)