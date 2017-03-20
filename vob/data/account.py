#coding:utf-8

import datetime
import collections
from .portfolio import Portfolio

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
        self._portfolios = collections.defaultdict(Portfolio)
        
        self._static_equity = self._init_cash
        self._dynamic_equity = self._init_cash
        self._total_pnl = 0
        self._total_margin = 0
        self._total_commission = 0
        self._available_cash = self._init_cash
        self._risk_measure = 0
        
    @property
    def static_equity(self):
        return self._static_equity
    
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

    @property
    def rick_measure(self):
        return self._risk_measure

    def settlement(self, bardict):
        """Settlement is the function from top to bottom aimed to settle all portfolios"""
        for elt in self.portfolios:
            self.portfolios[elt].process_settle(bardict)

    def update_account(self):
        self._total_pnl = sum([v.pnl for v in self.portfolios.values()])
        self._total_margin = sum([v.margin for v in self.portfolios.values()])
        self._total_commission = sum([v.commission for v in self.portfolios.values()])
        self._dynamic_equity = self._available_cash + self._total_margin + self._total_pnl
        self._risk_measure = self._total_margin / self._dynamic_equity

    def update_available(self, delta_margin):
        """For portfolio available_cash is viewing, so need this interface
        :delta_margin: change of margin in portfolio
        """
        self._available_cash += delta_margin
        
