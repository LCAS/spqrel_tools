import qi
import argparse
import sys
import time
import threading

import action_base
from action_base import *


actionName = "assign"


def actionThread_exec (params):
    t = threading.currentThread()
    memory_service = getattr(t, "mem_serv", None)
    print "Action "+actionName+" started with params "+params
    # action init
    try:
        vp = params.split('_')
        print "  -- Assign: ",vp[0]," = ",vp[1]
        memory_service.insertData(vp[0],vp[1])
    except:
        print "ERROR in Assign parameters"

    time.sleep(1.0)
		
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


