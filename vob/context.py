#coding:utf-8
import time
from .data import DataProxy, Account
from .event import EventSource, EventBus, EVENT

class Context(object):
    """Need say something Wow, will replace environment object"""
    def __init__(self):
        self._data_proxy = None
        self._event_source = None
        self._account = None
        self._event_bus = None
        self._scope = None # Strategy execution scope
        self._frequency = None
        self._start_date = None
        self._end_date = None
    
    @property
    def scope(self):
        return self._scope

    @scope.setter
    def scope(self, value):
        self._scope = value
        
    @property
    def start_date(self):
        return self._start_date

    @start_date.setter
    def start_date(self, value):
        if isinstance(value, str):
            self._start_date = value

    @property
    def end_date(self):
        return self._end_date

    @end_date.setter
    def end_date(self, value):
        if isinstance(value, str):
            self._end_date = value

    @property
    def frequency(self):
        return self._frequency
    @frequency.setter
    def frequency(self, value):
        if isinstance(value, str):
            self._frequency = value

    @property
    def data_proxy(self):
        return self._data_proxy
    
    @data_proxy.setter
    def data_proxy(self, value):
        if isinstance(value, DataProxy):
            self._data_proxy = value

    @property
    def account(self):
        return self._account

    @account.setter
    def account(self, value):
        if isinstance(value, Account):
            self._account = value

    @property
    def event_source(self):
        return self._event_source
    
    @event_source.setter
    def event_source(self, value):
        if isinstance(value, EventSource):
            self._event_source = value

    @property
    def event_bus(self):
        return self._event_bus

    @event_bus.setter
    def event_bus(self, value):
        if isinstance(value, EventBus):
            self._event_bus = value
    
    def register(self):
        self.event_bus.add_listeners(EVENT.INIT_EVENT, self.scope['init'])
        self.event_bus.add_listeners(EVENT.NORMAL_TICKER_EVENT, self.scope['trade_logic']) 
        self.event_bus.add_listeners(EVENT.SETTLEMENT_EVENT, self.account.settlement)
        
    def run(self):
        bars = self.data_proxy.get_trading_bars(self.scope['assets'](),
                                                self.start_date,
                                                self.end_date)

        trading_date_bar = self.data_proxy.get_trading_dates(bars)
        self.register()
        for event in self.event_source.events(trading_date_bar, frequency=self.frequency):
            if event.event_type == EVENT.SETTLEMENT_EVENT:
                print(event.data['date'])
                self.event_bus.pop_listeners(event.event_type, bars)
            elif event.event_type == EVENT.NORMAL_TICKER_EVENT:
                print(event.data['date'])
                self.event_bus.pop_listeners(event.event_type)
        end = time.time()
        
