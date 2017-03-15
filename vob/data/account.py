#coding:utf-8

import datetime
import collections
from portfolio import Portfolio

class Account(object):
    
    def __init__(self, **kwargs):
        """Simulator account data structure, can include serveral portfolios
        :kwargs: initcash, start_date, end_date [slippage]
        """
        self._init_cash = kwargs.get('initcash')
        self._start_date = kwargs.get('start_date')
        self._end_date = kwargs.get('end_date')
        if 'slippage' in kwargs:
            self._slippage = kwargs.get('slippage')

        #Portfolios seperated from strategies
        self._portfolios = collections.defaultdic(Portfolio)

        
