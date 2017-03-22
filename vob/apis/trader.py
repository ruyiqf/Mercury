#coding:utf-8
from ..data import Order

class Trader(object):
    def __init__(self):
        pass
    
    def order_booking(self, strategy_name, order, account, quotation=None, trade_mod='mock'):
        """Simulate order booking, but have reservation for real trade flag trade_mod ['mock', 'real']
        :strategy_name: seperate strategy when ordering
        :order: order class data
        :account: corresponding strategy
        :quotation: only meaningful under mock
        :trade_mode: revervation of switching between mock-trading and real-trading
        """
        if trade_mod == 'mock':
            if self._validate_order(order, account, quotation):
                portfolio.process_order(order)
        elif trade_mod == 'real':
            print('Need connect trading system later')
        
    def _validate_order(self, order, account, quotation):
        """Check whether order is validate
        :order: untraded order
        :account: include capital information
        :quotation: bar data
        """
        if quotation.volume < order.volume:
            print('Limit volume bardata volume:%d, untraded volume:%d' % 
                  (quotation.volume, order.volume))
            return False

        # Calculate this order's margin
        posid = order.instrument+'-'+order.direction
        if order.offset == 'open': 
            margin_ratio = account.portfolios[strategy_name].positions[posid].marge_ratio
            multiplier = account.portfolios[strategy_name].positions[posid].multiplier
            margin = order.price * order.volume * margin_ratio * multiplier
            if margin < account.available:
                print('Lack of capital available:%f, margin:%f' % (account.availalbe, margin))
                return False
        elif order.offset == 'close':
            hold_posi_quantity = account.portfolios[strategy_name].positions[posid].total_quantity
            if order.volume > hold_posi_quantity:
                print('Hold position quantity are not enough hold:%d, order volume:%d' % (hold_posi_quantity, order.volume))
                return False
        elif order.offset == 'closetoday':
            td_hold_posi_quantity = account.portfolios[strategy_name].positions[posid].today_position
            if order.volume > td_hold_posi_quantity:
                print('Today positions are not enough today:%d, order volume:%d' % (td_hold_posi_quantity, order.volume))
                return False
        else:
            return True
            
