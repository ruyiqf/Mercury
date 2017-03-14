#coding:utf-8
import abc
import six
from six import with_metaclass

class AbsStrategyLoader(with_metaclass(abc.ABCMeta)):
    @abc.abstractmethod
    def load(self, strategy, scope):
        raise NotImplementedError
