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
            indexlist = list(datebar.index)
            for i in datebar.index:
                yield Event(EVENT.NORMAL_TICKER_EVENT, data={'date':datebar.ix[i].time, 
                                                             'value':datebar.ix[i].value})
                #Judge this ticker whether generate settlement event
                xi = indexlist.index(i)
                if xi+1 == len(indexlist):
                    yield Event(EVENT.SETTLEMENT_EVENT, data={'date':datebar.ix[i].time, 
                                                              'value':datebar.ix[i].value})
                else:
                    ticker = datebar.ix[xi].time
                    ticker_next = datebar.ix[xi+1].time
                    if (ticker_next.to_pydatetime() - ticker.to_pydatetime()) > datetime.timedelta(hours=8):
                        yield Event(EVENT.SETTLEMENT_EVENT, data={'date':datebar.ix[xi].time, 
                                                                  'value':datebar.ix[xi].value})
        else:
            print('Till now not yet support')
             
       
