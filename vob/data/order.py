#coding:utf-8
class Order(object):
    def __init__(self):
        self._instrument = None
        self._price = 0
        self._direction = None
        self._offset = None
        self._volume = 0
