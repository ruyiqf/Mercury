import collections
from .data import Order
"""
Core functions of strategy are init and trade_logic
"""
def assets():
    return ['IF1703']

def init(context):
    """First need talib caculate index which whole strategies needed
       Calculate necessary indicators such as atr, sma
    """
    context.art = collections.defaultdict(dict)
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
    atr = context.atr[instrument].ix[quotation.date].atr[0]

    sma0 = context.sma[instrument].ix[quotation.data].sma0[0]
    sma1 = context.sma[instrument].ix[quotation.data].sma1[1]
    sma2 = context.sma[instrument].ix[quotation.data].sma2[2]

    if lastprice < posi_long.avg_cost - 2 * atr:
        order = Order()
        order.price = quotation.lastprice
        order.volume = posi_long.total_quantity
        order.direction = 'short'
        order.offset = 'close'
        order.instrument = instrument
        context.trader.order_booking(strategy_name, order, account, quotation = quotation)
    elif lastprice > posi_short.avg_cost + 2 * atr:
        order = Order()
        order.price = quotation.lastprice
        order.volume = posi_short.total_quantity
        order.direction = 'long'
        order.offset = 'close'
        order.instrument = instrument
        context.trader.order_booking(strategy_name, order, account, quotation = quotation)
    
    # Breaking system
    if quotation.lastprice > sma2:
        volume = (int)(account.available * 0.001 / (atr*10))
        order = Order()
        order.instrument = instrument
        order.price = quotation.lastprice
        order.direction = 'long'
        order.offset = 'open'
        order.volume = volume
        context.trader.order_booking(strategy_name, order, account, quotation = quotation)
    elif quotaton.lastprice < sma0:
        volume = (int)(account.available * 0.001 / (atr*10))
        order = Order()
        order.instrument = instrument
        order.price = quotation.lastprice
        order.direction = 'short'
        order.offset = 'open'
        order.volume = volume
        context.trader.order_booking(strategy_name, order, account, quotation = quotation)

