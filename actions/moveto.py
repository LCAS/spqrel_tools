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

actionName = "moveto"

def actionThread_exec(params):
    global memory_service

    t = threading.currentThread()
    memory_service = getattr(t, "mem_serv", None)

    print "Action " + actionName + " started with params " + str(params)

    # action init
    p = params.split('_')
    target = [float(p[0]), float(p[1]), float(p[2])/180.0*math.pi]
    print "  -- MoveTo: " + str(target)
    
    motion_service = getattr(t, "session", None).service("ALMotion")

    # action init
    # action init

    #print "Action "+actionName+" "+params+" exec..."
    # action exec
    #motion_service.setExternalCollisionProtectionEnabled('Move', False)
    #time.sleep(1)
    motion_service.moveTo(target[0], target[1], target[2])
    motion_service.waitUntilMoveIsFinished()
    #motion_service.setExternalCollisionProtectionEnabled('Move', True)
    # action exec
        
    # action end
    motion_service.stopMove()
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


