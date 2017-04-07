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

import click
import os

from vob import CommodityFuture
from vob import Config

@click.group()
@click.option('-v', '--verbose', count=True)
@click.pass_context
def cli(ctx, verbose):
    ctx.obj["VERBOSE"] = verbose

def entry_point():
    cli(obj={})

@cli.command()
@click.option('-d', '--data-bundle-path', default=os.path.expanduser("~/.mercury"), type=click.Path(file_okay=False))
def update_bundle(data_bundle_path):
    """
    Sync Data Bundle of commodity future data specially
    """
    click.echo('will start from here')
    cf = CommodityFuture()
    cf.update_bundle(data_bundle_path=data_bundle_path)

@cli.command()
@click.help_option('-h', '--help')
@click.option('-d', '--data-bundle-path', type=click.Path(exists=True))
@click.option('--progress/--no-progress', default=None, help="show progress bar")
@click.option('-f', '--strategy-dir', type=click.Path(exists=True))
@click.option('-s', '--start-date', type=click.STRING)
@click.option('-e', '--end-date', type=click.STRING)
@click.option('-ic', '--initial-cash', type=click.FLOAT)
@click.option('-fq', '--frequency', default=None, type=click.STRING)
@click.option('-o', '--results-path', type=click.Path(exists=True))
def run(**kwargs):
    """
    Start to run a strategy
    """
    cf = CommodityFuture()
    conf = Config(kwargs)
    cf.run(conf)

@cli.command()
@click.help_option('-h', '--help')
@click.option('-d', '--data-bundle-path', type=click.Path(exists=True))
@click.option('-f', '--strategy-dir', type=click.Path(exists=True))
@click.option('-s', '--start-date', type=click.STRING)
@click.option('-e', '--end-date', type=click.STRING)
@click.option('-ic', '--initial-cash', type=click.FLOAT)
@click.option('-fq', '--frequency', default=None, type=click.STRING)
def firm_bargain(**kwargs):
    """
    Actually use stratregy trading with system
    """
    cf = CommodityFuture()
    conf = Config(kwargs)
    cf.firm_bargain(conf)

if __name__ == '__main__':
    entry_point()
