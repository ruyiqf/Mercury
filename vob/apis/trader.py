#coding:utf-8

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
            if self._validate_order(order, account, quotation, strategy_name):
                account.portfolios[strategy_name].process_order(order)
        elif trade_mod == 'real':
            print('Need connect trading system later')
        
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
            order.direction = 'long' if order.direction == 'short' else 'short'
            posid = order.instrument+'-'+order.direction
            hold_posi_quantity = account.portfolios[strategy_name].positions[posid].total_position
            try:
                assert order.volume > 0, 'close volume need greater than zero %d'%(order.volume)
                assert order.volume < hold_posi_quantity, 'close volume need lower than hold posi quantity %d:%d'%(order.volume,
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
            
