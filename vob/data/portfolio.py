#coding:utf-8
import datetime
import collections

from position import Position
from order import Order
from bardata import BarData

class Portfolio(object):
    """Strategy core data structure corresponding to one strategy"""
    def __init__(self, account):
        #Positions dict whose key is instrument-direction
        self._positions = collections.defaultdic(Position)
        self._pnl = 0
        self._holding_pnl = 0
        self._offset_pnl = 0
        self._commission = 0
        self._margin = 0
        self._account = account #Father node point to account class

    def _calculate_holding_pnl(self, bardict):
        """Calculate holding pnl
        :bardict: bar simulate quotation bar data dict include bardata class
        """
        for elt in bardict:
            posi_long = self._search_position_by_orderid(elt + '-'+'long')
            posi_short = self._search_position_by_orderid(elt + '-'+'short')
            
            if posi_long.instrument == None:
                posi_long.instrument = elt
                posi_long.direction = 'long'
                posi_long.multiplier = bardict[elt].multiplier
                posi_long.margin_ratio = bardict[elt].margin_ratio
            if posi_short.instrument == None:
                posi_short.instrument = elt
                posi_short.direction = 'short'
                posi_short.multiplier = bardict[elt].multiplier
                posi_short.margin_ratio = bardict[elt].margin_ratio

            if (posi_long.deal_quantity - posi_short.deal_quantity) >= 0:
                self._holding_pnl = ((posi_long.deal_quantity - posi_short.deal_quantity) *
                                     (bardict[elt].lastprice - posi_long.avg_cost) *
                                     bardict[elt].multiplier)
            else:
                self._holding_pnl = (abs(posi_long.deal_quantity - posi_short.deal_quantity) *
                                     (posi_short.avg_coset - bardict[elt].lastprice) * 
                                     bardict[elt].multiplier)
            posi_long.lastprice = posi_short.lastprice = bardict[elt].lastprice
            posi_long.update_margin()
            posi_short.update_margin()
        self._calculate_pnl()
        self._calculate_margin()
        self._account.update_account()
       
    def _calculate_offset_pnl(self, instrument):
        """Calculate offest pnl
        :instrument: contract name
        """
        posi_long = self._search_position_by_order(instrument+'-'+'long')
        posi_short = self._search_position_by_order(instrument+'-'+'short')
        self._offset_pnl = (min(posi_long.deal_quantity, posi_short.deal_quantity) *
                            (posi_short.avg_cost - posi_long.avg_cost) *
                            posi_long.multiplier)
        self._calculate_pnl()
        self._calculate_margin()
        self._account.update_account()

    def _calculate_pnl(self):
        self._pnl = self._holding_pnl + self._offset_pnl
    
    def _search_position_by_orderid(self, orderid):
        return self._positions[orderid]

    def _calculate_margin(self):
        self._margin = sum([v.margin for v in positions.values()]

    def process_order(self, order):
        """Procedure of booking order when order is traded
        :order: Order class data
        """
        cur_posi = self._search_position_by_orderid(order.instrument+'-'+order.direction)
        cur_posi.update_position(order)

    def process_settle(self, bardict):
        """Process settlement bardict
        :bardict: Bar datas
        """
        #Temparorily use last price as settlement price, so first procedure is like normal bar
        self._calculate_holding_pnl()
        for elt in bardict:
            cur_long = self._search_position_by_orderid(elt+'-'+'long')
            cur_short = self._search_position_by_orderid(elt+'-'+'short')
            cur_long.move_td2yd_position()
            cur_short.move_td2yd_position()

    def process_normal_bar(self, bardict):
        """Process normal bardict event
        :bardict: Bar datas
        """
        self._calculate_holding_pnl(bardict)
