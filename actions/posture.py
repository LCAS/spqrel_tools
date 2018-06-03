import qi
import argparse
import sys
import time
import threading

import action_base
from action_base import *


actionName = "posture"


def actionThread_exec (params):
    t = threading.currentThread()
    session = getattr(t, "session", None)
    memory_service = getattr(t, "mem_serv", None)
    rp_service = session.service("ALRobotPosture")
    motion_service = session.service("ALMotion")
    print "Action "+actionName+" started with params "+params

    current_posture = rp_service.getPosture()
    if (not motion_service.robotIsWakeUp()):
        print "   Current status: Rest" 
    else:
        print "   Current posture: ", current_posture

    new_posture = params
    if (current_posture != new_posture):
        if (new_posture == 'Stand' or new_posture == 'Crouch'):
            print "   Changing posture to " + new_posture
            rp_service.goToPosture(new_posture,0.5)
        elif (new_posture == 'WakeUp'):
            print "   Wake up"
            motion_service.wakeUp()
        elif (new_posture == 'Rest'):
            if (current_posture != 'Crouch'):
                print "   Couch"
                rp_service.goToPosture('Crouch',0.5)
            print "   Rest"
            motion_service.rest()
        else:
            print "ERROR: Posture "+new_posture+" unknown !!!"

    print "   Done"

    if motion_service.robotIsWakeUp():
        stiff_body = 0.5
        stiff_head = 0.5
        stiff_arms = 0.0
        print "   Stiffness - Body ",stiff_body," Head ",stiff_head," Arms ",stiff_arms
        
        # Valid names: Head, LArm, RArm, LHand, RHand

        names = "Body"
        stiffnessLists = stiff_body
        timeLists = 1.0
        motion_service.stiffnessInterpolation(names, stiffnessLists, timeLists)

        names = "Head"
        stiffnessLists = stiff_head
        timeLists = 1.0
        motion_service.stiffnessInterpolation(names, stiffnessLists, timeLists)

        names = "LArm"
        stiffnessLists = stiff_arms
        timeLists = 1.0
        motion_service.stiffnessInterpolation(names, stiffnessLists, timeLists)

        names = "RArm"
        stiffnessLists = stiff_arms
        timeLists = 1.0
        motion_service.stiffnessInterpolation(names, stiffnessLists, timeLists)


    #print motion_service.getSummary()

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


