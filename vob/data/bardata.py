#coding:utf-8
class BarData(object):

    def __init__(self):
        self._instrument = None
        self._lastprice = 0.0
        self._margin_ratio = 0.0
    
    @property
    def instrument(self):
        return self._instrument
    @instrument.setter(self, value):
        if isinstance(value, str):
            self._instrument = value

    @property
    def lastprice(self):
        return self._lastprice
    @lastprice.setter(self, value):
        if isinstance(value, float):
            self._lastprice = value
        
    @property
    def margin_ratio(self):
        return self._margin_ratio
    @margin_ratio.setter(self, value):
        if isinstance(value, float):
            self._margin_ratio = value
