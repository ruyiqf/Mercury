#coding:utf-8
#
# Copyright 2017  MingQian Tech, MT
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
import sys
import tarfile
import tempfile
import datetime
import requests
import shutil
import click
import six

from .context import Context
from .loader import FileStrategyLoader
from .data import DataProxy, Account
from .event import EventSource, EventBus

class CompanyStock(object):
    
    def __init__(self):
        pass

    def run(self, conf):
        print('call stock run here')

    def firm_bargain(self, conf):
        print('call stock firm bargain here')

    def update_bundle(self, data_bundle_path=None, confirm=True):
        default_bundle_path = os.path.abspath(os.path.expanduser('~/.mercury/bundle/stock'))
        if data_bundle_path is None:
            data_bundle_path = default_bundle_path
        else:
            data_bundle_path = os.path.abspath(os.path.join(data_bundle_path, './bundle/stock'))
       
        if (confirm and os.path.exists(data_bundle_path) and data_bundle_path != default_bundle_path and os.listdir(data_bundle_path)):
            click.confirm(("""
[WARNING]
Target bundle path {data_bundle_path} is not empty.
The content of this folder will be REMOVED before updating.
Are you sure to continue?""").format(data_bundle_path=data_bundle_path), abort=True)
       
        day = datetime.date.today()
        tmp = os.path.join(tempfile.gettempdir(), 'rq.bundle')
        while True:
            url = 'http://7xjci3.com1.z0.glb.clouddn.com/bundles_v2/rqbundle_%04d%02d%02d.tar.bz2' % (
                day.year, day.month, day.day)
            six.print_(('try {} ...').format(url))
            r = requests.get(url, stream=True)
            if r.status_code != 200:
                day = day - datetime.timedelta(days=1)
                continue
            out = open(tmp, 'wb')
            total_length = int(r.headers.get('content-length'))
            with click.progressbar(length=total_length, label='downloading...') as bar:
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
        six.print_(("Data bundle download successfully in {bundle_path}").format(bundle_path=data_bundle_path))

    def run(self, config):
        """Run Strategy main function
        """
        allfiles = os.listdir(os.path.abspath(config.strategy_dir))
        fsl = FileStrategyLoader()
        data_proxy = DataProxy(os.path.abspath(config.data_bundle_path), assets=config.asset) 
        for elt in allfiles:
            source = fsl.load(os.path.abspath(config.data_bundle_path))
            context = Context()
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
        
