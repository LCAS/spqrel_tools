import qi
import argparse
import sys
import time
import threading

import random

import action_base
from action_base import *

actionName = "movearm"

jointsNames    = ["RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll", "RWristYaw", "RHand"]


def actionThread_exec (params):
    global memory_service

    t = threading.currentThread()
    motion_service = getattr(t, "session", None).service("ALMotion")

    print "Action "+actionName+" started with params "+params

    jointPosesStr = params.split("_")

    if len(jointPosesStr)!=6:
        print "Action "+actionName+" failed. Not enough joint args "
        action_fail(actionName,params)
   
    jointPoses = []
    for joint in jointPosesStr:
        jointPoses.append(float(joint))

    count = 1
        
    # action init
    while (getattr(t, "do_run", True) and count > 0): 

        # action exec
        #read current values to later restore position
        
        currentSensorAngles = motion_service.getAngles(jointsNames, True)
        #get the current joints stiffnesses
        currentStiffnesses = motion_service.getStiffnesses(jointsNames)
    
        motion_service.stiffnessInterpolation('RArm', 1, 0.2)
        motion_service.angleInterpolation(jointsNames, jointPoses,1.5,True)
 
        count -= 1
        # action exec

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


