#coding:utf-8
import collections
from enum import Enum

class Event(object):

    def __init__(self, event_type, data={}):
        self.event_type = event_type
        self.data = data

class EventBus(object):
    def __init__(self):
        self._listeners = collections.defaultdict(list)
    
    def add_listeners(self, event, handler):
        self._listeners[event].append(handler)
    
    def pop_listeners(self, event, *args, **kwargs):
        for h in self._listeners[event]:
            h(*args, **kwargs)

class EVENT(Enum):
    # Will trigger init function in strategies
    INIT_EVENT = 'init_strategy'
    # Will trigger trading_logic in strategies, this ticker will be changed by frequency
    NORMAL_TICKER_EVENT = 'normal_tick'
    # Will trigger context account settlement 
    SETTLEMENT_EVENT = 'settlement_account'
