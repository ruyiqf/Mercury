#coding:utf-8
import collections
from .stock_position import Position

class Portfolio(object):
    """Stock portfolio data strcuture"""
    def __init__(self, account):
        self._positions = collections.defaultdict(Position)
        self._pnl = .0
        self._holding_pnl = .0
        self._offset_pnl = .0
        self._account = account
        self._portfolio_value = .0

    @property
    def pnl(self):
        return self._pnl

    @property
    def portfolio_value(self):
        return self._portfolio_value

    @property
    def positions(self):
        return self._position

    def _calculate_holding_pnl(self, bardata):
        """Calculate holding pnl
        :bardata: bar data specially using stock quotation
        """
        posi = self._search_position_by_orderid(bardata.instrument)
        if posi.instrument == None:
            posi.instrument = bardata.instrument
        
        posi.lastprice = bardata.lastprice
        self._holding_pnl = (bardata.lastprice - posi.avg_cost) * posi.volume
          
    def _calculate_pnl(self):
        self._pnl = self._holding_pnl + self._offset_pnl

    def _search_position_by_orderid(self, orderid):
        return self._positions[orderid]

    def _calculate_market_value(self):
        self._portfolio_value = sum([v.avg_cost*v.volume for v in self._positions])

    def process_order(self, order):
        """Process of booking order when order is traded
        :order: Order class data for stock specially
        """
        if order.direction == 'sell':
            cur_posi = self._search_position_by_orderid(order.instrument)
            self._offset_pnl += (order.price - cur_posi.avg_cost) * order.volume
            cur_posi.calculate_avg_cost(order)
            cur_posi.update_position(order)
            self._account.update_balance(order.price*order.volume)
        elif order.direction == 'buy':
            cur_posi = self._search_position_by_orderid(order.instrument)
            cur_posi.calculate_avg_cost(order)
            cur_posi.update_position(order)
            self._account.update_position(-order.price*order.volume)
        self._account.update_account()
        self._calculate_market_value()

    def process_normal_bar(self, bardata):
        """Process normal bardata event
        :bardata: Bar data
        """
        self._calculate_holding_pnl(bardata)
        self._calculate_market_value()
        
