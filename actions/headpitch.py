import qi
import argparse
import sys
import time
import threading
import math

import action_base
from action_base import *

jointsNames = ["HeadPitch"]

actionName = "headpitch"

# yaw, pitch in radians
def moveHead(motion_service, pitch, headtime):
    # we move head to center
    #print "Moving head to ", pitch
    finalAngles = [pitch]
    timeLists  = [headtime]
    isAbsolute = True
    motion_service.angleInterpolation(jointsNames, finalAngles, timeLists, isAbsolute)


### BIG WARNING ###
#
# Parameters for this action must be integer degrees
#
# Example: headpose_-15_30 -> yaw = -15 deg, pitch = 30 deg
#

def actionThread_exec (params):
    t = threading.currentThread()
    memory_service = getattr(t, "mem_serv", None)
    motion_service = getattr(t, "session", None).service("ALMotion")
    print "Action "+actionName+" started with params "+params
    # action init

    stiff_head = 0.6
    print "   Stiffness -  Head ",stiff_head
        
    names = "Head"
    stiffnessLists = stiff_head
    timeLists = 1.0
    motion_service.stiffnessInterpolation(names, stiffnessLists, timeLists)

    v = params.split('_')
    pitch = 0
    try:
        if (len(v)==1):
            pitch = float(v[0])/180.0*math.pi
    except:
        print "headpose: ERROR in values ",v[0],"  - (using 0)"
    headtime = 1.0

    moveHead(motion_service, pitch, headtime)

    count=1

    # action init
    while (getattr(t, "do_run", True) and count>0): 
        print "Action "+actionName+" "+params+" exec..."
        # action exec
        count = count - 1		
        # action exec
        time.sleep(0.5)
        
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


