#!/usr/bin/env python

import webnsock
from signal import signal, SIGINT
from logging import error, warn, info, debug, basicConfig, INFO
from pprint import pformat, pprint
import qi
import os
import argparse

#from event_abstract import EventAbstractClass


class ALSubscriber():
    EVENT_NAME = "Veply"

    def on_event(self, data):
        info('on_event: %s' % pformat(data))
        self.handler(data)

    def __init__(self, memory_service, subscriber, handler):
        self.memory_service = memory_service
        self.handler = handler
        try:
            self.veply_sub = self.memory_service.subscriber(subscriber)
            self.veply_sub.signal.connect(self.on_event)
            info('subscribed to %s' % subscriber)
        except RuntimeError:
            warn("Cannot sign up to %s" %  subscriber)

        #self.breathing = ALProxy("ALMotion")
        #self.breathing.setBreathEnabled('Arms', True)
        #self.configuration = {"bodyLanguageMode": body_language_mode}

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

    def __init__(self):
        global memory_service

        self.sts = ALSubscriber(memory_service, "Veply",
                                lambda d: self.sendJSON({
                                    'method': 'update_html',
                                    'id': 'speech_output',
                                    'html': d
                                }))
        self.battery = ALSubscriber(memory_service, "BatteryChargeChanged",
                                    lambda d: self.sendJSON({
                                        'method': 'update_html',
                                        'id': 'batterytext',
                                        'html': d
                                    }))
        self.caction = ALSubscriber(memory_service, "PNP_action",
                                    lambda d: self.sendJSON({
                                        'method': 'update_html',
                                        'id': 'actiontext',
                                        'html': d
                                    }))
        self.navgoal = ALSubscriber(memory_service, "NAOqiPlanner/Goal",
                                    lambda d: self.sendJSON({
                                        'method': 'update_html',
                                        'id': 'currentnavgoal',
                                        'html': d
                                    }))
        super(SQPReLProtocol, self).__init__()

    def on_ping(self, payload):
        info('ping!')
        return {'result': True}

    def on_button(self, payload):
        info('button pressed: \n%s' % pformat(payload))
        self.sendJSON({'method': 'ping'})
        self.sendJSON({
            'method': 'modal_dlg',
            'id': 'modal_dlg'},
            lambda p: pprint(p))
        return {'button_outcome': True}


def qi_init():
    global memory_service, tablet_service
    parser = argparse.ArgumentParser()
    parser.add_argument("--pip", type=str, default=os.environ['PEPPER_IP'],
                        help="Robot IP address.  On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--pport", type=int, default=9559,
                        help="Naoqi port number")
    args = parser.parse_args()
    pip = args.pip
    pport = args.pport

    #Starting application
    try:
        connection_url = "tcp://" + pip + ":" + str(pport)
        print "Connecting to ", connection_url
        app = qi.Application(["SPQReLUI", "--qi-url=" + connection_url])
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" +
               pip + "\" on port " + str(pport) + ".\n"
               "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)

    app.start()
    session = app.session
    memory_service = session.service("ALMemory")
    try:
        tablet_service = session.service("ALTabletService")
    except RuntimeError:
        warn('cannot find ALTabletService')
        tablet_service = None
    if tablet_service:
        tablet_service.showWebview('http://localhost:8127/')
    #app.run()


if __name__ == "__main__":
    qi_init()

    webserver = webnsock.Webserver(webnsock.ControlServer())
    backend = webnsock.WSBackend(SQPReLProtocol)
    signal(SIGINT,
           lambda s, f: webnsock.signal_handler(webserver, backend, s, f))
    webserver.start()
    backend.talker()

