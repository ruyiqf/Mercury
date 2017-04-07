#coding:utf-8
class Order(object):
    def __init__(self):
        self._instrument = None
        self._price = 0
        self._direction = None
        self._offset = None
        self._volume = 0

        # Using for firm bargain
        self._strategy_name = None
        self._algotype = None
        self._orderstyle = None
        self._maxcancelnum = 0
        
    @property
    def strategy_name(self):
        return self._strategy_name
    @strategy_name.setter
    def strategy_name(self, value):
        if isinstance(value, str):
            self._strategy_name = value

    @property
    def algotype(self):
        return self._algotype
    @algotype.setter
    def algotype(self, value):
        if isinstance(value, str):
            self._algotype = value

    @property
    def orderstyle(self):
        return self._orderstyle
    @orderstyle.setter
    def orderstyle(self, value):
        if isinstance(value, str):
            self._orderstyle = value

    @property
    def maxcancelnum(self):
        return self._maxcancelnum
    @maxcancelnum.setter
    def maxcancelnum(self, value):
        if isinstance(value, int):
            self._maxcancelnum = value

    @property
    def instrument(self):
        return self._instrument
    @instrument.setter
    def instrument(self, value):
        if isinstance(value, str):
            self._instrument = value

    @property
    def price(self):
        return self._price
    @price.setter
    def price(self, value):
        if isinstance(value, float):
            self._price = value

    @property
    def direction(self):
        return self._direction
    @direction.setter
    def direction(self, value):
        if isinstance(value, str):
            self._direction = value

    @property
    def offset(self):
        return self._offset
    @offset.setter
    def offset(self, value):
        if isinstance(value, str):
            self._offset = value

    @property
    def volume(self):
        return self._volume
    @volume.setter
    def volume(self, value):
        if isinstance(value, int):
            self._volume = value

  
