import qi
import argparse
import sys
import time
import threading

import action_base
from action_base import *


actionName = "bow"


def actionThread_exec (params):
    t = threading.currentThread()
    session = getattr(t, "session", None)
    memory_service = getattr(t, "mem_serv", None)
    rp_service = session.service("ALRobotPosture")
    animation_service = session.service("ALAnimationPlayer") ###### MODIFY THISS!!!
    print "Action "+actionName+" started with params "+params

    position = params
    future = animation_service.run("animations/Stand/Gestures/BowShort_1")
            
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


