#coding:utf-8

class Risk(object):
    def __init__(self):
        self._volatility = .0
        self._sharpe = .0
        self._max_drawdown = .0

    def __repr__(self):
        return 'Risk({0})'.format(self.__dict__)
