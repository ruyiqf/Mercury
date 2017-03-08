#coding:utf-8

import os
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
class CreateBasicInstruments(object):

    def __init__(self):
        """Initialzie contract common data"""
        with open('contracts.json', 'r') as f:
            self.ctidmap = json.load(f)

        self.whole_q_df = collections.defaultdict(pd.DataFrame)
        self.whole_q_dict = collections.defaultdict(dict)

    def parse_daily_ticker(self, path):
        """Parse data from daily server record data
        :path: Daily data path
        """
        with open(path+'emercury_f_data.%s'%(datetime.datetim.now().strftime('%Y-%m-%d')), 'r') as f:
            line = f.readline()
            while line:
                line = line.strip()
                tmpret = self.convert_list_2_dict(line.split(','))
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
        ct.copy(rootdir=path+'futures.bcolz')

        attr_futures = bcolz.attrs.attrs(path+'futures.bcolz', 'wb')
        attr_futures['line_map'] = instrument_pos
        
    def convert_list_2_dict(self, datalist):
        """Convert list to dict which will be used in future
        :datalist: ['xxx', 'xxx',....]
        Fixed data format:
        symbol,open,exchange,lastprice,high,preclose,low,
        volume,bid,ask,date,time,openinterest,uppderlimit,lowderlimit,
        bidvolume,askvolume
        """
        ret = dict(
            symbol=datalist[0],
            open=datalist[1],
            exchange=datalist[2],
            lastprice=datalist[3],
            high=datalist[4],
            preclose=datalist[5],
            low=datalist[6],
            volume=datalist[7],
            bid=datalist[8],
            ask=datalist[9],
            date=datalist[10],
            time=datalist[11],
            openinterest=datalist[12],
            uppderlimit=datalist[13],
            lowderlimit=datalist[14],
            bidvolume=datalist[15],
            askvolume=datalist[16]
        )
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
        
    def accumulate_wind_ticker(self, csvpath, path):
        """Clean data from wind
        :csvpath: csv file directory path
        :path: output file path
        """
        allfiles = os.listdir(csvpath)
        whole_wind_df = collections.defaultdict(pd.DataFrame)
        for elt in allfiles:
            tmplist = elt.split('.')
            contract = tmplist[0]
            df = pd.read_csv(os.path.join('%s%s'%(csvpath, elt)))
            df = df.dropna()
            df = df.reset_index()
            print(df)
            ctid = contract[0:-4] if contract[-4].isdigit() else contract[0:-3]
            df['exchange'] = self.ctidmap[ctid]['exchange']
            df['symbol'] = contract
            df['last'] = None
            df['bid'] = None
            df['ask'] = None
            df['uppderlimit'] = None
            df['lowderlimit'] = None
            df['bidvolume'] = None
            df['askvolume'] = None
            whole_wind_df[elt] = df

        #Compress to bcolz file
        instrument_pos = collections.defaultdict(list)
        all_instruments = pd.DataFrame()
        for elt in whole_wind_df:
            df = whole_wind_df[elt]
            instrument_pos[elt].append(df.index[0]+len(all_instruments.index))
            instrument_pos[elt].append(df.index[-1]+len(all_instruments.index))
            all_instruments = pd.concat([all_instruments, df], ignore_index=True)

        ct = bcolz.ctable.fromdataframe(all_instruments)
        ct.copy(rootdir=path+'wdbasic.bcolz')

        attr_futures = bcolz.attrs.attrs(path+'wdbasic.bcolz', 'wb')
        attr_futures['line_map'] = instrument_pos
        
"""
Testing code
"""
def main():
    cb = CreateBasicInstruments()
    #output = open('instruments.pk', 'wb')
    #pickle.dump(cb.ctidmap, output, -1)
    #cb.parse_daily_ticker()
    cb.accumulate_wind_ticker('/Users/ruyiqf/winddata/csv/', '/Users/ruyiqf/winddata/')

if __name__ == '__main__':
    main()

