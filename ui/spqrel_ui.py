#!/usr/bin/env python

import webnsock
from signal import signal, SIGINT
from logging import error, warn, info, debug, basicConfig, INFO
from pprint import pformat

class SQPReLProtocol(webnsock.JsonWSProtocol):

    def onJSON(self, payload):
        info('SQPReL')
        if 'method' in payload:
            method = payload['method']
            try:
                method_to_call = getattr(self, 'on_%s' % method)
            except AttributeError:
                warn('cannot dispatch method %s' % method)
                return
            method_to_call(payload)

    def on_ping(self, payload):
        info('ping!')
        self.sendJSON({'result': True})

    def on_button(self, payload):
        info('button pressed: \n%s' % pformat(payload))



if __name__ == "__main__":

    webserver = webnsock.Webserver(webnsock.ControlServer())
    backend = webnsock.WSBackend(SQPReLProtocol)
    signal(SIGINT,
           lambda s, f: webnsock.signal_handler(webserver, backend, s, f))
    webserver.start()
    backend.talker()

