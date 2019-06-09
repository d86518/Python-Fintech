import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 資料前處理
taiex_df = pd.read_csv('TXF20112015_original.csv')
del taiex_df['dCode']
trade_day = np.unique(taiex_df['dDateTime']//10000)

# 評估策略的優劣程度
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

# 畫出價格區間
def plot_PriceRange(df):    
    time = pd.to_datetime(df['dDateTime'], format='%Y%m%d%H%M').values
    plt.plot(time, dayData['LowerBound'], 'g-', label='LowerBound')
    plt.plot(time, dayData['UpperBound'], 'r-', label='UpperBound')    
    plt.plot(time, df['dClose'], label='ClosePrice')
    plt.fill_between(time, df['LowerBound'], df['UpperBound'], color = 'pink')
    plt.title('Price Range')
    plt.xlabel('Datetime')
    plt.ylabel('Open Price')
    plt.legend()
    plt.show()
    
# 計算並畫出20110105的價格區間。
dayData = taiex_df[taiex_df['dDateTime']//10000 == 20110105].reset_index(drop=True)
box_ratio = 0.01
dayData['LowerBound'] = dayData['dOpen'][0] * (1 - box_ratio)
dayData['UpperBound'] = dayData['dOpen'][0] * (1 + box_ratio)
plot_PriceRange(dayData)

# 定義區間、停損停利點
# 價格突破區間順勢策略-價格突破上界
box_ratio = 0.01
stop_loss_ratio = 0.005
stop_profit_ratio = 0.03
TotalProfit = []
for date in trade_day:
    dayData = taiex_df[taiex_df['dDateTime']//10000 == date].reset_index(drop=True)   
    below_LowerBound = np.where(dayData['dLowest'] <= (dayData['dOpen'][0] * (1 - box_ratio)))[0] # 當價格突破下界   
    above_UpperBound = np.where(dayData['dHighest'] >= (dayData['dOpen'][0] * (1 + box_ratio)))[0] # 當價格突破上界   
    # 當天未進行交易，不進行接下來的判斷
    if len(below_LowerBound) == 0 and len(above_UpperBound) == 0:
        continue       
    # 當價格突破上界進場
    elif len(below_LowerBound) == 0 or (len(above_UpperBound) != 0 and above_UpperBound[0] < below_LowerBound[0]):
        buy_price = dayData['dClose'][above_UpperBound[0]]
        # 制定停損停利點
        stop_loss_price = buy_price * (1 - stop_loss_ratio)
        stop_loss_points = np.where(dayData['dLowest'] <= stop_loss_price)[0] 
        stop_profit_price = buy_price * (1 + stop_profit_ratio)
        stop_profit_points = np.where(dayData['dHighest'] >= stop_profit_price)[0]        
        after_stop_loss = stop_loss_points[stop_loss_points > above_UpperBound[0]]
        after_stop_profit = stop_profit_points[stop_profit_points > above_UpperBound[0]]
        if len(after_stop_profit) == 0 and len(after_stop_loss) == 0: # 到收盤時強制出場
            sell_price = dayData['dClose'].iloc[-1]        
        elif len(after_stop_profit) == 0 or (len(after_stop_loss) != 0 and after_stop_loss[0] < after_stop_profit[0]): # 停損判斷
            sell_price = dayData['dClose'][after_stop_loss[0]]
        elif len(after_stop_loss) == 0 or (len(after_stop_profit) != 0 and after_stop_profit[0] < after_stop_loss[0]): # 停利判斷
            sell_price = dayData['dClose'][after_stop_profit[0]]
        TotalProfit += [sell_price - buy_price]       
profit_show(TotalProfit)


# 畫出布林通道
def plot_BBands(df):    
    time = pd.to_datetime(df['dDateTime'], format='%Y%m%d%H%M').values
    plt.plot(time, df['LowerBound'], 'g-', label='LowerBound')
    plt.plot(time, df['UpperBound'], 'r-', label='UpperBound') 
    plt.plot(time, df['MA_20'], 'b--', label='MA_20') 
    plt.plot(time, df['dClose'], label='ClosePrice')
    plt.fill_between(time, df['LowerBound'], df['UpperBound'], color = 'pink')
    plt.title('Price Range')
    plt.xlabel('Datetime')
    plt.ylabel('Open Price')
    plt.legend()
    plt.show()

# 計算布林通道的組成元素(上線、中線、下線)。
taiex_df['MA_20'] = taiex_df['dClose'].rolling(20).mean() # 中界 
taiex_df['UpperBound'] = taiex_df['MA_20'] + 1.5*taiex_df['dClose'].rolling(20).std() # 上界
taiex_df['LowerBound'] = taiex_df['MA_20'] - 1.5*taiex_df['dClose'].rolling(20).std() # 下界
#taiex_df['MA_10'] = taiex_df['dClose'].rolling(10).mean() # 中界 
#taiex_df['UpperBound'] = taiex_df['MA_20'] + 2*taiex_df['dClose'].rolling(10).std() # 上界
#taiex_df['LowerBound'] = taiex_df['MA_20'] - 2*taiex_df['dClose'].rolling(30).std() # 下界
#taiex_df['MA_30'] = taiex_df['dClose'].rolling(30).mean() # 中界 
#taiex_df['UpperBound'] = taiex_df['MA_20'] + 2*taiex_df['dClose'].rolling(10).std() # 上界
#taiex_df['LowerBound'] = taiex_df['MA_20'] - 2*taiex_df['dClose'].rolling(30).std() # 下界

# 畫出20110105的布林通道。
dayData = taiex_df[taiex_df['dDateTime']//10000 == 20110105].reset_index(drop=True)
plot_BBands(dayData)


def goldencross(df):    
    diff_UpperBound = np.sign(df['dHighest'] - df['UpperBound'])    
    diff_LowerBound = np.sign(df['dHighest'] - df['LowerBound'])      
    signal = (np.where(np.roll(diff_UpperBound, 1)<diff_UpperBound))[0] # 價格與上線黃金交叉（價格由下往上穿越上線）      
    df['UB_goldencross'] = 0
    df['UB_goldencross'][signal] = 1
    signal = (np.where(np.roll(diff_LowerBound, 1)<diff_LowerBound))[0] # 價格與下線黃金交叉（價格由下往上穿越下線）
    df['LB_goldencross'] = 0
    df['LB_goldencross'][signal] = 1
    return df 
"""
TotalProfit = []
for date in trade_day:
    dayData = taiex_df[taiex_df['dDateTime']//10000 == date].reset_index(drop=True)    
    dayData = goldencross(dayData)    
    isBought = False  
    if sum(dayData['LB_goldencross']) == 0: # 當天未進行交易，不進行接下來的判斷
        continue    
    for i in range(1, len(dayData)):        
        if not isBought and dayData['LB_goldencross'][i]: # 價格與下線黃金交叉進場
            isBought = True
            buy_price = dayData['dClose'][i]      
        elif isBought and dayData['UB_goldencross'][i]: # 價格與上線黃金交叉出場
            isBought = False
            sell_price = dayData['dClose'][i]
            TotalProfit += [sell_price - buy_price]
            break
    if isBought: #到收盤時強制出場
        sell_price = dayData['dClose'].iloc[-1]
        TotalProfit += [sell_price - buy_price]
profit_show(TotalProfit)
"""
def deathcross(df):    
    diff_UpperBound = np.sign(df['dLowest'] - df['UpperBound'])    
    diff_LowerBound = np.sign(df['dLowest'] - df['LowerBound'])      
    signal = (np.where(np.roll(diff_UpperBound, 1)>diff_UpperBound))[0] # 價格與上線死亡交叉時進場（價格由上往下穿越上線） 
    df['UB_deathcross'] = 0
    df['UB_deathcross'][signal] = 1
    signal = (np.where(np.roll(diff_LowerBound, 1)>diff_LowerBound))[0] # 價格與下線死亡交叉時出場，收盤時強制出場 （價格由上往下穿越下線）
    df['LB_deathcross'] = 0
    df['LB_deathcross'][signal] = 1
    return df 
"""
TotalProfit = []
for date in trade_day:
    dayData = taiex_df[taiex_df['dDateTime']//10000 == date].reset_index(drop=True)    
    dayData = deathcross(dayData)    
    isBought = False  
    if sum(dayData['UB_deathcross']) == 0: # 當天未進行交易，不進行接下來的判斷
        continue    
    for i in range(1, len(dayData)):        
        if not isBought and dayData['UB_deathcross'][i]: # 價格與下線死亡交叉進場
            isBought = True
            buy_price = dayData['dClose'][i]      
        elif isBought and dayData['LB_deathcross'][i]: # 價格與上線死亡交叉出場
            isBought = False
            sell_price = dayData['dClose'][i]
            TotalProfit += [buy_price - sell_price]
            break
    if isBought: #到收盤時強制出場
        sell_price = dayData['dClose'].iloc[-1]
        TotalProfit += [buy_price - sell_price]
profit_show(TotalProfit)
"""

"""
1. 延伸布林通道逆勢策略 (策略1+策略2)
2. 一天多次交易
3. 分別選不同MA線(10分MA線、20分MA線、30分MA線)與不同標準差(1.5倍標準差、2倍標準差)，找出最佳配置。

The best：20分MA線、 1.5倍標準差
"""


TotalProfit = []
for date in trade_day:
    dayData = taiex_df[taiex_df['dDateTime']//10000 == date].reset_index(drop=True)    
    dayData = deathcross(dayData)
    dayData = goldencross(dayData)     
    x=0
    if sum(dayData['UB_deathcross']) == 0 and sum(dayData['LB_goldencross']) == 0: # 當天未進行交易，不進行接下來的判斷
        continue    
    for i in range(1, len(dayData)):        
        if x==0 and dayData['UB_deathcross'][i]: 
            buy_price = dayData['dClose'][i]
            x=-1
        elif x==-1 and dayData['LB_deathcross'][i]:
            sell_price = dayData['dClose'][i]
            TotalProfit += [buy_price - sell_price]
            x=0
        if x==0 and dayData['LB_goldencross'][i]:
            buy_price = dayData['dClose'][i]
            x=1
        elif x==1 and dayData['UB_goldencross'][i]:
            sell_price = dayData['dClose'][i]
            TotalProfit += [sell_price - buy_price]
            x=0
    if x==-1: # 到收盤時強制出場
        sell_price = dayData['dClose'].iloc[-1]
        TotalProfit += [buy_price - sell_price]
    if x==1: # 到收盤時強制出場
        sell_price = dayData['dClose'].iloc[-1]
        TotalProfit += [sell_price - buy_price]
    print(date)
profit_show(TotalProfit)