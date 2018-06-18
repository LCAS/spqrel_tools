#!/usr/bin/env python

import os
import sys
import webnsock
import web
from subprocess import check_output, Popen, PIPE
from signal import signal, SIGINT
from logging import error, warn, info, debug, basicConfig, INFO
from pprint import pformat, pprint
import qi
from os import path
import argparse

from time import sleep

from conditions import set_condition

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
            hist = self.memory_service.getEventHistory(subscriber)
            if len(hist) > 0:
                try:
                    print "get from hist: %s" % str(hist[-1][0])
                    self.on_event(hist[-1][0])
                except Exception:
                    pass
            self.veply_sub.signal.connect(self.on_event)
            info('subscribed to %s' % subscriber)
        except Exception:
            warn("Cannot sign up to %s" %  subscriber)

        #self.breathing = ALProxy("ALMotion")
        #self.breathing.setBreathEnabled('Arms', True)
        #self.configuration = {"bodyLanguageMode": body_language_mode}


class SPQReLUIServer(webnsock.WebServer):

    __plan_dir = os.path.realpath(os.getenv("PLAN_DIR", default=os.getcwd()))
    _ip = os.getenv("PEPPER_IP", default="127.0.0.1")

    def __init__(self):
        global memory_service
        global session
        self.memory_service = memory_service
        self.session = session

        webnsock.WebServer.__init__(self)

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

        serv_self = self

        class Index(self.page):
            path = '/'

            def GET(self):
                plans = serv_self.find_plans()
                ip = web.ctx.host.split(':')[0]
                return render.index(plans.keys(), ip)

        class tmux(self.page):
            path = '/tmux'

            def GET(self):
                ip = web.ctx.host.split(':')[0]
                return render.tmux(ip)

        class blockly(self.page):
            path = '/blockly'

            def GET(self):
                ip = web.ctx.host.split(':')[0]
                return render.blockly(ip)

        class admin(self.page):
            path = '/admin'

            def GET(self):
                ip = web.ctx.host.split(':')[0]
                plans = serv_self.find_plans()
                actions = serv_self.find_actions()
                return render.admin(plans, actions, ip)

        class modim(self.page):
            path = '/modim'

            def GET(self):
                ip = web.ctx.host.split(':')[0]
                return render.modim(ip)

        class spqrel(self.page):
            path = '/spqrel'

            def GET(self):
                return render.spqrel()

    def find_plans(self):
        files = os.listdir(self.__plan_dir)
        plans = {}
        for f in files:
            if f.endswith('.plan'):
                plans[f.replace('.plan', '')] = f
            if f.endswith('.py'):
                plans[f] = f
        return plans

    def find_actions(self):
        services = self.session.services()
        srv_names = [s['name'] for s in services]
        action_names = []
        for s in srv_names:
            if s.startswith('init_actions_'):
                label = s[len('init_actions_'):]
                if len(label) > 0:
                    action_names.append(label)
        return action_names


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

    __plan_dir = os.path.realpath(os.getenv("PLAN_DIR", default=os.getcwd()))

    def __init__(self):
        global memory_service
        self.memory_service = memory_service
        self._python_plan = None
        super(SQPReLProtocol, self).__init__()

    def onOpen(self):
        info("Client opened")

        self.als_map_jpg = ALSubscriber(
            memory_service, "/map/jpg",
            lambda data: self.sendJSON({
                'method': 'update_map',
                'data': data
            }))

        self.als_map_props = ALSubscriber(
            memory_service, "/map/props",
            lambda data: self.sendJSON({
                'method': 'update_map_props',
                'data': data
            }))

        # self.als_pose = ALSubscriber(
        #     memory_service, "NAOqiLocalizer/RobotPose",
        #     lambda data: self.sendJSON({
        #         'method': 'update_pose',
        #         'data': data
        #     }))

        self.answeroptions = ALSubscriber(
            memory_service, "AnswerOptions",
            lambda actstr: self.sendJSON({
                'method': 'show_buttons',
                'buttons': self._answer_options_parse(actstr)
            }))

        self.continuebutton = ALSubscriber(
            memory_service, "ContinueButton",
            lambda actstr: self.sendJSON({
                'method': 'show_continue_button',
                'options': self._answer_options_parse(actstr)
            }))

        self.plan = ALSubscriber(
            memory_service, "/gpsr/plan",
            lambda actstr: self.sendJSON({
                'method': 'update_html',
                'id': 'gpsr_plan',
                'html': '<li class="list-group-item">' +
                        ('</li><li class="list-group-item">'
                            .join(actstr.split('\n'))) +
                        '</li>'
            }))

        self.als_notification = ALSubscriber(
            memory_service, "notificationAdded",
            lambda d: self.sendJSON({
                'method': 'update_html',
                'id': 'notificationAdded',
                'html': d
            }))

        self.als_active_action = ALSubscriber(
            memory_service, "PNP/RunningActions/",
            lambda d: self.sendJSON({
                'method': 'choose_action',
                'ids': d
            }))

        # all the ones that are just HTML updates
        als_names = [
            "current_task_step",
            "CommandInterpretations",
            "ASR_transcription",
            "TopologicalNav/Goal",
            "TopologicalNav/CurrentNode",
            "TopologicalNav/ClosestNode",
            "NAOqiPlanner/Status",
            "NAOqiPlanner/Goal",
            "PNP/RunningActions/",
            "PNP/CurrentPlan",
            "Veply",
            "BatteryChargeChanged"
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
                        'html': str(d)
                    }))
            except Exception as e:
                error(str(e))

    def _translate_plan(self, plan_name):
        try:
            print "translate plan in %s" % self.__plan_dir
            print check_output(
                ['pnpgen_translator',
                 'inline', plan_name + '.plan'],
                cwd=self.__plan_dir
            )
            print "translated plan"
        except Exception as e:
            print "failed translating plan: %s" % str(e)

    def _ensure_py_stopped(self):
        try:
            if self._python_plan is not None:
                if self._python_plan.poll() is None:
                    info("stopped Python plan: %s")
                    self._python_plan.terminate()
                    sleep(.5)
                    self._python_plan.kill()
            self._python_plan = None
            memory_service.raiseEvent("PNP/QuitRunningActions/", "unused")
        except Exception as e:
            warn("failed stopping Python plan: %s" % str(e))

    def _start_python_plan(self, plan_name):
        self._ensure_py_stopped()
        try:
            info("start Python plan in %s" % self.__plan_dir)
            self._python_plan = Popen(
                ['python',
                 plan_name],
                cwd=self.__plan_dir,
                stdin=PIPE
            )
            print "started Python plan"
        except Exception as e:
            print "failed starting Python plan: %s" % str(e)

    def _start_plan(self, plan_name):
        self._ensure_py_stopped()
        try:
            print "start plan in %s" % self.__plan_dir
            print check_output(
                ['./run_plan.py',
                 '--plan', plan_name],
                cwd=self.__plan_dir
            )
            print "started plan"
        except Exception as e:
            print "failed starting plan: %s" % str(e)

    def _answer_options_parse(self, inp, skip=1):
        inp = inp.replace('+', ' ')
        return inp.split('_')[skip:]

    def on_ping(self, payload):
        info('ping!')
        return {'result': True}

    def on_continue_button(self, payload):
        info('CONTINUE!')
        set_condition(self.memory_service, 'continue', 'true')
        sleep(1)
        set_condition(self.memory_service, 'continue', 'false')

    def on_dialog_button(self, payload):
        info('dialog button pressed: \n%s' % pformat(payload))
        self.memory_service.raiseEvent('TabletAnswer', payload['text'])

    def on_plan_start_button(self, payload):
        info('plans_start_button pressed: \n%s' % pformat(payload))
        p = payload['plan']
        if p.endswith('.py'):
            info('this is a Python plan')
            self._start_python_plan(p)
        else:
            info('this is a linear plan')
            self._translate_plan(p)
            self._start_plan(p)
        # self.sendJSON({'method': 'ping'})
        # self.sendJSON({
        #     'method': 'modal_dlg',
        #     'id': 'modal_dlg'},
        #     lambda p: pprint(p))
        return


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

    ip = os.getenv("PEPPER_IP", default="127.0.0.1")
    webserver = webnsock.WebserverThread(SPQReLUIServer())
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
        ip = os.getenv("PEPPER_IP", default="127.0.0.1")
        tablet_service.showWebview('http://%s:8127/' % ip)

    backend.talker()

