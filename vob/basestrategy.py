#coding:utf-8
from six import with_metaclass
from abc import ABCMeta

class BaseStrategy(with_metaclass(ABCMeta)):
    @abc.abstractmethod
    def init(self):
        """Init strategy
        """
        raise NotImplementedError

    @abc.abstractmethod
    def trade_logic(self):
        """Trade logic will be called event engine when trading event trigger
        """
        raise NotImplementedError

    @abc.abstractmethod
    def drive_trade(self):
        """Drive trade responsible for collecting data and generate trade signals
        """
        raise NotImplementedError

    @abc.abstractmethod
    def risk_control(self):
        """Risk control responsible for search position and balance controlling risk
        """
        raise NotImplementedError
        
