#coding:utf-8
from .stock_order import Order

class Position(object):

    def __init__(self):
        self._instrument = None
        self._avg_cost = .0
        self._volume = 0
        self._lastprice = .0
    
    @property
    def avg_cost(self):
        return self._avg_cost

    @property
    def volume(self):
        return self._volume
    
    @property
    def lastprice(self):
        return self._lastprice
    @lastprice.setter(self, value):
        if isinstance(value, float):
            self._lastprice = value
           
    def calculate_avg_cost(self, order):
        if order.direction == 'buy':
            self._avg_cost = (order.volume * order.price +
                              self._avg_cost * self._volume) / (order.volume + self._volume)
        elif order.direction == 'sell':
            if self._volume - order.volume > 0:
                self._avg_cost = (self._avg_cost * self._volume -
                                  order.volume * order.price) / (self._volume - order.volume)
            elif self._volume - order.volume == 0:
                self._avg_cost = 0.0
            else:
                print('Error position: %d less then order volume: %d'%(self._volume, order.volume))

    def update_position(self, order):
        if order.diretion == 'buy':
            self._volume += order.volume
        elif order.direction == 'sell':
            self._volume -= order.volume
