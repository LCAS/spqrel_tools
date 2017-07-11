import qi
import argparse
import sys
import time
import threading

import action_base
from action_base import *
import conditions
from conditions import get_condition


actionName = "waitfor"


def actionThread_exec (params):
    t = threading.currentThread()
    memory_service = getattr(t, "mem_serv", None)
    print "Action "+actionName+" started with params "+params

    v = params.split('_')
    neg = False
    cond = params
    if (len(v)==2):
        cond = v[1]
        neg=True

    # action init
    val = False
    # action init
    while (getattr(t, "do_run", True) and (not val)): 
        #print "Action "+actionName+" "+params+" exec..."
        # action exec
        try:
            cval = get_condition(memory_service, cond)
            if (not neg):
                val = (cval.lower()=='true') or (cval=='1')
            else:
                val = (cval.lower()=='false') or (cval=='0')
        except:
            pass
        # action exec
        time.sleep(0.25)
        
    print "Action "+actionName+" "+params+" terminated"
    # action end

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

