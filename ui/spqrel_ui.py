#!/usr/bin/env python

import os
import sys

print sys.path

import threading
import webnsock
import web
from signal import signal, SIGINT
from logging import error, warn, info, debug, basicConfig, INFO
from pprint import pformat, pprint
import qi
from os import path
import argparse

import action_base
from action_base import *

from time import sleep

#from event_abstract import EventAbstractClass


class ALSubscriber():

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


class SPQReLUIServer(webnsock.ControlServer):

    def __init__(self):

        webnsock.ControlServer.__init__(self)

        TEMPLATE_DIR = path.realpath(
            path.join(
                path.dirname(__file__),
                'www'
            )
        )
        print TEMPLATE_DIR, __file__

        os.chdir(TEMPLATE_DIR)

        render = web.template.render(TEMPLATE_DIR,
                                     base='base', globals=globals())

        class Index(self.page):
            path = '/'

            def GET(self):
                return render.index()

        class tmux(self.page):
            path = '/tmux'

            def GET(self):
                return render.tmux()

        class blockly(self.page):
            path = '/blockly'

            def GET(self):
                return render.blockly()



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
        self.memory_service = memory_service

        self.answeroptions = ALSubscriber(
            memory_service, "AnswerOptions",
            lambda actstr: self.sendJSON({
                'method': 'show_buttons',
                'buttons': self._answer_options_parse(actstr)
            }))

        self.als_notification = ALSubscriber(
            memory_service, "notificationAdded",
            lambda d: self.sendJSON({
                'method': 'update_html',
                'id': 'notificationAdded',
                'html': d
            }))

        # all the ones that are just HTML updates
        als_names = [
            "PNP/CurrentAction",
            "PNP/CurrentPlan",
            "Veply",
            "BatteryChargeChanged",
            "NAOqiPlanner/Goal",
        ]

        self.als = {}
        for a in als_names:
            clean_name = a.replace('/', '_').replace(' ', '_')
            try:
                self.als[clean_name] = ALSubscriber(
                    memory_service, a,
                    lambda d, id=clean_name: self.sendJSON({
                        'method': 'update_html',
                        'id': id,
                        'html': d
                    }))
            except Exception as e:
                error(str(e))

        super(SQPReLProtocol, self).__init__()

    def _answer_options_parse(self, inp, skip=1):
        inp = inp.replace('+', ' ')
        return inp.split('_')[skip:]

    def on_ping(self, payload):
        info('ping!')
        return {'result': True}

    def on_dialog_button(self, payload):
        info('dialog button pressed: \n%s' % pformat(payload))
        self.memory_service.raiseEvent('TabletAnswer', payload['text'])

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
    return session

if __name__ == "__main__":
    session = qi_init()

    webserver = webnsock.Webserver(SPQReLUIServer())
    backend = webnsock.WSBackend(SQPReLProtocol)
    signal(SIGINT,
           lambda s, f: webnsock.signal_handler(webserver, backend, s, f))
    webserver.start()

    try:
        # wait for the webserver to be running before displaying it
        tablet_service = session.service("ALTabletService")
    except RuntimeError:
        warn('cannot find ALTabletService')
        tablet_service = None

    if tablet_service:
        sleep(5)
        tablet_service.showWebview('http://localhost:8127/')

    backend.talker()

