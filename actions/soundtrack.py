import qi
import argparse
import sys
import time
import threading
import math
import functools

import action_base
from action_base import *
import conditions
from conditions import get_condition


actionName = "soundtrack"

# typical values:  distance = 1.0 m, confidence = 0.5

def actionThread_exec (params):
    t = threading.currentThread()
    memory_service = getattr(t, "mem_serv", None)
    motion_service = getattr(t, "session", None).service("ALMotion")

    session = getattr(t, "session", None)

    print "Action "+actionName+" started with params "+params

    values = params.split('_')
    confidence_threshold = float(values[0])/100.0
    distance_to_people = float(values[1])
    time_to_rotate = int(values[2])

    print "Confidence: " , confidence_threshold
    print "Distance: " , distance_to_people
    print "Time: " , time_to_rotate

    # action init
   
    tracker_service = session.service("ALTracker")
    tracker_service.setMode("WholeBody")
    tracker_service.registerTarget("Sound",[distance_to_people,confidence_threshold])
    tracker_service.track("Sound")

    # action init

    val = False

    while (getattr(t, "do_run", True) and (not val)): 
        #print "Action "+actionName+" "+params+" exec..."
        # action exec
        try:
            sound_value = memory_service.getData("ALSoundLocalization/SoundLocated")
            if len(sound_value)> 1 :
                #print "confidence: ", sound_value[1][2]
                confidence = sound_value[1][2]
                if (confidence > confidence_threshold):
                    val = True
                    break
        except:
	        pass

        # action exec
        time.sleep(0.25)

    count = time_to_rotate * 10
    while (getattr(t, "do_run", True) and  val and count > 0):
        time.sleep(.1)
        count -= 1
		
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
