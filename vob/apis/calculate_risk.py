#coding:utf-8
from __future__ import division
import numpy as np
import pandas as pd

class RiskCal(object):
    def __init__(self, static_equity_list):
        """Calulate all risk indicators
        :static_equity_list: Construct every static equity by settled during trading dates
        """
        self._static_equity_list = static_equity_list
        self._max_returns = -np.inf
        self._max_drawdown = .0
        self._riskfree_returns = .03
        self._annualized_returns = .0
        self._volatility = .0
        self._sharpe = .0
        self._ret_df = None

    @property
    def riskfree_returns(self):
        return self._riskfree_returns
    @riskfree_returns.setter
    def riskfree_returns(self, value):
        if isinstance(value, float):
            self._riskfree_returns = value

    @property
    def ret_df(self):
        return self._ret_df

    def calculate(self):
        date_index = pd.DatetimeIndex([date for date, account in self._static_equity_list])
        print(date_index)
        daily_net_worth = [account._static_equity/account._init_cash for date, account in self._static_equity_list]
         
        self._annualized_returns = daily_net_worth[-1] ** 360 / len(daily_net_worth) - 1
        self._volatility = 252 ** 0.5 * np.std(daily_net_worth)  
        self._max_drawdown = max(daily_net_worth) - min(daily_net_worth) 
        self._sharpe = (np.mean(daily_net_worth) - self._riskfree_returns) / self._volatility
        self._ret_df = pd.DataFrame({'net_worth':daily_net_worth}, index=date_index)
        print(self._ret_df)
