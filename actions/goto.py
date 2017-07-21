import qi
import argparse
import sys
import time
import threading

import action_base
from action_base import *

import conditions
from conditions import set_condition

import headpose

headJointsNames = ["HeadYaw", "HeadPitch"]
headYaw = 0.0
headPitch = -0.4 # head up

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
    elif (params=='exit'):
        return [8.4, -4.8 ]
    elif (params=='entrance'):
        return [6.0, -5.1 ]
    elif (params=='tv'):
        return [2.2, -5.6]
    elif (params=='rips'):
        return [1.1, -2.0 ]
    elif (params=='car'):
        car_x,car_y = memory_service.getData("car/coordinates")
        return [car_x,car_y]
    return [0,0]


goal_reached = False

def plannerstatus_cb(value):
    global tts_service 
    global goal_reached
    global memory_service
    print "NAOqi Planner status: ",value # GoalReached, PathFound, PathNotFound, WaitingForGoal
    if (value=='GoalReached'):
        goal_reached = True
    elif (value=='PathNotFound'):
        mem_key_execstatus = "NAOqiPlanner/ExecutionStatus"
        v = memory_service.getData(mem_key_execstatus)
        print "Goto:: distance and angle to goal: ", v
        distToGoal = v[0]
        angleToGoal = v[1]
        
        if (math.abs(angleToGoal)<0.1 and distToGoal<3.0):
            dist = int(distToGoal * 10) / 10.0
            tts_service.say("I cannot reach the goal, but I know that it is quite close in front of me. Can you please push me ahead for about "+str(dist)+" meters?")

        set_condition(memory_service,'pathnotfound','true')
        time.sleep(1)
        set_condition(memory_service,'pathnotfound','false')

        if (distToGoal<1.0):
            set_condition(memory_service,'closetotarget','true')
            time.sleep(1)
            set_condition(memory_service,'closetotarget','false')


def actionThread_exec (params):
    global goal_reached
    global memory_service
    global tts_service 

    t = threading.currentThread()
    memory_service = getattr(t, "mem_serv", None)
    tts_service = getattr(t, "session", None).service("ALTextToSpeech")

    print "Action "+actionName+" started with params "+params
    tts_service.say("Going to location "+params)

    # action init
    target = coords(params)
    print "  -- Goto: "+str(target)
    mem_key_goal = "NAOqiPlanner/Goal"
    mem_key_status = "NAOqiPlanner/Status"
    mem_key_reset = "NAOqiPlanner/Reset"

    acb = memory_service.subscriber(mem_key_status)
    acb.signal.connect(plannerstatus_cb)

    motion_service = getattr(t, "session", None).service("ALMotion")

    goal_reached = False
    memory_service.raiseEvent(mem_key_goal,target);

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
            headtime = 1.0
            headpose.moveHead(motion_service, headYaw, headPitch, headtime)
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


