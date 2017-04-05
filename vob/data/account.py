#coding:utf-8

import datetime
import collections
import copy
from .portfolio import Portfolio
from .settledata import SettleData

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
        self._portfolios = collections.defaultdict(lambda:Portfolio(self))
        
        self._static_equity = self._init_cash
        self._dynamic_equity = self._init_cash
        self._total_pnl = 0.0
        self._total_margin = 0.0
        self._total_commission = 0.0
        self._available_cash = self._init_cash
        self._risk_measure = 0

    @property
    def init_cash(self):
        return self._init_cash

    @property
    def portfolios(self):
        return self._portfolios 

    @property
    def static_equity(self):
        return self._static_equity
    @static_equity.setter
    def static_equity(self, value):
        if isinstance(value, float):
            self._static_equity = value
    
    @property
    def dynamic_equity(self):
        return self._dynamic_equity

    @property
    def margin(self):
        return self._total_margin

    @property
    def pnl(self):
        return self._total_pnl
    
    @property
    def commission(self):
        return self._total_commission
    
    @property
    def available(self):
        return self._available_cash
    @available.setter
    def available(self, value):
        if isinstance(value, float):
            self._available_cash = value

    @property
    def rick_measure(self):
        return self._risk_measure

    def settlement(self, retlist, bardata):
        """Settlement is the function from top to bottom aimed to settle all portfolios
        :retlist: strategy context data, need put settlement result into retlist
        :bardata: every instrument has one dict data
        """
        for elt in self.portfolios:
            self.portfolios[elt].process_settle(bardata)

        retlist.append((bardata.date, SettleData(copy.copy(self.__dict__))))

    def update_account(self):
        pre_pnl = self._total_pnl
        self._total_pnl = sum([v.pnl for v in self.portfolios.values()])
        delta_pnl = self._total_pnl - pre_pnl
        pre_margin = self._total_margin
        self._total_margin = sum([v.margin for v in self.portfolios.values()])
        delta_margin = pre_margin - self._total_margin
        self._total_commission = sum([v.commission for v in self.portfolios.values()])
        self._available_cash = self._available_cash + delta_pnl + delta_margin
        self._dynamic_equity = self._available_cash + self._total_margin
        self._risk_measure = self._total_margin / self._dynamic_equity
