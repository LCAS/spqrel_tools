import qi
import argparse
import sys
import time
import threading

import action_base
from action_base import *
import conditions
from conditions import get_condition


actionName = "approach"


def actionThread_exec (params):
    t = threading.currentThread()
    memory_service = getattr(t, "mem_serv", None)
    session = getattr(t, "session", None)

    print "Action "+actionName+" started with params "+params

    # action init
    tracker_service = session.service("ALTracker")

    #We need to obtain the id of the person to approach

    val = params
    if (params[0]=='^'):
        print params[1:]
        personid = memory_service.getData(params[1:])

    print "Person ID = ",personid

    tracker_service.setMode("Navigate")
    
    # The robot stays a 50 centimeters of target with 10 cm precision
    tracker_service.setRelativePosition([-0.5, 0.0, 0.0, 0.1, 0.1, 0.3])

    tracker_service.registerTarget("People",personid)
    tracker_service.track("People")
    val = False
    # action init

    while (getattr(t, "do_run", True) and (not val)): 
        #print "Action "+actionName+" "+params+" exec..."
        # action exec
        val = get_condition(memory_service, params)
        # action exec
        time.sleep(0.25)

    # action end
    tracker_service.stopTracker()
    tracker_service.unregisterAllTargets()
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
