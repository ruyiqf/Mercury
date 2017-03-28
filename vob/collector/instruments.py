#coding:utf-8

import os
import pickle
import json
import tarfile
import tempfile
import shutil
import pandas as pd
import collections
import bcolz
import numpy as np

from pandas import DataFrame, Series

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

        self.whole_q_df = None
        self.whole_wind_dict = collections.defaultdict(DataFrame)
        self.whole_wind_q_df = collections.defaultdict(DataFrame)

    def _filter_raw_data(self, path, outpath):
        """Filter rawdata remove overflow data
        :path: rawdata path
        :outpath: output new data path
        """
        ret = list()
        with open(path, 'r') as f:
            line = f.readline()
            while line:
                tmplist = line.strip().split(',')
                newlist = ['0' if len(x)>20 else x for x in tmplist]
                ret.append(','.join(newlist))
                line = f.readline()
        with open(outpath, 'w') as f:
            for x in ret:
                f.write(x+'\n')
        
    def parse_daily_ticker(self, path):
        """Parse data from daily server record data
        :path: Daily ticker data path include filename
        """
        reader = pd.read_csv(path, names=['symbol','open','exchange','lastprice','high',
                                          'preclose','low','volume','bid','ask','date',
                                          'time','openinterest','uppderlimit','lowderlimit',
                                          'bidvolume','askvolume'],
                                   dtype={'symbol':object, 'open':np.float64, 'exchange':object,
                                          'lastprice':np.float64, 'high':np.float64, 'preclose':np.float64, 'low':np.float64, 'volume':np.int32,
                                          'bid':np.float64, 'ask':np.float64, 'date':object, 'time':object, 'openinterest':np.int32,
                                          'uppderlimit':np.float64, 'lowderlimit':np.float64, 'bidvolume':np.int32, 'askvolume':np.int32},iterator=True)
        chunksize = 100000
        chunks = []
        while True:
            try:
                chunk = reader.get_chunk(1000000)
                chunks.append(chunk)
            except StopIteration:
                print('Iteration is stopped')
                break

        self.whole_q_df = pd.concat(chunks, ignore_index=True)
        self.whole_q_df = self.whole_q_df.sort_values(by='symbol', kind='mergesort')
        self.whole_q_df = self.whole_q_df.reset_index()
        d = self._convert_time_format(self.whole_q_df['date'])
        self.whole_q_df['date'] = d + ' ' + self.whole_q_df['time']
        self.whole_q_df = self.whole_q_df.drop(['time'], axis=1)
        self.whole_q_df['amt'] = None
        self.whole_q_df['chg'] = None
        self.whole_q_df['pct_chg'] = None
        self.whole_q_df['oi'] = self.whole_q_df['openinterest']
        self.whole_q_df = self.whole_q_df.drop(['openinterest'], axis=1)
        self.whole_q_df['close'] = self.whole_q_df['preclose']
        self.whole_q_df = self.whole_q_df.drop(['preclose'], axis=1)
        
    def _convert_time_format(self, s):
        return Series(['{}-{}-{}'.format(x[0:4],x[4:6],x[6:]) for x in s.values])

    def infusion_wind_daily_once(self, path, csvpath, outpath):
        """Merge wind daily ticker once time
        :path: Daily ticker data path
        :csvpath: Wind data csv path
        :outpath: Compress data path
        """
        self.parse_daily_ticker(path)
        self.accumulate_wind_ticker(csvpath)
        daily_ticker = dict(list(self.whole_q_df.groupby('symbol')))
        keys1 = self.whole_wind_dict.keys()
        keys2 = daily_ticker.keys()
        keys1.extend(keys2)
        all_key = set(keys1)
        for elt in all_key:
            if (elt in self.whole_wind_dict) and (elt in daily_ticker):
                self.whole_wind_q_df[elt] = pd.concat([self.whole_wind_dict[elt],daily_ticker[elt]],
                                                      ignore_index=True)
            elif elt in self.whole_wind_dict:
                self.whole_wind_q_df[elt] = self.whole_wind_dict[elt]
            else:
                self.whole_wind_q_df[elt] = daily_ticker[elt]
        self._generate_bcolzdata(self.whole_wind_q_df, outpath)

    def _generate_instrument_pk(self, whole_df, outpath):
        """According to whole df, generate pickle data for instruments
        :whole_df: dict include instrument symbol and df data
        :outpath: output data path
        """
        final_instrupk = collections.defaultdict(dict)
        for elt in whole_df:
            ctid = elt[0:-4] if elt[-4].isdigit() else elt[0:-3]
            final_instrupk[elt] = self.ctidmap[ctid]
            final_instrupk[elt]['order_book_id'] = elt
            final_instrupk[elt]['de_listed_date'] = list(whole_df[elt].date)[0]
            final_instrupk[elt]['listed_date'] = list(whole_df[elt].date)[-1]

        output = open(outpath+'instruments.pk', 'wb')
        pickle.dump(final_instrupk, output, -1)

    def infusion_increasing(self, path, bz2filepath):
        """Merge daily ticker data with previous day
        :path: Daily ticker data file path 
        "bz2filepath: Previous day data path
        """
        if os.path.exists(path):
            self.parse_daily_ticker(path)
            tar = tarfile.open(bz2filepath, 'r:bz2')
            tar.extractall()
            tar.close()
            try:
                table = bcolz.open('futures.bcolz', 'r')
                index = table.attrs['line_map']
                old_table = collections.defaultdict(pd.DataFrame)
                for elt in index:
                    s,e = index[elt]
                    old_table[elt] = pd.DataFram(table[s:e])
                #Merge new dict
                for elt in self.whole_q_df:
                    if elt in old_table:
                        old_table[elt] = pd.concat(old_table[elt],
                                                   self.whole_q_df[elt],
                                                   ignore_index=True)
                outpath = os.path.join(os.path.abspath('.'), 'data')
                if os.path.exists(outpath):
                    shutil.rmtree(outpath)
                    os.makedirs(outpath)
                else:
                    os.makedirs(outpath)
                self._generate_bcolzdata(old_table, outpath)
            except Exception as e:
                print('Can not find futures.bcolz fine')
            finally:
                os.remove('instruments.pk')
                os.remove('futures.bcolz')
        else:
            print('Data file not exists')
            return 
        
    def _generate_bcolzdata(self, whole_dict, outpath):
        """Generate bcolzdata and instrument pickle file
        :whole_dict: raw data
        :outpath: output data path
        """
        all_instruments = pd.DataFrame()
        instrument_pos = collections.defaultdict(list)

        df_list = list()
        cursor = 0
        for elt in whole_dict:
            df = whole_dict[elt]
            df = df.drop('index',axis=1)
            df = df.reset_index()
            df = df.drop('index',axis=1)
            instrument_pos[elt].append(df.index[0]+cursor)
            instrument_pos[elt].append(df.index[-1]+1+cursor)
            cursor += len(df.index)
            df_list.append(df)

        ret = list()
        columns = ['date','symbol','open','exchange','lastprice','high','low','volume',
                   'bid','ask','uppderlimit','lowderlimit','bidvolume',
                   'askvolume','amt','chg','pct_chg','oi','close']
        
        for elt in df_list:
            elt.to_csv('tmp.csv', index=False, mode='a', header=False, columns=columns)
        
        try:
            reader = pd.read_csv('tmp.csv', names=columns,
                                 dtype={'date':object, 'symbol':object, 'open':np.float64,'exchange':object,
                                        'lastprice':np.float64, 'high':np.float64, 'low':np.float64, 'volume':np.float64,
                                        'bid':np.float64, 'ask':np.float64, 'uppderlimit':np.float64, 'lowderlimit':np.float64, 'bidvolume':np.float64, 'askvolume':np.float64,
                                        'amt':np.float64, 'chg':np.float64,'pct_chg':np.float64, 'oi':np.float64, 'close':np.float64},iterator=True)
        except ValueError:
            print('ValueError when read tmpcsv')
            os.remove('tmp.csv')

        chunksize = 100000
        chunks = []
        while True:
            try:
                chunk = reader.get_chunk(1000000)
                chunks.append(chunk)
            except StopIteration:
                print('Iteration is stopped')
                break

        all_instruments = pd.concat(chunks, ignore_index=True)
        ct = bcolz.ctable.fromdataframe(all_instruments)
        ct.copy(rootdir=outpath+'futures.bcolz')
        attr_futures = bcolz.attrs.attrs(outpath+'futures.bcolz', 'wb')
        attr_futures['line_map'] = instrument_pos
        self._generate_instrument_pk(whole_dict, outpath)
        os.remove('tmp.csv')

    def accumulate_wind_ticker(self, csvpath):
        """Clean data from wind
        :csvpath: csv file directory path
        """
        allfiles = os.listdir(csvpath)
        allinstruments = list()
        for elt in allfiles:
            tmplist = elt.split('.')
            contract = tmplist[0]
            df = pd.read_csv(os.path.join('%s%s'%(csvpath, elt)))
            df = df.dropna()
            df = df.reset_index()
            ctid = contract[0:-4] if contract[-4].isdigit() else contract[0:-3]
            df['exchange'] = self.ctidmap[ctid]['exchange']
            df['symbol'] = contract
            df['lastprice'] = df['close']
            df['bid'] = None
            df['ask'] = None
            df['uppderlimit'] = None
            df['lowderlimit'] = None
            df['bidvolume'] = None
            df['askvolume'] = None
            self.whole_wind_dict[contract] = df
        
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

