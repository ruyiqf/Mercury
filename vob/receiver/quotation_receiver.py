#coding:utf-8
import json
import zmq
import datetime

class ReceiverQuotation(object):

    def __init__(self):
        self._ctx = zmq.Context()
        self._mdsocket = self._ctx.socket(zmq.SUB)
        self._mdsocket.setsockopt_string(zmq.SUBSCRIBE, '')
        with open('quotation.json','r') as f:
            self._conf = json.load(f)

    @property
    def socket(self):
        return self._mdsocket
    
    @property
    def mdaddress(self):
        return self._conf['mdaddr']
    
