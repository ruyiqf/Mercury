#coding:utf-8
import pandas as pd
import numpy as np
import talib

class Quotation(object):
    """Quotation will provide mock data and recieve real quotation data"""
    def __init__(self):
        pass

    def history(self, databar, period, indicator):
        """Recieve mock data as databar dataframe format
        :databar: mock data bar, flexible, means will be changed by indicator, one dimension or several dimensions
        :period: time interval, flexbile too
        :indicator: include ['sma','macd','atr' ...]
        """
        if indicator == 'sma':
            try:
                sma0 = talib.SMA(np.array(databar.low), timeperiod = period)
                sma1 = talib.SMA(np.array(databar.close), timeperiod = period)
                sma2 = talib.SMA(np.array(databar.high), timeperiod = period)
                return pd.DataFrame({'sma0':sma0, 'sma1':sma1, 'sma2':sma2}, index=pd.DatetimeIndex(databar.date))
            except KeyError:
                print('Pls check databar whether is dataframe')
                
        elif indicator == 'atr':
            try:
                atr = talib.ATR(np.array(databar.high), np.array(databar.low), np.array(databar.close), timeperiod = period)
                return pd.DataFrame({'atr':atr}, index=pd.DatetimeIndex(databar.date))
            except KeyError:
                print('Pls check databar whether is dataframe')
                return None
        elif indicator == 'macd':
            try:
                macd, macdsignal, macdhist = talib.MACD(databar, 
                                                        fastperiod = period['fastperiod'],
                                                        slowperiod = period['slowperiod'],
                                                        signalperiod = period['signalperiod'])
                
                return pd.DataFrame({'macd':macd, 'macdsignal':macdsignal, 'macdhist':macdhist}, index=pd.DatetimeIndex(databar.date))
            except KeyError:
                print('Pls check databar whether is dataframe')
                return None
                
        
