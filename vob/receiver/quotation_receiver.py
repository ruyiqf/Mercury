#coding:utf-8
import json
import zmq
import datetime
from ..protocol import TickData

class ReceiverQuatation(object):

    def __init__(self):
        self.ctx = zmq.Context()
        self.mdsocket = ctx.socket(zmq.SUB)
        self.mdsocket.setsocketopt(zmq.SUBSCRIBE,'')
        with open('europa.json','r') as f:
            self.conf = json.load(f)
    
    def start_recv_data(self):
        pass
