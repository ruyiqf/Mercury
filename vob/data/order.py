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
        self._sinterval = 0
        self._signalid = None
        self._size = 0
        self._wttime = 0
        self._clientid = None

    @property
    def clientid(self):
        return self._clientid
    @clientid.setter
    def clientid(self, value):
        if isinstance(value, str):
            self._clientid = value

    @property
    def size(self):
        return self._size
    @size.setter
    def size(self, value):
        if isinstance(value, int):
            self._size = value

    @property
    def wttime(self):
        return self._wttime
    @wttime.setter
    def wttime(self, value):
        if isinstance(value, int):
            self._wttime = value

    @property
    def signalid(self):
        return self._signalid
    @signalid.setter
    def signalid(self, value):
        if isinstance(value, str):
            self._signalid = value

    @property
    def sinterval(self):
        return self._sinterval
    @sinterval.setter
    def sinterval(self, value):
        if isinstance(value, int):
            self._sinterval = value

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

  
