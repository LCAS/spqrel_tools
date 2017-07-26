import qi
import argparse
import sys
import time
import threading

import action_base
from action_base import *
import conditions
from conditions import get_condition
import math


actionName = "enter"


def actionThread_exec (params):
    t = threading.currentThread()
    
    memory_service = getattr(t, "mem_serv", None)
    motion_service = getattr(t, "session", None).service("ALMotion")


    print "Action "+actionName+" started with params "+params
    
    # action init
    print "  -- Enter: "+params
    values = params.split('_')
    x = values[0]
    y = values[1]
    t = values[2]
    time_ = values[3]
    without_collision_avoidance = values[4].lower() == 'true'

    #print "x: ",x
    #print "y: ",y
    #print "t: ",t
    # action init
    count = 1
    
    while (getattr(t, "do_run", True) and count>0): 
        print "Action "+actionName+" "+params+" cm/s exec..."
        # action exec
        if without_collision_avoidance:
            motion_service.setExternalCollisionProtectionEnabled('Move', False)
	    time.sleep(1)
        motion_service.move(float(x)/100.0,float(y)/100.0,float(t) / 180 * math.pi)
        # action exec
        time.sleep(float(time_))
	print 'done'
        motion_service.setExternalCollisionProtectionEnabled('Move', True)
        count = 0		
        
    motion_service.stopMove()
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


