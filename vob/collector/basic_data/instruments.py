#coding:utf-8

import os
import pickle
import json
import tarfile
import tempfile
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
        self.whole_wind_df = collections.defaultdict(pd.DataFrame)
        self.whole_wind_q_df = collections.defaultdict(pd.DataFrame)

    def parse_daily_ticker(self, path):
        """Parse data from daily server record data
        :path: Daily ticker data path include filename
        """
        with open(path, 'r') as f:
            line = f.readline()
            while line:
                line = line.strip()
                tmpret = self.convert_list_2_dict(line.split(','))
                self.assemble_whole_dataframe(tmpret)
                line = f.readline()

        for elt in self.whole_q_dict:
            df = pd.DataFrame(self.whole_q_dict[elt])
            self.whole_q_df [elt] = df
        
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
        
    def infusion_wind_daily_once(self, path, csvpath, outpath):
        """Merge wind daily ticker once time
        :path: Daily ticker data path
        :csvpath: Wind data csv path
        :outpath: Compress data path
        """
        self.parse_daily_ticker(path)
        self.accumulate_wind_ticker(csvpath)
        for elt in self.whole_wind_df:
            if elt in self.whole_q_df:
                self.whole_wind_q_df[elt] = pd.concat([self.whole_wind_df[elt],
                                                       self.whole_q_df[elt]],
                                                       ignore_index=True)
                                                      
            else:
                self.whole_wind_q_df[elt] = self.whole_wind_df[elt]
        
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
        :path: Daily ticker data path
        "bz2filepath: Previous day data path
        """
        dnow = (datetime.datetime.now()-datetime.timedelta(days=1)).strftime('%Y-%d-%m')
        if os.path.exists(path+'.'+dnow):
            self.parse_daily_ticker(path+'.'+dnow)
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
                self._generate_bcolzdata(old_table, os.path.join(os.path.abspath('.'), 'data'))

            except Exception as e:
                print('Can not find futures.bcolz fine')
                
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
            instrument_pos[elt].append(df.index[0]+cursor)
            instrument_pos[elt].append(df.index[-1]+1+cursor)
            cursor += len(df.index)
            df_list.append(df)

        all_instruments = pd.concat(df_list, ignore_index=True)
        ct = bcolz.ctable.fromdataframe(all_instruments)
        ct.copy(rootdir=outpath+'futures.bcolz')
        attr_futures = bcolz.attrs.attrs(path+'futures.bcolz', 'wb')
        attr_futures['line_map'] = instrument_pos
        self._generate_instrument_pk(whole_dict, outpath)

    def accumulate_wind_ticker(self, csvpath):
        """Clean data from wind
        :csvpath: csv file directory path
        """
        allfiles = os.listdir(csvpath)
        for elt in allfiles:
            tmplist = elt.split('.')
            contract = tmplist[0]
            df = pd.read_csv(os.path.join('%s%s'%(csvpath, elt)))
            df = df.dropna()
            df = df.reset_index()
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
            self.whole_wind_df[elt] = df
        
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

