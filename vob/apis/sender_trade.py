#coding:utf-8
import json
import zmq

class SenderTrade(object):

    def __init__(self):
        self._ctx = zmq.Context()
        self._socket = self._ctx.socket(zmq.PUB)
        with open('trader.json', 'r') as f:
            self._conf = json.load(f)
        self._socket.connect(self._conf['tdwatcher'])
    
    def send(self, msg):
        self._socket.send(msg)

        
         
