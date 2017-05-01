#coding:utf-8
import datetime
import collections
from .stock_portfolio import Portfolio

class StockAccount(object):
    
    def __init__(self, **kwargs):
        """Simulator stock account, can include serveral portfolios
        :kwargs: initcash, start_date, end_date, slippage, assets
        """
        self._init_cash = kwargs.get('initcash')
        self._start_date = kwargs.get('start_date')
        self._end_date = kwargs.get('end_date')
        self._slippage = kwargs.get('slippage')
        
        self._portfolios = collections.defaultdict(lambda:Portfolio(self))
        self._available_cash = self._init_cash
        self._market_value = .0
        self._total_assets = .0
        self._total_pnl = .0
        self._balance = self._init_cash
   
    @property
    def init_cash(self):
        return self._init_cash

    @property
    def portfolios(self):
        return self._portfolios

    @property
    def available_cash(self):
        return self._available_cash

    @property
    def market_value(self):
        return self.market_value

    @property
    def assets(self):
        return self._total_assets
    
    @property
    def pnl(self):
        return self._total_pnl

    @property
    def balance(self):
        return self._balance

    def update_account(self):
        self._market_value = sum([v.portfolio_value for v in self._portfolios.values()]) 
        self._total_assets = self._market_value + self._balance
        self._total_pnl = sum([v.portfolio_pnl for v in self._portfolios.values()])

    def update_balance(self, order_value):
        """Updating balance when process order
        :order_value: Positiv when selling, negative when buying
        """
        self._balance += order_value
        #Ignore frozen cash
        self._available_cash = self._balance
        
     
