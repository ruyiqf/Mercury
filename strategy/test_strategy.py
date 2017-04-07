import collections
import pandas as pd
from vob.data import Order

"""
Core functions of strategy are init and trade_logic
"""
def assets():
    return ['rb1705', 'ag1705']

def init(context):
    """First need talib caculate index which whole strategies needed
       Calculate necessary indicators such as atr, sma
    """
    context.atr = collections.defaultdict(dict)
    context.sma = collections.defaultdict(dict)
    for bar in context.bars:
        context.atr[bar] = context.quotation.history(context.bars[bar], 14*240, 'atr')
        context.sma[bar] = context.quotation.history(context.bars[bar], 20*240, 'sma')
    
def trade_logic(context, quotation):
    """Normal ticker data will trigger"""
    instrument = quotation.instrument
    account = context.account
    strategy_name = context.strategy_name
    portfolio = account.portfolios[strategy_name]
    lastprice = quotation.lastprice
    posi_long = portfolio.positions[instrument+'-'+'long']
    posi_short = portfolio.positions[instrument+'-'+'short']
    atr = context.atr[instrument].ix[quotation.date].atr

    sma0 = context.sma[instrument].ix[quotation.date].sma0
    sma1 = context.sma[instrument].ix[quotation.date].sma1
    sma2 = context.sma[instrument].ix[quotation.date].sma2
    
    #print('lastprice:%f,atr:%f,sma0:%f,sma2:%f'%(lastprice,atr,sma0,sma2))

    if lastprice < posi_long.avg_cost - 2 * atr:
        order = Order()
        order.price = quotation.lastprice
        order.volume = posi_long.total_position
        order.direction = 'short'
        order.offset = 'close'
        order.instrument = instrument
        #print('lastprice lower than atr close short order.volume:%d' % order.volume)
        context.trader.order_booking(strategy_name, order, account, quotation = quotation)
    elif lastprice > posi_short.avg_cost + 2 * atr:
        order = Order()
        order.price = quotation.lastprice
        order.volume = posi_short.total_position
        order.direction = 'long'
        order.offset = 'close'
        order.instrument = instrument
        context.trader.order_booking(strategy_name, order, account, quotation = quotation)
        #print('lastprice greater than atr close long order.volume:%d' % order.volume)
    
    # Breaking system
    if quotation.lastprice > sma2:
        #volume = (int)(account.available * 0.0001 / (atr*10))
        volume = 1
        order = Order()
        order.instrument = instrument
        order.price = quotation.lastprice
        order.direction = 'long'
        order.offset = 'open'
        order.volume = volume
        context.trader.order_booking(strategy_name, order, account, quotation = quotation)
    elif quotation.lastprice < sma0:
        #volume = (int)(account.available * 0.001 / (atr*10))
        volume = 1
        order = Order()
        order.instrument = instrument
        order.price = quotation.lastprice
        order.direction = 'short'
        order.offset = 'open'
        order.volume = volume
        context.trader.order_booking(strategy_name, order, account, quotation = quotation)

    # Update account and position information
    portfolio.process_normal_bar(quotation)

