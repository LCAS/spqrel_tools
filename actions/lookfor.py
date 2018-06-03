import qi
import argparse
import sys
import time
import threading

import action_base
from action_base import *
import conditions
from conditions import get_condition

import headpose

actionName = "lookfor"

headYaw = [ 0.0, 0.7, -0.7 ]
headPitch = [ -0.3, -0.3, -0.3 ]
headtime = 1.0 # how much time to make a single movement
wait = [ 3.0, 3.0, 3.0, 3.0 ] # waiting times in each position




def actionThread_exec (params):
    t = threading.currentThread()
    memory_service = getattr(t, "mem_serv", None)
    motion_service = getattr(t, "session", None).service("ALMotion")
    print "Action "+actionName+" started with params "+params
    # action init
    i = -1
    dt = 0.25
    count = 1
    val = False
    # action init
    while (getattr(t, "do_run", True) and (not val)):         
        # action exec
        count = count - 1
        val = get_condition(memory_service, params)
        if (count==0 and (not val)):
            i = i + 1
            if (i==len(headYaw)):
                i = 0
            headpose.moveHead(motion_service, headYaw[i], headPitch[i], headtime)
            count = (int)(wait[i]/dt)
        # action exec
        time.sleep(dt)
        
    # action end
    action_success(actionName,params)


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


