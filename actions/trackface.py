#! /usr/bin/env python
# -*- encoding: UTF-8 -*-

import qi
import argparse
import sys
import time
import threading

import action_base
from action_base import *
import conditions
from conditions import get_condition


actionName = "trackface"


def actionThread_exec(params):
    t = threading.currentThread()
    memory_service = getattr(t, "mem_serv", None)
    session = getattr(t, "session", None)

    print "Action "+actionName+" started with params "+params

    # action init
    tracker_service = session.service("ALTracker")

    p = params.split('_')

    if p[0] == 'start':
        tracker_service.setMode("Head")

        tracker_service.registerTarget("Face", 0.15)
        tracker_service.track("Face")
    elif p[0] == 'stop':
        tracker_service.stopTracker()
        tracker_service.unregisterAllTargets()
    # action end
    action_success(actionName,params)


def init(session):
    print actionName+" init"
    action_base.init(session, actionName, actionThread_exec)


def quit():
    print actionName+" quit"
    actionThread_exec.do_run = False


if __name__ == "__main__":

    app = action_base.initApp(actionName)
    	
    init(app.session)

    #Program stays at this point until we stop it
    app.run()

    quit()
