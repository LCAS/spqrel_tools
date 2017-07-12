import qi
import argparse
import sys
import time
import threading

import action_base
from action_base import *
import conditions
from conditions import get_condition


actionName = "soundtrack"


def actionThread_exec (params):
    t = threading.currentThread()
    memory_service = getattr(t, "mem_serv", None)
    session = getattr(t, "session", None)

    print "Action "+actionName+" started with params "+params

    # action init

    tracker_service = session.service("ALTracker")
    tracker_service.setMode("WholeBody")
    v = params.split('_')
    distance = v[0]
    confidence = v[1]

    tracker_service.registerTarget("Sound",distance,confidence)
    tracker_service.track("Sound")
    val = False
    # action init

    while (getattr(t, "do_run", True) and (not val)): 
        #print "Action "+actionName+" "+params+" exec..."
        # action exec
        try:
	        cval = get_condition(memory_service, params)
	        val = (cval.lower()=='true') or (cval=='1')
        except:
	        pass
        # action exec
        time.sleep(0.25)
		
    print "Action "+actionName+" "+params+" terminated"
    # action end
    tracker_service.stopTracker()
    tracker_service.unregisterAllTargets()
    # action end
    memory_service.raiseEvent("PNP_action_result_"+actionName,"success");


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