#coding:utf-8
import datetime
from .event import Event, EVENT

class EventSource(object):
    def __init__(self):
        pass

    def events(self, datebar, frequency=None):
        """Generate trading events by datebar and will cut off according to frequency
        datebar: pd.DatetimeIndex data
        frequency: ['1m', '1d', '1t', '5m', '10m',...] designed for any interval cutting off date series
        """
        if frequency == '1t':
            # Means one ticker, this will use raw sequency of date bar
            yield Event(EVENT.INIT_EVENT)
            tickerlist = list(datebar)
            for ticker in tickerlist:
                yield Event(EVENT.NORMAL_TICKER_EVENT)
                #Judge this ticker whether generate settlement event
                xi = tickerlist.index(ticker)
                if xi+1 == len(tickerlist):
                    yield Event(EVENT.SETTLEMENT_EVENT)
                else:
                    ticker_next = tickerlist[xi+1]
                    if (ticker_next.to_datetime() - ticker.to_datetime()) > datetime.timedelta(hours=8):
                        yield Event(EVENT.SETTLEMENT_EVENT)
        else:
            print('Till now not yet support')
             
       
