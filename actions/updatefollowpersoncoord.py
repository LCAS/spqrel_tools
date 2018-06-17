import qi
import argparse
import sys
import time
import threading
import math

import action_base
from action_base import *
import conditions
from conditions import get_condition


actionName = "updatefollowpersoncoord"


def actionThread_exec (params):
    t = threading.currentThread()
    memory_service = getattr(t, "mem_serv", None)
    motion_service = getattr(t, "session", None).service("ALMotion")

    tts_service = getattr(t, "session", None).service("ALTextToSpeech")

    session = getattr(t, "session", None)

    print "Action "+actionName+" started with params "+params

    # action init
    tracker_service = session.service("ALTracker")
    
    personid = memory_service.getData('Actions/personhere/PersonID')

    print "\n"
    print "Followin the person ID: ",personid

    tracker_service.setMode("Head")
    tracker_service.setMaximumAcceleration(3)
    tracker_service.setMaximumVelocity(2)

    tracker_service.registerTarget("People",personid)
    tracker_service.track("People")
    val = False
    # action init
    visible = False

    while (getattr(t, "do_run", True) and (not val)): 
        #print "Action "+actionName+" "+params+" exec..."

        # Check if the person is visible
        try:
            pmemkey_visible = "PeoplePerception/Person/"+str(personid)+"/NotSeenSince"
            notseensince = memory_service.getData(pmemkey_visible)
        except ValueError:
            print "Memory position doesnt exist!!!!"
            val = True

        print "person not seen since: ", notseensince

        if float(notseensince) < 5:
            # action exec
            pmemkey_dist   = "PeoplePerception/Person/"+str(personid)+"/Distance"
            pmemkey_pos    = "PeoplePerception/Person/"+str(personid)+"/PositionInRobotFrame"
            pmemkey_angles = "PeoplePerception/Person/"+str(personid)+"/AnglesYawPitch"

            key_list = [pmemkey_dist,  pmemkey_pos, pmemkey_angles]
            
            data_list = memory_service.getListData(key_list)
            Xpos = data_list[1][0]
            Ypos = data_list[1][1]
            #Xpos = 0
            #Ypos = 0
            Theta = data_list[2][0] #yaw angle

            print "[ TRACKING ]" 
            print "    Person ID: ", personid
            print "    Distance: ", data_list[0]
            print "    Xpos: ", Xpos
            print "    Ypos: ", Ypos
            print "    Theta: ", Theta
            print "\n"

            kw = 0.5
            kx = 0.5
            ky = 0.5
            w = kw * Theta
            vx = kx * Xpos
            vy = ky * Ypos

            #vx = 0
            #vy = 0

            if w > 1:
                w = 1
            if w < -1:
                w = -1
            if vx > 1:
                vx = 1
            if vx < -1:
                vx = -1
            if vy > 1:
                vy = 1
            if vy < -1:
                vy = -1           


            motion_service.moveToward(vx, vy, w,[ ["MaxVelXY",0.55], 
                                                   ["MaxVelTheta",2],
                                                   ["MaxAccXY",0.55],
                                                   ["MaxAccTheta",3] ])

            #motion_service.moveTo(Xpos, Ypos, Theta,[ ["MaxVelXY",0.55], 
            #                                          ["MaxVelTheta",2],
            #                                          ["MaxAccXY",0.55],
            #                                          ["MaxAccTheta",3] ])
            
            if data_list[0] > 2:
                tts_service.say("You are too far, please could you slow down a bit? I'm a slow robot")
            val = get_condition(memory_service, params)
        
        else:
            print "Person not seen!!! Stopping the action"
            val = True
    


        # action exec
        time.sleep(0.1)
    motion_service.stopMove()

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


