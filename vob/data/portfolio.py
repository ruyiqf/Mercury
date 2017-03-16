#coding:utf-8
import datetime
import collections

from position import Position
from order import Order

class Portfolio(object):
    """Strategy core data structure corresponding to one strategy"""
    def __init__(self):
        #Positions dict whose key is instrument-direction
        self._positions = collections.defaultdic(Position)
        self._pnl = 0
        self._holding_pnl = 0
        self._offset_pnl = 0
        self._commission = 0
        self._margin = 0

    def _calculate_holding_pnl(self, order):
        """Calculate holding pnl"""
        pass

    def _calculate_offset_pnl(self, order):
        """Calculate offest pnl"""
        pass


