#coding:utf-8
import datetime

class BarData(object):

    def __init__(self):
        self._instrument = None
        self._lastprice = 0.0
        self._margin_ratio = 0.0
        self._multiplier = 0.0
        self._date = None
        self._volume = 0

        #Using firm bargain
        self._bid = 0.0
        self._ask = 0.0
        self._bidvolume = 0.0
        self._askvolume = 0.0

    @property
    def bid(self):
        return self._bid
    @bid.setter
    def bid(self, value):
        if isinstance(value, float):
            self._bid = value
    
    @property
    def ask(self):
        return ask
    @ask.setter
    def ask(self, value):
        if isinstance(value, float):
            self._ask = value

    @property
    def bidvolume(self):
        return self._bidvolume
    @bidvolume.setter(self, value):
        if isinstance(value, int):
            self._bidvolume = value

    @property
    def askvolume(self):
        return self._askvolume
    @askvolume.setter(self, value):
        if isinstance(value, int):
            selfk._askvolume = value

    @property
    def volume(self):
        return self._volume
    @volume.setter
    def volume(self, value):
        if isinstance(value, int):
            self._volume = value

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
            self._multiplier = value
