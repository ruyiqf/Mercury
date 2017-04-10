#coding:utf-8
import datetime
import time
import pandas as pd
import numpy as np
from queue import Queue
from .data import DataProxy, Account, BarData
from .event import EventSource, EventBus, EVENT, Event
from .apis import Trader, Quotation 
from .exception import SearchError
from .receiver import ReceiverQuotation 
from .protocol import TickData

class Context(object):
    """Need say something Wow, will replace environment object"""
    LONG_DATA_LEN = 12
    def __init__(self):
        self._data_proxy = None
        self._event_source = None
        self._account = None
        self._event_bus = None
        self._scope = None # Strategy execution scope
        self._frequency = None
        self._start_date = None
        self._end_date = None
        self._trader = None # Mock and real trader handler
        self._quotation = None # Transmit quotation
        self._strategy_name = None # Corresponding portfolio, a strategy has only one context
        self._bars = None # Dict {instrument:df}
        self._results_q = None # When initializing, will setting queue
        self._ret_list = list()
        self._trade_mode = 'mock' # Trade mode will be transferred to order booking
    
    def __setter__(self, name, value):
        """Connect strategy functions, here not check validation of values"""
        self.__dict__[name] = value
    
    @property
    def trade_mode(self):
        return self._trade_mode
    @trade_mode.setter
    def trade_mode(self, value):
        if isinstance(value, str):
            self._trade_mode = value

    @property
    def results_q(self):
        return self._results_q
    @results_q.setter
    def results_q(self, value):
        if isinstance(value, Queue):
            self._results_q = value
        
    @property
    def bars(self):
        return self._bars

    @property
    def strategy_name(self):
        return self._strategy_name
    @strategy_name.setter
    def strategy_name(self, value):
        if isinstance(value, str):
            self._strategy_name = value

    @property
    def trader(self):
        return self._trader
    @trader.setter
    def trader(self, value):
        if isinstance(value, Trader):
            self._trader = value

    @property
    def quotation(self):
        return self._quotation
    @quotation.setter
    def quotation(self, value):
        if isinstance(value, Quotation):
            self._quotation = value

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
        
    def _search_by_date_from_bars(self, date, instrument, bars):
        df = bars[instrument]
        if len(df[df.date == date]) > 0:
            return df[df.date == date]
        raise SearchError()

    def _is_price_reasonable(self, price):
        """Filter abnormal price when receiving quotation"""
        return (0 if len(str(price)) > Context.LONG_DATA_LEN else price)

    def firm_bargain(self):
        """Using for real trade with trading system"""
        bars = self.data_proxy.get_all_trading_bars(self.start_date, self.end_date)
        print('after getting bars')
        rq = ReceiverQuotation()
        socket = rq.socket
        mdaddr = rq.mdaddress
        socket.connect(mdaddr)
        self.register()

        self.event_bus.pop_listeners(EVENT.INIT_EVENT, self)
        while True:
            ticker = socket.recv()
            data = TickData()
            data.ParseFromString(ticker)
            bar = bars[data.symbol]
            if bar.columns.size == 0:
                bar = pd.DataFrame(columns=['symbol','open','exchange','lastprice','high',
                               'close','low','volume','bid','ask','date',
                               'time','oi','uppderlimit','lowderlimit',
                               'bidvolume','askvolume','chg','pct_chg'])
            bar.loc[bar.index.size] = [None for x in bar.columns]
            bar.loc[bar.index.size-1,'symbol'] = data.symbol
            bar.loc[bar.index.size-1,'open'] = self._is_price_reasonable(data.openPrice)
            bar.loc[bar.index.size-1,'exchange'] = data.exchange
            bar.loc[bar.index.size-1,'lastprice'] = self._is_price_reasonable(data.lastPrice)
            bar.loc[bar.index.size-1,'high'] = self._is_price_reasonable(data.highPrice)
            bar.loc[bar.index.size-1,'close'] = self._is_price_reasonable(data.preClosePrice)
            bar.loc[bar.index.size-1,'low'] = self._is_price_reasonable(data.lowPrice)
            bar.loc[bar.index.size-1,'volume'] = data.volume
            bar.loc[bar.index.size-1,'bid'] = self._is_price_reasonable(data.bidPrice1)
            bar.loc[bar.index.size-1,'ask'] = self._is_price_reasonable(data.askPrice1)
            bar.loc[bar.index.size-1,'date'] = np.datetime64(datetime.datetime.now())
            bar.loc[bar.index.size-1,'uppderlimit'] = self._is_price_reasonable(data.upperLimit)
            bar.loc[bar.index.size-1,'lowderlimit'] = self._is_price_reasonable(data.lowerLimit)
            bar.loc[bar.index.size-1,'bidvolume'] = data.bidVolume1
            bar.loc[bar.index.size-1,'askvolume'] = data.askVolume1
            bar.loc[bar.index.size-1,'oi'] = data.openInterest
            
            objects = self.scope['assets']()

            bardata = BarData()
            bardata.instrument = data.symbol
            bardata.bid = self._is_price_reasonable(data.bidPrice1)
            bardata.ask = self._is_price_reasonable(data.askPrice1)
            bardata.bidvolume = int(data.bidVolume1)
            bardata.askvolume = int(data.askVolume1)
            bardata.date = datetime.datetime.now()
            #bardata.margin_ratio = self.data_proxy.instruments[bardata.instrument].margin_rate
            #bardata.multiplier = self.data_proxy.instruments[bardata.instrument].contract_multiplier
            bardata.volume = int(data.volume)
            
            if data.symbol in objects:
                self.event_bus.pop_listeners(EVENT.NORMAL_TICKER_EVENT, self, bardata)
                
    
    def run(self):
        bars = self.data_proxy.get_trading_bars(self.scope['assets'](),
                                                self.start_date,
                                                self.end_date)
        self._bars = bars

        trading_date_bar = self.data_proxy.get_trading_dates(bars)
         
        self.register()
        for event in self.event_source.events(trading_date_bar, frequency=self.frequency):
            if event.event_type == EVENT.INIT_EVENT:
                self.event_bus.pop_listeners(event.event_type, self)
                continue
            try:
                data = self._search_by_date_from_bars(event.data['date'], event.data['value'], bars)
                bardata = BarData()
                bardata.instrument = data.symbol.values[0]
                bardata.lastprice = data.close.values[0]
                bardata.date = pd.to_datetime(data.date.values[0]).to_pydatetime()
                bardata.margin_ratio = self.data_proxy.instruments[bardata.instrument].margin_rate
                bardata.multiplier = self.data_proxy.instruments[bardata.instrument].contract_multiplier
                bardata.volume = int(data.volume.values[0])
            except SearchError as e:
                print(e)
            if event.event_type == EVENT.SETTLEMENT_EVENT:
                self.event_bus.pop_listeners(event.event_type, self._ret_list, bardata)
            elif event.event_type == EVENT.NORMAL_TICKER_EVENT:
                self.event_bus.pop_listeners(event.event_type, self, bardata)

        self._results_q.put((self._strategy_name, self._ret_list))
        end = time.time()
