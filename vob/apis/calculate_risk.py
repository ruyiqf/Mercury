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
        daily_net_worth = [account._static_equity/account._init_cash for date, account in self._static_equity_list]
        self._volatility = 252 ** 0.5 * np.std(daily_net_worth)  
        self._max_drawdown = max(daily_net_worth) - min(daily_net_worth) 
        self._sharpe = (np.mean(daily_net_worth) - self._riskfree_returns) / self._volatility
        self._ret_df = pd.DataFrame({'net_worth':daily_net_worth}, index=date_index)
        self._ret_df = self._ret_df.sort_index()
    
    def draw(self, title):
        import matplotlib
        import matplotlib.pyplot as plt
        import matplotlib.image as mpimg
        from matplotlib import gridspec
        plt.style.use('ggplot')
        red = '#aa4643'
        blue = '#4572a7'
        black = '#000000'
        figsize = (18,6)
        f = plt.figure(title, figsize=figsize)
        gs = gridspec.GridSpec(10,8)
        font_size = 12
        value_font_size = 11
        label_height, value_height = 0.8, 0.6
        fig_data = [
            (0.00, label_height, value_height, 'Max Down', '{0:.3%}'.format(self._max_drawdown), red, black),
            (0.30, label_height, value_height, 'Sharpe', '{0:.3}'.format(self._sharpe), red, black),
            (0.60, label_height, value_height, 'Volatility',  '{0:3%}'.format(self._volatility), red, black)]
       
        ax = plt.subplot(gs[:3, :-1])
        ax.axis('off')
        for x, y1, y2, label, value, label_color, value_color in fig_data:
            ax.text(x, y1, label, color=label_color, fontsize=font_size)
            ax.text(x, y2, value, color=value_color, fontsize=value_font_size)
       
        ax = plt.subplot(gs[4:,:])
        ax.get_xaxis().set_minor_locator(matplotlib.ticker.AutoMinorLocator())
        ax.get_yaxis().set_minor_locator(matplotlib.ticker.AutoMinorLocator())
        ax.grid(b=True, which='minor', linewidth=.2)
        ax.grid(b=True, which='major', linewidth=1)
        ax.plot(self._ret_df['net_worth'], label='strategy', alpha=1, linewidth=2, color=red)
        vals = ax.get_yticks()
        ax.set_yticklabels(['{:3.2f}%'.format(x*100) for x in vals])
        leg = plt.legend(loc='upper left')
        leg.get_frame().set_alpha(0.5)
        plt.show()
