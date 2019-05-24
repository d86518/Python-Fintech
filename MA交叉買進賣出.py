import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime

taiex_df= pd.read_csv('TXF20112015_original.csv')
del taiex_df['dCode']
trade_day = np.unique(taiex_df['dDateTime']//10000)

#開始進行MA計算
taiex_df['MA_10']=taiex_df['dClose'].rolling(10,axis=0).sum()/10
taiex_df['MA_20']=taiex_df['dClose'].rolling(20,axis=0).sum()/20

#畫圖
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
    
    
def plot_MA(df,col1,col2):
    time =pd.to_datetime(df['dDateTime'], format='%Y%m%d%H%M')
    plt.plot(time,df[col1],'r-',label=col1)
    plt.plot(time,df[col2],'b-',label=col2)
    plt.plot(time,df['dClose'],'k-',label='price')
    plt.title('Moving Average')
    plt.xlabel('Datetime')
    plt.ylabel('MA')
    plt.legend()
    plt.show()

    
def plot_MA_cross(df,col1,col2):
    time =pd.to_datetime(df['dDateTime'], format='%Y%m%d%H%M')
    plt.plot(time,df[col1],'r-',label= col1)
    plt.plot(time,df[col2],'b-',label= col2)
    plt.plot(time,df['dClose'],'g-',label='price')
    plt.title('Cross Moving Average')
    plt.xlabel('Datetime')
    plt.ylabel('MA')
    plt.legend()
    plt.show()
    
plot_MA(taiex_df.loc[:][:300],'MA_10','MA_20')
#%%
taiex_df= pd.read_csv('TXF20112015_original.csv')
del taiex_df['dCode']
trade_day = np.unique(taiex_df['dDateTime']//10000)

#%%
taiex_df['MA_10']=taiex_df['dClose'].rolling(10).sum()/10
taiex_df['MA_20']=taiex_df['dClose'].rolling(20).sum()/20
taiex_df['MA_60']=taiex_df['dClose'].rolling(60).sum()/60
#%%
def cross(df,fast ,slow):
    df['diff'] = df[fast] - df[slow] # 計算「短線」減去「長線」之差
    asign = np.sign(df['diff']) # asign 會在這個數大於 0 時回傳 +1，小於 0 時回傳-1
    asign[np.where(asign==0)[0]]=1 # +1是當短線高於長線時，-1是長線高於短線時 
    # 而黃金交叉（短線從長線下面穿越到長線）就是在 -1 到 +1 之時
    cross_signal = (np.where(np.roll(asign, 1)<asign))[0] 
    taiex_df['golden_cross']=0
    taiex_df['golden_cross'][cross_signal] = 1 # 把結果存到 golden_cross 裡面
    
    # 而死亡交叉（短線從長線上面跌落到長線）就是在 +1 到 -1 之時
    death_signal = (np.where(np.roll(asign, 1)>asign))[0]  
    taiex_df['death_cross']=0
    taiex_df['death_cross'][death_signal]=-1   # 把結果存到 death_cross 裡面
    # 為了和黃金交叉有分別，把本來的 1 改成 -1
    
    print("黃金交叉總共有:",taiex_df['golden_cross'].sum(),"次")
    print("死亡交叉總共有:",-taiex_df['death_cross'].sum(),"次")
    # 理論上要一樣多或是只差一，因為穿越上去要再穿越下來，才能再穿越上去
    return taiex_df

#%%
print('=====策略1.1=====')
TotalProfit = []
for date in trade_day:
    dayData = taiex_df[taiex_df['dDateTime']//10000 == date].reset_index(drop=True)
    # 進場判斷
    Index=0
    i=0
    Profit=0
    while i<len(dayData):
        # 當價格向上突破MA 進場做多
        if dayData['golden_cross'][i]==1:
            Index=Index+1
            OrderTime=dayData['dDateTime'][i]
            OrderPrice=dayData['dClose'][i]
            i=i+1
        #若沒有進場，則不進行接下來的出場判斷
        if Index==0:   
            i=i+1
            continue
        # 多單出場判斷
        elif Index==1:
            while i<len(dayData):
                if i==len(dayData)-1:
                    Index=Index-1
                    CoverTime=dayData['dDateTime'][i]
                    CoverPrice=dayData['dClose'][i]
                elif taiex_df['death_cross'][i]==-1:
                    Index=Index-1
                    CoverTime=dayData['dDateTime'][i]
                    CoverPrice=dayData['dClose'][i]
                    break
                i=i+1
        Profit=Profit+CoverPrice-OrderPrice
    TotalProfit+=[Profit]
#        print('BuyOrderTime',OrderTime,'OrderPrice',OrderPrice,'CoverTime',CoverTime,'CoverPrice',CoverPrice,'Profit',Profit)
    print(date)
profit_show(TotalProfit)
#%% 1.2
print('=====策略1.2=====')
TotalProfit = []
for date in trade_day:
    print(date)
    dayData = taiex_df[taiex_df['dDateTime']//10000 == date].reset_index(drop=True)
    # 進場判斷
    Index=0
    Profit=0
    i=0
    while i<len(dayData):
        # 當價格向上突破MA 進場做空
        if dayData['death_cross'][i]==-1:
#            print(i)
            Index=Index-1
            OrderTime=dayData['dDateTime'][i]
            OrderPrice=dayData['dClose'][i]
            i=i+1
        # 若沒有進場，則不進行接下來的出場判斷
        if Index==0:   
            i=i+1
            continue
        # 多單出場判斷
        elif Index==-1:
            while i<len(dayData):
#                print(i)
                if i==len(dayData)-1:
#                    print(i)
                    Index=Index+1
                    CoverTime=dayData['dDateTime'][i]
                    CoverPrice=dayData['dClose'][i]
                elif taiex_df['golden_cross'][i]==1:
#                    print(i)             
                    Index=Index+1
                    CoverTime=dayData['dDateTime'][i]
                    CoverPrice=dayData['dClose'][i]
                    break
                i=i+1
            Profit=Profit+OrderPrice-CoverPrice
        TotalProfit+=[Profit]
profit_show(TotalProfit)
#%% 
"""
找出當天第一個遇到交叉點，來當作當天的策略
(假設第一個遇到的是黃金交叉，當天做策略1.1；反之)
"""

cross(taiex_df,'MA_10','MA_20')
cross(taiex_df,'MA_10','MA_60')
cross(taiex_df,'MA_20','MA_60')

print('=====策略1.3=====')
TotalProfit = []
for date in trade_day:
    print(date)
    dayData = taiex_df[taiex_df['dDateTime']//10000 == date].reset_index(drop=True)
    # 進場判斷
    Index=0
    Profit=0
    i=0
    death_cross = 0
    golden_cross = 0
    #判斷先死亡或黃金
    for i in range(len(dayData)):
        if dayData['death_cross'][i]==-1:
            death_cross = 1
            break
        elif dayData['golden_cross'][i]==1:
            golden_cross = 1
            break
        
    #第一個遇到的是死亡交叉，當天做策略1.2
    if death_cross == 1:
        print('death_cross first for ',date)
        while i<len(dayData):
            # 若沒有進場，則不進行接下來的出場判斷
            if Index==0:   
                i=i+1
                continue
            # 當價格向上突破MA 進場做空
            if dayData['death_cross'][i]==-1:
    #            print(i)
                Index=Index-1
                OrderTime=dayData['dDateTime'][i]
                OrderPrice=dayData['dClose'][i]
                i=i+1
            # 多單出場判斷
            elif Index==-1:
                while i<len(dayData):
    #                print(i)
                    if i==len(dayData)-1:
    #                    print(i)
                        Index=Index+1
                        CoverTime=dayData['dDateTime'][i]
                        CoverPrice=dayData['dClose'][i]
                    elif taiex_df['golden_cross'][i]==1:
    #                    print(i)             
                        Index=Index+1
                        CoverTime=dayData['dDateTime'][i]
                        CoverPrice=dayData['dClose'][i]
                        break
                    i=i+1
                Profit=Profit+OrderPrice-CoverPrice
            TotalProfit+=[Profit]
            
    #第一個遇到的是黃金交叉，當天做策略1.1        
    elif golden_cross == 1:
       print('golden_cross first for ',date)
       while i<len(dayData):
            # 當價格向上突破MA 進場做空
            if dayData['death_cross'][i]==-1:
    #            print(i)
                Index=Index-1
                OrderTime=dayData['dDateTime'][i]
                OrderPrice=dayData['dClose'][i]
                i=i+1
            # 若沒有進場，則不進行接下來的出場判斷
            if Index==0:   
                i=i+1
                continue
            # 多單出場判斷
            elif Index==-1:
                while i<len(dayData):
    #                print(i)
                    if i==len(dayData)-1:
    #                    print(i)
                        Index=Index+1
                        CoverTime=dayData['dDateTime'][i]
                        CoverPrice=dayData['dClose'][i]
                    elif taiex_df['golden_cross'][i]==1:
    #                    print(i)             
                        Index=Index+1
                        CoverTime=dayData['dDateTime'][i]
                        CoverPrice=dayData['dClose'][i]
                        break
                    i=i+1
                Profit=Profit+OrderPrice-CoverPrice
            TotalProfit+=[Profit] 
            
profit_show(TotalProfit)