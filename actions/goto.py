import qi
import argparse
import sys
import time
import threading

import action_base
from action_base import *


actionName = "goto"

def coords(params):
	if (params=='partyroom'):
		return [10,10]
	elif (params=='bar'):
		return [5,5]
	elif (params=='hall'):
		return [2,2]
	elif (params=='test'):
		return [200,300]
	return [0,0]

def actionThread_exec (params):
    t = threading.currentThread()
    memory_service = getattr(t, "mem_serv", None)
    print "Action "+actionName+" started with params "+params
    # action init
    target = coords(params)
    print "  -- Goto: "+str(target)
    mem_key_goal = "NAOqiPlanner/Goal"
    mem_key_status = "NAOqiPlanner/Status"
    memory_service.raiseEvent(mem_key_goal,target);
    count = 10
    # action init
    while (getattr(t, "do_run", True) and count>0): 
        print "Action "+actionName+" "+params+" exec..."
        # action exec
        time.sleep(0.1)
        #val = memory_service.getData(mem_key_status)
        #print val
        count = count-1
        # action exec
		
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


