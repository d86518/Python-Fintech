import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
taiex_df = pd.read_csv('TXF20112015.csv')
trade_day = np.unique(taiex_df['dDateTime']//10000)

# 找出停損停利點
def stopprofitandloss():
    for date in trade_day:
        dayData = taiex_df[taiex_df['dDateTime']//10000 == date]
        buy_price = dayData['dOpen'].iloc[0] # 記錄開盤價
        # 停損點
        stop_loss = np.where(dayData['dLowest'] <= buy_price - 30)[0]
        # 停利點 
        stop_profit = np.where(dayData['dHighest'] >= buy_price + 30)[0]
        
        """
       1 整天都沒有觸及停損停利點 	-> 以最終收盤價賣出
       2 有停損點出現但沒有停利 		-> 以停損點時收盤價賣出
       3 有停利點出現但沒有停損 		-> 以停利點時收盤價賣出
       4 停損點出現比停利點早 		-> 以停損點時收盤價賣出
       5 停利點比停損點早 		 -> 以停利點時收盤價賣出
        """
        
        if len(stop_loss) == 0 and len(stop_profit) == 0: 
            sell_price = dayData['dClose'].iloc[-1]
        elif len(stop_profit) == 0:
            sell_price = dayData['dClose'].iloc[stop_loss[0]] #stop_loss[0]開始要停損
        elif len(stop_loss) == 0:   
            sell_price = dayData['dClose'].iloc[stop_profit[0]]
            
        elif stop_loss[0] < stop_profit[0]:
            sell_price = dayData['dClose'].iloc[stop_loss[0]]
        else:
            sell_price = dayData['dClose'].iloc[stop_profit[0]]
            
        profit.append(sell_price - buy_price)
        
    return profit

#動量策略  
def momentum():
    profit = []
    for date in trade_day:
        dayData = taiex_df[taiex_df['dDateTime']//10000 == date]
        
        below_open = np.where(dayData['dLowest'] <= dayData['dOpen'].iloc[0] - 30)[0]
        above_open = np.where(dayData['dHighest'] >= dayData['dOpen'].iloc[0] + 30)[0]
        """
        某分鐘最高價大於開盤價30點	 買進一口直至收盤
	    某分鐘最低價小於開盤價30點	 放空一口直至收盤
        """
        if len(below_open) == 0 and len(above_open) == 0:
            pass
        elif len(below_open) == 0:
            buy_price = dayData['dClose'].iloc[above_open[0]]
            sell_price = dayData['dClose'].iloc[-1]
            profit.append(sell_price - buy_price)
        elif len(above_open) == 0:
            buy_price = dayData['dClose'].iloc[below_open[0]]
            sell_price = dayData['dClose'].iloc[-1]
            profit.append(buy_price - sell_price)
        elif above_open[0] < below_open[0]:
            buy_price = dayData['dClose'].iloc[above_open[0]]
            sell_price = dayData['dClose'].iloc[-1]
            profit.append(sell_price - buy_price)
        else:
            buy_price = dayData['dClose'].iloc[below_open[0]]
            sell_price = dayData['dClose'].iloc[-1]
            profit.append(buy_price - sell_price)
            
#動量策略&停損 - 買好跌30點要停損          
def momentumloss():
    profit = []
    for date in trade_day:
        dayData = taiex_df[taiex_df['dDateTime']//10000 == date]
        
        below_open = np.where(dayData['dLowest'] <= dayData['dOpen'].iloc[0] - 30)[0]
        above_open = np.where(dayData['dHighest'] >= dayData['dOpen'].iloc[0] + 30)[0]
        
        if len(below_open) == 0 and len(above_open) == 0:
            pass
        elif len(below_open) == 0:
            buy_price = dayData['dClose'].iloc[above_open[0]]
            stop_loss = np.where(dayData['dLowest'].iloc[above_open[0]+1:] <= buy_price - 30)[0]
            if stop_loss.size > 0 :
                sell_price = dayData['dClose'].iloc[stop_loss[0]]
            else:
                sell_price = dayData['dClose'].iloc[-1]
            profit.append(sell_price - buy_price)
            
        elif len(above_open) == 0:
            buy_price = dayData['dClose'].iloc[below_open[0]] #放空 -> 賣高收低(賺下跌)
            stop_loss = np.where(dayData['dHighest'].iloc[below_open[0]+1:] >= buy_price + 30)[0]
            if stop_loss.size > 0 :
                sell_price = dayData['dClose'].iloc[stop_loss[0]]
            else: 
                sell_price = dayData['dClose'].iloc[-1]
            profit.append(buy_price - sell_price)
            
        elif above_open[0] < below_open[0]:
            buy_price = dayData['dClose'].iloc[above_open[0]]
            stop_loss = np.where(dayData['dLowest'].iloc[above_open[0]+1:] <= buy_price - 30)[0]
            if stop_loss.size > 0 :
                sell_price = dayData['dClose'].iloc[stop_loss[0]]
            else:
                sell_price = dayData['dClose'].iloc[-1]
            profit.append(sell_price - buy_price)
            
        else:
            buy_price = dayData['dClose'].iloc[below_open[0]] #放空
            stop_loss = np.where(dayData['dHighest'].iloc[below_open[0]+1:] >= buy_price + 30)[0]
            if stop_loss.size > 0 :
                sell_price = dayData['dClose'].iloc[stop_loss[0]]
            else:
                sell_price = dayData['dClose'].iloc[-1]
            profit.append(buy_price - sell_price)
            
    return profit

#def countprofit():
#    global profit
#    profit = []
#    for date in trade_day:
#        dayData = taiex_df[taiex_df['dDateTime']//10000 == date]
#        sell_price = stopprofitandloss()
#        profit.append(sell_price - dayData['dOpen'].iloc[0])

def show(profit):
    profit = np.array(profit)
    print('總損益點數:%d'% np.sum(profit))
    print('勝率:%f'%(np.sum(profit>0)/len(profit)))
    print('賺錢時平均獲利點數:%f'% (np.mean(profit[profit > 0])))
    print('賺錢時平均虧損點數:%f'% (np.mean(profit[profit <= 0])))
    plt.title('Daily Accumulated Points')
    plt.plot(np.cumsum(profit))
    plt.show()
    plt.title('Histogram of daily profits and losses')
    plt.hist(profit, bins=100)
    plt.show()

#profit = stopprofitandloss()
profit = momentumloss()
show(profit)

