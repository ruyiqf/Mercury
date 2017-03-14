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

class CommodityFuture(object):

    def __init__(self):
        pass

    def run(self, config):
        """Run strategy main function
        """
         
        print(config.data_bundle_path)
        print(config.strategy_dir)
        print(config.start_date)
        print(config.end_date)
        print(config.initial_cash)
        print(config.frequency)
        

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
