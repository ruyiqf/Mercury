#coding:utf-8
#
# Copyright 2017 Oak Tech, OT
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import click
import datetime
import tempfile
import tarfile
import requests
import shutil
import time
import traceback
import collections
import pandas as pd
import bcolz

from .context import Context
from .data import DataProxy, Account
from .loader import FileStrategyLoader
from .event import EventSource, EventBus
from .apis import RiskCal, Quotation, Trader
from .collector import CreateBasicInstruments

from threading import Thread
from queue import Queue

class CommodityFuture(object):

    def __init__(self):
        self.results_q = Queue() # Asynchronous receiving results from strategy context
        self.results_dir = None

    def recv_results(self):
        """Asynchronize receiving results from strategies"""
        while True:
            try:
                strategy_name, result_list = self.results_q.get()
                rc = RiskCal(result_list)
                rc.calculate()
                output_file = os.path.join(self.results_dir, strategy_name+'_result.pk')
                rc.ret_df.to_pickle(output_file)
                rc.draw('test')
            except Exception as e:
                traceback.print_exc()
                print('encounter errors will return')
       
    def firm_bargain(self, config):
        """Uset strategy real trading with system
        """
        allfiles = os.listdir(os.path.abspath(config.strategy_dir))
        fsl = FileStrategyLoader()
        data_proxy = DataProxy(os.path.abspath(config.data_bundle_path))
        for elt in allfiles:
            source = fsl.load(os.path.join(os.path.abspath(config.strategy_dir),elt),{})
            context = Context()
            context.scope = source
            context.data_proxy = data_proxy
            context.account = Account(initcash=config.initial_cash, start_date=config.start_date, end_date=config.end_date)
            context.event_source = EventSource()
            context.event_bus = EventBus()
            context.start_date = config.start_date
            context.end_date = config.end_date
            context.frequency = config.frequency
            context.trade_mode = 'real'
            context.quotation = Quotation()
            context.trader = Trader(context.trade_mode)
            print('recv data before')
            context.strategy_name = elt.split('.')[0]
            handle_ctx = Thread(target=context.firm_bargain)
            handle_ctx.setDaemon(True)
            handle_ctx.start()
            
        while True:
           time.sleep(1)

    def run(self, config):
        """Run strategy main function
        """
        allfiles = os.listdir(os.path.abspath(config.strategy_dir))
        fsl = FileStrategyLoader()
        data_proxy = DataProxy(os.path.abspath(config.data_bundle_path))
        self.results_dir = os.path.abspath(config.results_path)

        for elt in allfiles:
            source = fsl.load(os.path.join(os.path.abspath(config.strategy_dir), elt), {})
            #For every strategy code assign context
            context = Context()
            print(source['assets']())
            context.scope = source
            context.data_proxy = data_proxy
            context.account = Account(initcash=config.initial_cash, start_date=config.start_date, end_date=config.end_date)
            context.event_source = EventSource()
            context.event_bus = EventBus()
            context.start_date = config.start_date
            context.end_date = config.end_date
            context.frequency = config.frequency
            context.results_q = self.results_q
            context.quotation = Quotation()
            context.trader = Trader(context.trade_mode)
            context.strategy_name = elt.split('.')[0]
            handle_ctx = Thread(target=context.run)
            handle_ctx.setDaemon(True)
            handle_ctx.start()

        self.recv_results()

    def _check_timestamp(self, lasttime_ts):
        """According to downloading last timestamp calculate lacked daily list
        :lasttime_ts: lastest timestamp
        """
        ret = list()
        day = datetime.date.today()
        index = lasttime_ts + datetime.timedelta(days=1)
        while index <= day:
            ret.append(index)
            index = index + datetime.timedelta(days=1)
        return ret
         
    def _convert_bcolz2dfmap(self, bcolzfile, dfmap):
        """Convert bcolz file to dataframe map
        :bcolzfile: Raw bcolz file
        :dfmap: default dataframe dict
        """
        try:
            table = bcolz.open(bcolzfile)
            index = table.attrs['line_map']
            for elt in index:
                s,e = index[elt]
                dfmap[elt] = pd.DataFrame(table[s:e])
        except Exception as e:
            traceback.print_exc()
        
    def update_bundle(self, data_bundle_path=None, confirm=True):
        default_bundle_path = os.path.abspath(os.path.expanduser('~/.mercury/bundle/'))
        if data_bundle_path is None:
            data_bundle_path = default_bundle_path
        else:
            data_bundle_path = os.path.abspath(os.path.join(data_bundle_path, './bundle'))

        if (confirm and os.path.exists(data_bundle_path) and data_bundle_path != default_bundle_path and
                os.listdir(data_bundle_path)):
            click.confirm("""
[WARNING]
Target bundle path {data_bundle_path} is not empty.
The content of this folder will be REMOVED before updating.
Are you sure to continue?""".format(data_bundle_path=data_bundle_path), abort=True)
        else:
            click.echo("Will download data in this {}".format(data_bundle_path))
        
        day = datetime.date.today()
        
        #Record previous dataframe map aimed to increase daily download data
        old_table = collections.defaultdict(pd.DataFrame)
        
        if os.path.exists(os.path.join(default_bundle_path, 'downloadtime')):
            with open(os.path.join(default_bundle_path, 'downloadtime')) as f:
                last_time_stamp = datetime.datetime.strptime(f.readlines()[0].strip(), '%Y-%m-%d')
            lack_time_list = self._check_timestamp(datetime.date(last_time_stamp.year,
                                                                 last_time_stamp.month,
                                                                 last_time_stamp.day))

            self._convert_bcolz2dfmap(os.path.join(data_bundle_path, 'futures.bcolz'), old_table)
        else:
            #Downloadtime file not exist will compensate all time stamp from 2017-04-04 to now
            lack_time_list = list()
            start_day = datetime.date(2017,4,4)
            lack_time_list.append(start_day)
            while start_day <= datetime.date.today():
                start_day = start_day + datetime.timedelta(days=1)
                lack_time_list.append(start_day)
                
        if len(lack_time_list) == 0:
            click.echo('Already updated all, it is newest data')
            return


        for ts in lack_time_list:
            url = 'http://www.ruyiqf.com:8083/bundles_v2/mercury_%04d%02d%02d.tar.bz2' % (ts.year, ts.month, ts.day)
            click.echo(url)
            r = requests.get(url, stream=True)
            if r.status_code != 200:
                continue
            tmp = os.path.join(tempfile.gettempdir(), 'mercury.bundle')
            out = open(tmp, 'wb')
            total_length = int(r.headers.get('content-length'))
            with click.progressbar(length=total_length, label=('downloading ...')) as bar:
                for data in r.iter_content(chunk_size=8192):
                    bar.update(len(data))
                    out.write(data)
            tar = tarfile.open(tmp, 'r:bz2')
            tmpdata = os.path.join('.', 'tmpdata') 
            os.makedirs(tmpdata)
            tar.extractall(tmpdata)
            tmpdfmap = collections.defaultdict(pd.DataFrame)
            self._convert_bcolz2dfmap(os.path.join(tmpdata, 'futures.bcolz'), tmpdfmap)
            #Merge two dataframe map 
            for elt in tmpdfmap:
                if elt in old_table:
                    old_table[elt] = pd.concat([old_table[elt],tmpdfmap[elt]],
                                               ignore_index=True)
                else:
                    old_table[elt] = tmpdfmap[elt]
            out.close()
            tar.close()
            shutil.rmtree(tmpdata)
            os.remove(tmp)
            
        if os.path.exists(data_bundle_path):
            shutil.rmtree(data_bundle_path)
            os.makedirs(data_bundle_path)
        else:
            os.makedirs(data_bundle_path)
        
        cbi = CreateBasicInstruments()
        cbi.generate_bcolzdata(old_table, os.path.join(data_bundle_path, ''))

        #Update timestamp
        with open(os.path.join(data_bundle_path, 'downloadtime'), 'w') as f:
            f.write(datetime.datetime.now().strftime('%Y-%m-%d'))
        os.remove(os.path.join('.', 'tmp.csv'))
