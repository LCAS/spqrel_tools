import qi
import argparse
import sys
import time
import threading

import action_base
from action_base import *
import conditions
from conditions import get_condition


actionName = "followuntil"


def actionThread_exec (params):
    t = threading.currentThread()
    memory_service = getattr(t, "mem_serv", None)
    session = getattr(t, "session", None)

    print "Action "+actionName+" started with params "+params

    # action init
    tracker_service = session.service("ALTracker")

    #We need to obtain the id of the person to follow
    #try:
    #    params = params.split('_')
    #except:
    #    params = params

    #if len(params) == 2:
    #    try:
    #        personid = memory_service.getData(params[1])
    #        params = params[0]
    #    except:
    #        pass
    #else:
    #    try:
    #        
    #    except:
    #        pass
    #print "Person ID = ",personid
    
    personid = memory_service.getData("EngagementZones/PersonEnteredZone1")
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

