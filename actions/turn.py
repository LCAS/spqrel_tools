import qi
import argparse
import sys
import time
import math

import action_base
from action_base import *


actionName = "turn"
    

def actionThread_exec (params):
    global goal_reached

    t = threading.currentThread()
    memory_service = getattr(t, "mem_serv", None)
    motion_service = getattr(t, "session", None).service("ALMotion")

    print "Action "+actionName+" started with params "+params

    # action init

    val = params
    if (params[0]=='^'):
        print params[1:]
        val = memory_service.getData(params[1:])

    mod = "REL"
    #target_angle = 0
    if '_' not in val:
        val = val + '_' + mod
    v = val.split('_')

    target_angle = int(v[0])
    if (len(v)==2):
        mod = v[1]

    if (mod=='ABS'):
        try:
            [Rx,Ry,Rth_rad] = memory_service.getData('NAOqiLocalizer/RobotPose')
            theta = (target_angle/180.0*math.pi) - Rth_rad

            print "Robot theta: ", Rth_rad/math.pi*180, "Target theta: ", target_angle, "Diff: ", theta/math.pi*180
        except:
            print 'ERROR Turn ABS: cannot read robot pose'
            target_angle = 0
            theta = 0
    else:
        theta = target_angle/180.0*math.pi

    #Turn 90deg to the left
    x = 0.01
    y = 0.01
    
    print "Turn to ", target_angle
    motion_service.setExternalCollisionProtectionEnabled('Move', False)
    time.sleep(1)
    motion_service.moveTo(x, y, theta) #blocking function
    motion_service.waitUntilMoveIsFinished()
    motion_service.setExternalCollisionProtectionEnabled('Move', True)

    print "MOVEMENT FINISH"

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


