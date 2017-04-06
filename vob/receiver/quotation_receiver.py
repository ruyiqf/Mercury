#coding:utf-8
import json
import zmq
import datetime

class ReceiverQuatation(object):

    def __init__(self):
        self._ctx = zmq.Context()
        self._mdsocket = ctx.socket(zmq.SUB)
        self._mdsocket.setsocketopt(zmq.SUBSCRIBE,'')
        with open('europa.json','r') as f:
            self._conf = json.load(f)

    @property
    def sockect(self):
        return self._mdsocket
    
    @property
    def mdaddress(self):
        return self._conf['mdaddr']
    
