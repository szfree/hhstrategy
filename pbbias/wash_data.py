import calendar
import sys
import datetime
import string
import sqlite3
import os

import numpy as np
import pandas as pd


setting = {
    'database' : 'hk.db',
    'folder' : '160503',
    'potential_inc': 0.8,
    'minimum_na' : 200000000,
    'cycle' : 4,  # weeks
    'top' : 20 # top items into the portfolio
}



def createDB():
    if os.path.exists(setting['database']):
        return

    db = sqlite3.connect(setting['database'])
    cu = db.cursor()
    sql = 'create table weeklyquota (pb5 float, pb7 float, sid varchar(12), sname varchar(30), tradeday varchar(10), adjclose float, marketcap float, pe float, pb float)'
    cu.execute(sql)
    db.commit()
    cu.close()
    db.close()




#stock_id, stock_name, date, adjclose,marketcap, pe, pb
def main():
    df = load_data()
    dfQuota = calc_potential_inc(df)
    dfPortfolio = build_portfolio(dfQuota)
   
    

def load_data():
    print('load data from csv files.')
    csvs = get_csv_list()

    isfirst = True
    cleaned_df = None
    for csv in csvs:
        print csv
        df = pd.read_csv(setting['folder']+'\\'+csv, skiprows=1, thousands=',', encoding='gbk', names=['sid','sname','tradeday','adjclose','marketcap','pb'])

        df.dropna(inplace=True)

        if isfirst:
            cleaned_df = df
            isfirst = False
        else:
            cleaned_df = cleaned_df.append(df)

    #calc net assets
    cleaned_df['netassets'] = cleaned_df['marketcap'] / cleaned_df['pb']
    #cleaned_df.sort_values(['sid','tradeday'], inplace=True)
    #cleaned_df.to_csv(setting['folder']+'\\'+'all.csv', encoding='gbk')
    print cleaned_df
    return cleaned_df


def calc_potential_inc(df=None):
    print('calculate the potential increasement...')
    print df
    gs = df.groupby(['sid'])
    
    df_data = None
    isfirst = True
    n = 1
    for k, g in gs:
        print(str(n)+':'+str(k))
        n=n+1

        tmpdf = g.copy()
        tmpdf['pb5'] = pd.rolling_mean(tmpdf['pb'], window=260)
        tmpdf['na5'] = pd.rolling_mean(tmpdf['netassets'], window=260)
        tmpdf.dropna(inplace=True)

        tmpdf['pb7'] = pd.rolling_mean(tmpdf['pb'], window=364)
        tmpdf['na7'] = pd.rolling_mean(tmpdf['netassets'], window=364)


        

        if isfirst :
            df_data = tmpdf
            isfirst = False
        else:
            df_data = df_data.append(tmpdf)

    print df_data
    df_data['pbbias5'] = df_data['pb5'] / df_data['pb'] -1
    df_data['potential_marketcap5'] = df_data['pb5'] * df_data['na5']
    df_data['potential_inc5'] = df_data['potential_marketcap5'] / df_data['marketcap'] - 1

    df_data['pbbias7'] = df_data['pb7'] / df_data['pb'] -1
    df_data['potential_marketcap7'] = df_data['pb7'] * df_data['na7']
    df_data['potential_inc7'] = df_data['potential_marketcap7'] / df_data['marketcap'] - 1


    df_data.sort_values(['tradeday','potential_inc5'], ascending=True, inplace=True)
    df_data = df_data[df_data['tradeday']>'2006-01-01']
    #df_data.to_csv('all.csv', encoding='gbk')

    

    #update the sell price 
    # print('calc the sell price...')
    # df_data.sort_values(['sid','tradeday'], inplace=True, ascending=True)
    # ln=0
    # length = len(df_data.index)
    # cycle = setting['cycle']
    # df_data['sellprice'] = df_data['adjclose']
    # print(df_data.info())

    # while ln+cycle<length:
    #     print(str(ln)+'--'+str(length))
    #     if str(df_data.iloc[ln:0]) != str(df_data.iloc[ln+cycle:0]):
    #         pass
    #     else:
    #         df_data.iloc[ln:12] = df_data.iloc[ln+cycle:3] #update the sellprice
    #     ln = ln + 1


    #remove stocks which are not match the standard
    # print('washing data.....')
    # df_data = df_data[df_data['netassets']>setting['minimum_na']]
    # df_data = df_data[df_data['pb']<50]
    # df_data = df_data[df_data['pb']>0.2] 
    # df_data = df_data[df_data['adjclose']>0.1]
    #df_data = df_data[df_data['netassets'] / df_data['na5'] < 2]
    #df_data = df_data[df_data['netassets'] / df_data['na5'] > 0.5]

    df_data.to_csv('r.csv',encoding='gbk')
    
    return df_data



def build_portfolio(df):
    print('build portfolio...')
    

    df.sort_values(['tradeday'], inplace=True)
    gb = df.groupby(['tradeday'])

    isfirst = True
    tops = setting['top']
    for k, g in gb:
        tmpdf = g[g['potential_inc5']>=setting['potential_inc']]
        if len(tmpdf.index) < setting['top']:
            continue
        p = tmpdf.copy()
        p.sort_values(['potential_inc5'],inplace=True, ascending=False)
        if isfirst:
            portfolio = p[0:tops]
            isfirst = False
        else:
            portfolio = portfolio.append(p[0:tops])

    portfolio.to_csv('p.csv', encoding='gbk')
    print('save portfolio success...')
    return portfolio

def calculate_return(df):
    pass

def calc_return(portfolio=pd.DataFrame(), quota=pd.DataFrame(), weeks=4, top=20, onecycle=False):

    if portfolio.empty:
        return pd.DataFrame()
    if quota.empty:
        return pd.DataFrame()

    if onecycle:
        return update_sellprice(portfolio, quota, weeks, top)

    
    gs = portfolio.groupby(['tradeday'])
    isfirst = True
    df = None
    for k, g in gs:
        tmpdf = calc_return(g, quota, weeks, top, True)
        if tmpdf.empty:
            continue

        if isfirst :
            isfirst = False
            df = tmpdf
        else:
            df = df.append(tmpdf)

    print('calc portfolio return, weeks='+str(weeks)+', top='+str(top))


def update_sellprice(x, position, ):
    cycle = setting['cycle']
    if position + cycle > len(df.index):
        return x
    if str(df.iloc[position:0]) != str(df_data.iloc[position+cycle:0]):
        return x

    return df.iloc[position+cycle:3] #update the sellprice










        

def get_value(strval):
    r = strval.strip().replace('"','').replace(',','')
    if r == '':
        r = 'NULL'
    return r



def get_csv_list():
    data = os.walk(setting['folder'])
    for root, dirs, files in data:
        if root.upper() == setting['folder'].upper():
            return files



def load_csv(csv):
    print('load data from csv file: ' + csv + '...')
    
    
    f = open(setting['folder']+'\\'+csv)
    lines = f.readlines()
    f.close()
    
    db =  sqlite3.connect(setting['database'])
    cu = db.cursor()
    
    skipfirstline = True
    for line in lines:

        if skipfirstline:
            skipfirstline = False
            continue

        items = line.split('","')

        sid = get_value(items[0])
        sname = get_value(items[1])
        sdate = get_value(items[2])
        sadjclose = get_value(items[3])
        smarketcap = get_value(items[4])
        spe = get_value(items[5])
        spb = get_value(items[6])
        
        
        sql = 'insert into weeklyquota (sid, sname, tradeday, adjclose, marketcap, pe,pb ) values ("'+sid+'", "'+sname+'","'+sdate+'",'+sadjclose+','+smarketcap+','+spe+','+spb+')'
        #print(sql)
        try:
            cu.execute(sql)
        except:
            print('sql error: ' + sql)
            raise

        print(sid + '--' + sdate)
        
        
        
    cu.close()
    db.commit()
    db.close()
    


main()
    
    
