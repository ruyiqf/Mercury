#coding:utf-8
from .base_exception import BaseException
class SearchError(BaseException):
    def __init__(self, err = 'Search result is none'):
        Exception.__init__(self, err)

