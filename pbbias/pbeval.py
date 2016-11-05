import calendar
import sys
import datetime
import string
import sqlite3
import os

import numpy as np
import pandas as pd


setting = {
    'folder' : '20161010',

}





#stock_id, stock_name, date, adjclose, pb
def main():
    df = load_data()
    dfQuota = eval_pb_bias(df)
    
   
    

def load_data():
    print('load data from csv files.')
    csvs = get_csv_list()
    
    dfpb = pd.DataFrame()
    for csv in csvs:
        df = pd.read_csv(setting['folder']+'\\'+csv, skiprows=1, thousands=',', encoding='gbk', names=['sid','sname','tradeday','adjclose','pb'])

        df.dropna(inplace=True)

        if dfpb.empty:
            dfpb = df
        else:
            dfpb = dfpb.append(df)
    return dfpb


def eval_pb_bias(df=None):
    print('calculate the potential increasement based on pb bias...')
    
    gs = df.groupby(['sid'])
    
    df_data = pd.DataFrame()
    n = 1
    for k, g in gs:
        print(str(n)+':'+str(k))
        n=n+1

        tmpdf = g.copy()
        tmpdf['pb5'] = pd.rolling_mean(tmpdf['pb'], window=52*5)

        if df_data.empty:
        	df_data = tmpdf
        else:
        	df_data = df_data.append(tmpdf)
        

    
    df_data['pbbias5'] = df_data['pb5'] / df_data['pb'] -1


    df_data.sort_values(['tradeday','pbbias5'], ascending=False, inplace=True)

    df_data.to_csv('r.csv',encoding='gbk')
    
    return df_data



def get_csv_list():
    data = os.walk(setting['folder'])
    for root, dirs, files in data:
        if root.upper() == setting['folder'].upper():
            return files




main()
    
    
