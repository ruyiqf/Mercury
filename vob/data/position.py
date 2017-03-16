#coding:utf-8
from order import Order

class Position(object):

    def __init__(self):
        self._intrument = None
        self._avg_cost = 0
        self._td_position = 0 #Today position number
        self._yd_position = 0 #Yesterday position number
        self._total_position = 0
        self._direction = None
        self._deal_quantity = 0 #Single direction traded number

    def calculate_avg_cost(self, order):
        self._avg_cost = (order.volume * order.price + 
                          self._avg_cost * self._deal_quantity) / (order.volume + self._deal_quantity)
        self._deal_quantity += order.volume
