import qi
import argparse
import sys
import time
import threading
import json

import action_base
from action_base import *


actionName = "saveposition"

def actionThread_exec (params):
    t = threading.currentThread()
    memory_service = getattr(t, "mem_serv", None)
    print "Action "+actionName+" started with params "+params
    # action init
    count = 1
    try:
        car_x, car_y , car_t = memory_service.getData('NAOqiLocalizer/RobotPose')
        last_node = memory_service.getData('TopologicalNav/LastNode')
    except Exception:
        car_x = 0
        car_y = 0
        last_node = 'start'

    position_name = params
    # action init
    print "Action "+actionName+" "+params+" exec..."
    # action exec
    print "saved" + position_name
    
    memory_service.insertData(position_name+"/coordinates",str(car_x)+"_"+str(car_y))
    memory_service.insertData(position_name+"/waypoint", last_node)

    # action exec
    time.sleep(0.1)

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


