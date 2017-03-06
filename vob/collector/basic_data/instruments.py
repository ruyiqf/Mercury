#coding:utf-8

import pickle
import json
import pandas as pd
import collections
import bcolz

INFINITE = 10e10
NEGINFINITE = -10e10

"""
Unitize data format together with wind and europa
[date:pd.DatetimeIndex, open, high, last, volume, amt, chg, pct_chg, oi, symbol, exchange, close,
 bid, ask, upperlimit, lowderlimit, bidvolume, askvolume]
"""
class Data(object):

    def __init__(self):
        self.product = 'Commodity'
        self.margin_rate = 0.0
        self.exchange = ''
        self.underlying_symbol = ''
        self.type = 'Future'
        self.order_book_id = ''
        self.maturity_date = ''
        self.contract_multiplier = 0.0
        self.de_listed_date = ''
        self.listed_date = ''
        self.round_lot = 1.0

class CreateBasicInstruments(object):

    def __init__(self):
        """Initialzie contract common data"""
        with open('contracts.json', 'r') as f:
            self.ctidmap = json.load(f)

        self.whole_q_df = collections.defaultdict(pd.DataFrame)
        self.whole_q_dict = collections.defaultdict(dict)

    def parse_daily_ticker(self):
        """Parse data from daily server record data"""
        #This will be added time stamp but now is only for testing
        with open('emercury_f_data', 'r') as f:
            line = f.readline()
            while line:
                line = line.strip()
                tmpret = self.convert_list_2_dict(line.split('|'))
                self.assemble_whole_dataframe(tmpret)
                line = f.readline()

        all_instruments = pd.DataFrame()
        instrument_pos = collections.defaultdict(list)

        for elt in self.whole_q_dict:
            df = pd.DataFrame(self.whole_q_dict[elt])
            instrument_pos[elt].append(df.index[0]+len(all_instruments.index))
            instrument_pos[elt].append(df.index[-1]+len(all_instruments.index))
            all_instruments = pd.concat([all_instruments, df], ignore_index=True)

        ct = bcolz.ctable.fromdataframe(all_instruments)
        ct.copy(rootdir='/Users/ruyiqf/mercury/Mercury/vob/collector/basic_data/futures.bcolz')

        attr_futures = bcolz.attrs.attrs('/Users/ruyiqf/mercury/Mercury/vob/collector/basic_data/futures.bcolz', 'wb')
        attr_futures['line_map'] = instrument_pos
        
    def convert_list_2_dict(self, datalist):
        """Convert list to dict which will be used in future
        :datalist: ['xxx:xxx', 'xxx:xxx',....]
        """
        ret = dict()
        for elt in datalist:
            elt_list = elt.split(':')
            ret[elt_list[0]] = elt_list[1]
        return ret
            
    
    def assemble_whole_dataframe(self, one_q_record):
        """Assemble partly result to seperated dataframe
        :one_q_record: dictory format
        """
        key = one_q_record['symbol']
        if key not in self.whole_q_dict:
            self.whole_q_dict[key] = dict(
                date=list(),
                open=list(),
                high=list(),
                last=list(),
                volume=list(),
                amt=list(),
                chg=list(),
                pct_chg=list(),
                oi=list(),
                symbol=list(),
                exchange=list(),
                close=list(),
                bid=list(),
                ask=list(),
                uppderlimit=list(),
                lowderlimit=list(),
                bidvolume=list(),
                askvolume=list()
            )
        self.whole_q_dict[key]['date'].append(one_q_record['date']+
            ' '+one_q_record['time'])
        self.whole_q_dict[key]['open'].append(self.check_data_reasonable(float(one_q_record['open'])))
        self.whole_q_dict[key]['high'].append(self.check_data_reasonable(float(one_q_record['high'])))
        self.whole_q_dict[key]['last'].append(self.check_data_reasonable(float(one_q_record['lastprice'])))
        self.whole_q_dict[key]['volume'].append(self.check_data_reasonable(int(one_q_record['volume'])))
        self.whole_q_dict[key]['amt'].append(None)
        self.whole_q_dict[key]['chg'].append(None)
        self.whole_q_dict[key]['pct_chg'].append(None)
        self.whole_q_dict[key]['oi'].append(self.check_data_reasonable(int(one_q_record['openinterest'])))
        self.whole_q_dict[key]['symbol'].append(key)
        ctid = key[0:-4] if key[-4].isdigit() else key[0:-3]
        self.whole_q_dict[key]['exchange'].append(self.ctidmap[ctid]['exchange'])
        self.whole_q_dict[key]['close'].append(self.check_data_reasonable(float(one_q_record['preclose'])))
        self.whole_q_dict[key]['bid'].append(self.check_data_reasonable(float(one_q_record['bid'])))
        self.whole_q_dict[key]['ask'].append(self.check_data_reasonable(float(one_q_record['ask'])))
        self.whole_q_dict[key]['uppderlimit'].append(self.check_data_reasonable(float(one_q_record['uppderlimit'])))
        self.whole_q_dict[key]['lowderlimit'].append(self.check_data_reasonable(float(one_q_record['lowderlimit'])))
        self.whole_q_dict[key]['bidvolume'].append(self.check_data_reasonable(float(one_q_record['bidvolume'])))
        self.whole_q_dict[key]['askvolume'].append(self.check_data_reasonable(float(one_q_record['askvolume'])))
        
    def check_data_reasonable(self, price):
        return price if (price < INFINITE and price > NEGINFINITE) else None
        
    def accumulate_wind_ticker(self):
        """Clean data from wind"""
        pass

"""
Testing code
"""
def main():
    cb = CreateBasicInstruments()
    #output = open('instruments.pk', 'wb')
    #pickle.dump(cb.ctidmap, output, -1)
    cb.parse_daily_ticker()

if __name__ == '__main__':
    main()



