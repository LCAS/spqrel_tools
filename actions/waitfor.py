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

    # action init
    val = False
    # action init
    while (getattr(t, "do_run", True) and (not val)): 
        #print "Action "+actionName+" "+params+" exec..."
        # action exec
        neg = False
        cond = params

        if params[0:4]=='not_':
            neg = True
            cond = params[4:]

        val = get_condition(memory_service, cond)
        if neg:
            val = not val

        #print 'DEBUG waitfor %s neg=%r -> %r' %(cond, neg, val)
        time.sleep(0.25)
        
    # action end
    print "Action "+actionName+" "+params+" terminated"
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

