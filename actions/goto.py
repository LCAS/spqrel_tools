import qi
import argparse
import sys
import time
import threading
import math

import action_base
from action_base import *

import conditions
from conditions import set_condition

actionName = "goto"

def coords(params):
    if (params=='partyroom'):
        return [15,11,0]
    elif (params=='bar'):
        return [17,10, -1.57]
    elif (params=='bar'):
        return [17,10, -1.57]
    elif (params=='door'):
        return [12, 9, 1.57]
    elif (params=='test1'):
        return [2,15]
    elif (params=='test2'):
        return [15,2]
    elif (params=='exit'):
        return [12.5, 9.8]
    elif (params=='entrance'):
        return [13.6, 9.8]
    elif (params=='person'):
        return [15.6, 9.8]
    elif (params=='centralperson'):
        person_x,person_y = memory_service.getData("center_person/pose")
        return [person_x,person_y]
    elif (params=='rips'):
        return [16, 10, 0]
    elif (params=='corridor2'):
        return [6.0, 2.95]
    elif (params=='backdoorin'):
        return [11.5, 1.6]
    elif (params=='backdoorout'):
        return [12.65, 0.4]
    elif (params=='car'):
        car_x,car_y,car_t = memory_service.getData("car/coordinates")
        return [car_x,car_y]
    return [0,0]


goal_reached = False

def plannerstatus_cb(value):
    global goal_reached
    global memory_service
    print "NAOqi Planner Result: ",value # GoalReached, PathFound, PathNotFound, WaitingForGoal
    if (value=='GoalReached'):
        goal_reached = True
    elif (value=='Aborted'):
        print 'Aborted'
        set_condition(memory_service,'aborted','true')
        time.sleep(1)
        set_condition(memory_service,'aborted','false')

def actionThread_exec (params):
    global goal_reached
    global memory_service

    t = threading.currentThread()
    memory_service = getattr(t, "mem_serv", None)

    print "Action "+actionName+" started with params "+params

    # action init
    target = coords(params)
    print "  -- Goto: "+ str(target)
    mem_key_goal   = "NAOqiPlanner/Goal"
    mem_key_result = "NAOqiPlanner/Result"
    mem_key_reset  = "NAOqiPlanner/Reset"
    mem_key_headcontrol = "PepperHeadControl/Enabled"
    
    acb = memory_service.subscriber(mem_key_result)
    acb_connect = acb.signal.connect(plannerstatus_cb)

    goal_reached = False
    memory_service.raiseEvent(mem_key_headcontrol,True);
    memory_service.raiseEvent(mem_key_goal,target);

    # action init
    while (getattr(t, "do_run", True) and not goal_reached): 
        #print "Action "+actionName+" "+params+" exec..."
        # action exec
        time.sleep(0.5)
        # action exec
        
    # action end
    memory_service.raiseEvent(mem_key_reset,True)
    memory_service.raiseEvent(mem_key_headcontrol, False)
    acb.signal.disconnect(acb_connect)
    action_success(actionName,params)


def init(session):
    print actionName+" init"
    action_base.init(session, actionName, actionThread_exec)


def quit():
    print actionName+" quit"
    mem_key_headcontrol = "PepperHeadControl/Enabled"
    memory_service.raiseEvent(mem_key_headcontrol, False)
    actionThread_exec.do_run = False
    


if __name__ == "__main__":

    app = action_base.initApp(actionName)
        
    init(app.session)

    #Program stays at this point until we stop it
    app.run()

    quit()


