import qi
import argparse
import sys
import time
import threading

import action_base
from action_base import *


actionName = "animation"


def parser(params):
    if params == ('hey1'):
        return ('animations/Stand/Gestures/Hey_1')
    elif params == ('hey6'):
        return ('animations/Stand/Gestures/Hey_6')
    elif params == ('bow'):
        return ('animations/Stand/Gestures/BowShort_1')
    else:
        return('')



def actionThread_exec (params):
    t = threading.currentThread()
    session = getattr(t, "session", None)
    
    # init services
    memory_service = getattr(t, "mem_serv", None)
    rp_service = session.service("ALRobotPosture")
    motion_service = session.service("ALMotion")
    animation_service = session.service("ALAnimationPlayer")

    #get original stiffness
    original_stiffness = 

    # parse the paramaters
    print "Action "+actionName+" started with params "+params

    values = params.split('_')
    animation_name = parser(values[0])
    if values[1] == 1:
        async = False
    else:
        asyn = True

    # execute the animation
    animation = animation_service.run(animation_name, _async=async)
  
    #finish the action
    print "Action "+actionName+" "+params+" terminated"
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


