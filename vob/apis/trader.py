#coding:utf-8

from .quant_client_sys_pb2 import ClientReqOrder, OrderList
from .sender_trade import SenderTrade

class Trader(object):
    def __init__(self, trade_mode):
        self._trade_mode = trade_mode
        if trade_mode == 'real':
            self.sender = SenderTrade() 

    def order_booking(self, strategy_name, order, account, quotation=None):
        """Simulate order booking, but have reservation for real trade flag trade_mode ['mock', 'real']
        :strategy_name: seperate strategy when ordering
        :order: order class data
        :account: corresponding strategy
        :quotation: only meaningful under mock
        :trade_mode: revervation of switching between mock-trading and real-trading
        """
        if self._trade_mode == 'mock':
            if self._validate_order(order, account, quotation, strategy_name):
                account.portfolios[strategy_name].process_order(order)

        elif self._trade_mode == 'real':
            orderlist = OrderList()
            content = orderlist.orders.add()
            content.instrument = order.instrument
            content.direction = 'dlong' if order.direction == 'long' else 'dshort'
            content.sinterval = order.sinterval
            content.volume = order.volume
            content.price = 'PRICEALGO_BID' if order.direction == 'long' else 'PRICEALGO_ASK'
            content.algotype = order.algotype 
            content.offset = order.offset
            content.strategyname = order.strategyname
            content.size = order.size
            content.wttime = order.wttime
            content.signalid = order.signalid
            content.pricetype = 'PRICETYPE_LIMITPRICE'
            content.orderstyle = order.orderstyle
            content.maxcancelnum = order.maxcancelnum
            content.clientid = order.clientid
            self.sender.send(orderlist.SerializeToString())
            
        
    def _validate_order(self, order, account, quotation, strategy_name):
        """Check whether order is validate
        :order: untraded order
        :account: include capital information
        :quotation: bar data
        """
        if quotation.volume < order.volume:
            print('Limit volume bardata volume:%d, untraded volume:%d, date:%s' % 
                  (quotation.volume, order.volume, quotation.date))
            return False

        # Calculate this order's margin
        if order.offset == 'open': 
            posid = order.instrument+'-'+order.direction
            margin_ratio = account.portfolios[strategy_name].positions[posid].margin_ratio = quotation.margin_ratio
            multiplier = account.portfolios[strategy_name].positions[posid].multiplier = quotation.multiplier
            margin = order.price * order.volume * margin_ratio * multiplier
            if margin > account.available:
                print('Lack of capital available:%f, margin:%f' % (account.available, margin))
                return False
            return True
        elif order.offset == 'close':
            if order.direction == 'long':
                posid = order.instrument+'-'+'short'
            elif order.direction == 'short':
                posid = order.instrument+'-'+'long'
            hold_posi_quantity = account.portfolios[strategy_name].positions[posid].total_position
            try:
                assert order.volume > 0, 'close volume need greater than zero %d'%(order.volume)
                assert order.volume <= hold_posi_quantity, 'close volume need lower than hold posi quantity %d:%d'%(order.volume,
                hold_posi_quantity)
            except AssertionError as e:
                #print(e)
                return False
            return True
        elif order.offset == 'closetoday':
            order.direction = 'long' if order.direction == 'short' else 'short'
            posid = order.instrument+'-'+order.direction
            td_hold_posi_quantity = account.portfolios[strategy_name].positions[posid].today_position
            try:
                assert order.volume < td_hold_posi_quantity, 'close today position need lower than today hold position'
            except AssertionError as e:
                print(e)
                return False
            return True
        else:
            return False
            
