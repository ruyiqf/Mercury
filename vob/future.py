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

from .context import Context
from .data import DataProxy, Account
from .loader import FileStrategyLoader
from .event import EventSource, EventBus
from .apis import RiskCal, Quotation, Trader

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
        tmp = os.path.join(tempfile.gettempdir(), 'mercury.bundle')

        while True:
            url = 'http://www.ruyiqf.com:8083/bundles_v2/mercury_%04d%02d%02d.tar.bz2' % (day.year, day.month, day.day)
            click.echo(url)
            r = requests.get(url, stream=True)
            if r.status_code != 200:
                day = day - datetime.timedelta(days=1)
                continue

            out = open(tmp, 'wb')
            total_length = int(r.headers.get('content-length'))

            with click.progressbar(length=total_length, label=('downloading ...')) as bar:
                for data in r.iter_content(chunk_size=8192):
                    bar.update(len(data))
                    out.write(data)
            out.close()
            break

        shutil.rmtree(data_bundle_path, ignore_errors=True)
        os.makedirs(data_bundle_path)
        tar = tarfile.open(tmp, 'r:bz2')
        tar.extractall(data_bundle_path)
        tar.close()
        os.remove(tmp)
