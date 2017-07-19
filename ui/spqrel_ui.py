#!/usr/bin/env python

import webnsock
from signal import signal, SIGINT
from logging import error, warn, info, debug, basicConfig, INFO
from pprint import pformat, pprint


class SQPReLProtocol(webnsock.JsonWSProtocol):

    # def onJSON(self, payload):
    #     if 'method' in payload:
    #         method = payload['method']
    #         try:
    #             method_to_call = getattr(self, 'on_%s' % method)
    #             info('dispatch to method on_%s' % method)
    #         except AttributeError:
    #             warn('cannot dispatch method %s' % method)
    #             return
    #         return method_to_call(payload)
    #     elif '_response_to' in payload:
    #         info('got a response to %s' % payload['_response_to'])
    #     else:
    #         warn("don't know what to do with message %s" % pformat(payload))


    def on_ping(self, payload):
        info('ping!')
        return {'result': True}

    def on_button(self, payload):
        info('button pressed: \n%s' % pformat(payload))
        self.sendJSON({'method': 'ping'})
        self.sendJSON({
            'method': 'update_html',
            'id': 'hurga',
            'html': "it worked"
        })
        self.sendJSON({
            'method': 'modal_dlg',
            'id': 'modal_dlg'},
            lambda p: pprint(p))
        return {'button_outcome': True}




if __name__ == "__main__":

    webserver = webnsock.Webserver(webnsock.ControlServer())
    backend = webnsock.WSBackend(SQPReLProtocol)
    signal(SIGINT,
           lambda s, f: webnsock.signal_handler(webserver, backend, s, f))
    webserver.start()
    backend.talker()

