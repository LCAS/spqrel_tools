import qi
import argparse
import sys
import time
import threading

import action_base
from action_base import *
import conditions
from conditions import get_condition


actionName = "updatefollowpersoncoord"


def actionThread_exec (params):
    t = threading.currentThread()
    memory_service = getattr(t, "mem_serv", None)
    session = getattr(t, "session", None)

    print "Action "+actionName+" started with params "+params

    # action init
    tracker_service = session.service("ALTracker")
    
    personid = memory_service.getData('Actions/personhere/PersonID')

    tracker_service.setMode("Head")
    tracker_service.setMaximumAcceleration(3)
    tracker_service.setMaximumVelocity(2)


    tracker_service.registerTarget("People",personid)
    tracker_service.track("People")
    val = False
    # action init

    while (getattr(t, "do_run", True) and (not val)): 
        #print "Action "+actionName+" "+params+" exec..."
        # action exec
        pmemkey_dist   = "PeoplePerception/Person/"+str(personid)+"/Distance"
        pmemkey_pos    = "PeoplePerception/Person/"+str(personid)+"/PositionInRobotFrame"

        key_list = [pmemkey_dist,  pmemkey_pos]
        
        data_list = memory_service.getListData(key_list)

        print "[ TRACKING ]"
        print "     Person ID: ", personid, "]"
        print "     Distance: ", data_list[0], "]"
        print "     Position In Robot Frame: ", data_list[1], "]"
        print "\n"

        val = get_condition(memory_service, params)        

        # action exec
        time.sleep(1)

    # action end
    tracker_service.stopTracker()
    tracker_service.unregisterAllTargets()
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


