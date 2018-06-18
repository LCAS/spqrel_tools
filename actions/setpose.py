import qi
import argparse
import sys
import time
import threading
import math

import action_base
from action_base import *

actionName = "setpose"

def actionThread_exec (params):
    global goal_reached
    global memory_service

    t = threading.currentThread()
    memory_service = getattr(t, "mem_serv", None)

    print "Action "+actionName+" started with params "+params

    # action init
    print "  -- SetPose: "+ params
    mem_key_setpose   = "NAOqiLocalizer/SetPose"
    pose = params.split("_")
    if (len(pose) == 3):
        posef = [float(pose[0]), float(pose[1]), float(pose[2])]
        memory_service.raiseEvent(mem_key_setpose, posef);

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


