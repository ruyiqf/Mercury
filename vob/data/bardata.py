#coding:utf-8
import datetime

class BarData(object):

    def __init__(self):
        self._instrument = None
        self._lastprice = 0.0
        self._margin_ratio = 0.0
        self._multiplier = 0.0
        self._date = None
    
    @property
    def instrument(self):
        return self._instrument
    @instrument.setter
    def instrument(self, value):
        if isinstance(value, str):
            self._instrument = value

    @property
    def lastprice(self):
        return self._lastprice
    @lastprice.setter
    def lastprice(self, value):
        if isinstance(value, float):
            self._lastprice = value
        
    @property
    def margin_ratio(self):
        return self._margin_ratio

    @margin_ratio.setter
    def margin_ratio(self, value):
        if isinstance(value, float):
            self._margin_ratio = value

    @property
    def date(self):
        return self._date
    @date.setter
    def date(self, value):
        if isinstance(value, datetime.datetime):
            self._date = value

    @property
    def multiplier(self):
        return self._multiplier
    @multiplier.setter
    def multiplier(self, value):
        if isinstance(value, float):
            self._multipler = value
