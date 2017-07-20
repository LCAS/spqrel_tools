import qi
import argparse
import sys
import time
import threading

import action_base
from action_base import *

import conditions
from conditions import set_condition


actionName = "navigate_to"


goal_reached = False
goal_failed=False


def navstatus_cb(value):
    global tts_service 
    global goal_reached
    global memory_service
    global goal_failed
    
    print "NAOqi Planner status: ",value # GoalReached, PathFound, PathNotFound, WaitingForGoal
    if (value=='Success'):
        goal_reached = True
    elif (value=='Fail'):
        goal_failed = True        


def actionThread_exec (params):
    global goal_reached
    global memory_service
    global tts_service 
    global goal_failed

    t = threading.currentThread()
    memory_service = getattr(t, "mem_serv", None)
    tts_service = getattr(t, "session", None).service("ALTextToSpeech")

    print "Action "+actionName+" started with params "+params
    tts_service.say("Going to location "+params)

    # action init
    target = params
    print "  -- Goto: "+str(target)
    mem_key_goal = "TopologicalNav/Goal"
    mem_key_status = "TopologicalNav/Status"
    #mem_key_reset = "NAOqiPlanner/Reset"

    acb = memory_service.subscriber(mem_key_status)
    acb.signal.connect(navstatus_cb)


    goal_reached = False
    goal_failed = False
    memory_service.raiseEvent(mem_key_goal,target);

    # action init
    while (getattr(t, "do_run", True) and not goal_reached and not goal_failed): 
        #print "Action "+actionName+" "+params+" exec..."
        # action exec
        time.sleep(0.5)
        # action exec
        
    print "Action "+actionName+" "+params+" terminated"
    # action end
    #memory_service.raiseEvent(mem_key_reset,True);
    # TODO acb. disconnect...
    # action end
    if goal_reached:
        memory_service.raiseEvent("PNP_action_result_"+actionName,"success")
    else:
        memory_service.raiseEvent("PNP_action_result_"+actionName,"failed")

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


