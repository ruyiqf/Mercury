#coding:utf-8
from .order import Order

class Position(object):

    def __init__(self):
        self._instrument = None
        self._avg_cost = 0
        self._td_position = 0 #Today position number
        self._yd_position = 0 #Yesterday position number
        self._total_position = 0
        self._direction = None
        self._deal_quantity = 0 #Single direction traded number
        self._margin_ratio = 0.0
        self._mutiplier = 0.0
        self._margin = 0.0
        self._lastprice = 0.0

    def _calculate_avg_cost(self, order):
        self._avg_cost = (order.volume * order.price + 
                          self._avg_cost * self._deal_quantity) / (order.volume + self._deal_quantity)
        self._deal_quantity += order.volume

    def update_position(self, order):
        #Update avg cost first
        self._calculate_avg_cost(order) 
        #Update position by offset
        if order.offset == 'open':
            self._td_position += order.volume
            self._total_position = self._td_position + self._yd_position
        elif order.offset == 'close':
            self._yd_position -= order.volume
            delta = 0 if self._yd_position >=0 else self._yd_position
            self._td_position += delta
            self._yd_position = 0 if delta < 0 else self._yd_position
        elif order.offset == 'closetoday':
            self._td_position -= order.volume
            delta = 0 if self._td_position >=0 else self._td_position
            self._yd_position += delta
            self._td_position = 0 if delta < 0 else self._td_position
        self._total_position = self._td_position + self._yd_position
        self.update_margin()
        
    def move_td2yd_position(self, settle_price):
        """If bardata trigger settlement event need move position
        :settle_price: price of settlement
        """
        self._yd_position += self._td_position
        self._td_position = 0
        self._deal_quantity = 0
        self._avg_cost = settle_price if self._total_position > 0 else 0
        self._lastprice = settle_price
        
    def update_margin(self):
        self._margin = self._lastprice * self._total_position * self._margin_ratio * self._multiplier
        
    @property
    def instrument(self):
        return self._instrument
    @instrument.setter
    def instrument(self, value):
        if isinstance(value, str):
            self._instrument = value
    
    @property
    def direction(self):
        return self._direction
    @direction.setter
    def direction(self, value):
        if isinstance(value, str):
            self._direction = value

    @property
    def deal_quantity(self):
        return self._deal_quantity

    @property
    def avg_cost(self):
        return self._avg_cost

    @property
    def margin_ratio(self):
        return self._margin_ratio
    @margin_ratio.setter
    def margin_ratio(self, value):
        if isinstance(value, float):
            self._margin_ratio = value
    
    @property
    def multiplier(self):
        return self._multiplier
    @multiplier.setter
    def multiplier(self, value):
        if isinstance(value, float):
            self._multiplier = value

    @property
    def margin(self):
        return self._margin
    
    @property
    def lastprice(self):
        return self._lastprice
    @lastprice.setter
    def lastprice(self, value):
        if isinstance(value, float):
            self._lastprice = value

    @property
    def today_position(self):
        return self._td_position
        
