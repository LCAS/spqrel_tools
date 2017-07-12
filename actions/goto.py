import qi
import argparse
import sys
import time
import threading

import action_base
from action_base import *

import conditions
from conditions import set_condition

headJointsNames = ["HeadYaw", "HeadPitch"]
headYaw = 0.0
headPitch = -0.3

actionName = "goto"

def coords(params):
	if (params=='partyroom'):
		return [10,10]
	elif (params=='bar'):
		return [5,5]
	elif (params=='hall'):
		return [2,2]
	elif (params=='test1'):
		return [2,15]
	elif (params=='test2'):
		return [15,2]
	elif (params=='entrance'):
		return [-6.3, -6.2]
	elif (params=='exit'):
		return [-2.6, -9.0 ]
	elif (params=='rips'):
		return [-1.0, -2.7 ]
	return [0,0]


goal_reached = False

def plannerstatus_cb(value):
    global goal_reached
    global memory_service
    print "NAOqi Planner status: ",value # GoalReached, PathFound, PathNotFound, WaitingForGoal
    if (value=='GoalReached'):
        goal_reached = True
    elif (value=='PathNotFound'):
        mem_key_execstatus = "NAOqiPlanner/ExecutionStatus"
        distToGoal = memory_service.getData(mem_key_execstatus)
        print distToGoal
        set_condition(memory_service,'pathnotfound','true')
        time.sleep(1)
        set_condition(memory_service,'pathnotfound','false')


def actionThread_exec (params):
    global goal_reached
    global memory_service

    t = threading.currentThread()
    memory_service = getattr(t, "mem_serv", None)

    print "Action "+actionName+" started with params "+params
    # action init
    target = coords(params)
    print "  -- Goto: "+str(target)
    mem_key_goal = "NAOqiPlanner/Goal"
    mem_key_status = "NAOqiPlanner/Status"
    mem_key_reset = "NAOqiPlanner/Reset"
    memory_service.raiseEvent(mem_key_goal,target);

    acb = memory_service.subscriber(mem_key_status)
    acb.signal.connect(plannerstatus_cb)
    goal_reached = False

    head_count = 0
    head_count_max = 6 
    # action init
    while (getattr(t, "do_run", True) and not goal_reached): 
        #print "Action "+actionName+" "+params+" exec..."
        # action exec
        time.sleep(0.5)
        head_count = head_count + 1
        if (head_count == head_count_max):
            head_count = 0
            print "Moving head to ", headYaw, headPitch
            finalAngles = [yaw, pitch]
            timeLists  = [1.0, 1.0]
            isAbsolute = True
            motion_service.angleInterpolation(headJointsNames, finalAngles, timeLists, isAbsolute)
        # action exec
        
    print "Action "+actionName+" "+params+" terminated"
    # action end
    memory_service.raiseEvent(mem_key_reset,True);
    # TODO acb. disconnect...
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


