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

    # action init
   
    #tracker_service = session.service("ALTracker")
    #tracker_service.setMode("Move")
    #tracker_service.registerTarget("Sound",[1,0.1])
    #tracker_service.track("Sound")
    
    confidence_threshold = 0.4
    val = False

    HEAD_PITCH_MAX = 0.6371 * 0.75
    HEAD_PITCH_MIN = -0.7068 * 0.75
    HEAD_YAW_MAX = 2.0857 * 0.75
    HEAD_YAW_MIN = -2.0857 * 0.75
    MAX_SPEED_FRACTION = 0.2
    NAMES = ["HeadYaw", "HeadPitch"]

    # action init

    while (getattr(t, "do_run", True) and (not val)): 
        #print "Action "+actionName+" "+params+" exec..."
        # action exec
        sound_value =  memory_service.getData("ALSoundLocalization/SoundLocated")
        confidence = sound_value[1][2]
        print "confidence = ",confidence
        if confidence > confidence_threshold:
            print "sound detected"
            sound_azimuth = sound_value[1][0]
            sound_elevation = sound_value[1][1]
            x = math.sin(sound_elevation) * math.cos(sound_azimuth)
            y = math.sin(sound_elevation) * math.sin(sound_azimuth)
            z = math.cos(sound_elevation)
            head_pitch = sound_value[2][4]
            head_yaw = sound_value[2][5]
            azimuth = sound_azimuth + head_yaw
            elevation = sound_elevation + head_pitch
            turn = 0
            if azimuth > HEAD_YAW_MAX:
                turn = azimuth
                azimuth = 0.
            if azimuth < HEAD_YAW_MIN:
                turn = azimuth
                azimuth = 0.
            if elevation > HEAD_PITCH_MAX:
                elevation = HEAD_PITCH_MAX
            if elevation < HEAD_PITCH_MIN:
                elevation = HEAD_PITCH_MIN
            target_angles = [azimuth, 0]  # [azimuth, elevation]
            #print "Current Head Yaw: ", head_yaw, "Current Head Pitch", head_pitch
            #print "Sound Detected Azimuth: ", sound_azimuth, "Sound Detected Elevation: ", sound_elevation
            #print "Sound Detected Coordinate: ", [x, y, z]
            #print "Target Head Yaw: ", azimuth, "Target Head Pitch: ", elevation
            #print "Turn: ", turn
            #print "------------------------------------------------------------------"
            motion_service.angleInterpolationWithSpeed(NAMES, target_angles, MAX_SPEED_FRACTION)
            if math.fabs(turn) > 0.01:
                motion_service.moveTo(0, 0, turn)

        try:
            val = get_condition(memory_service, params)
        except:
	        pass
        # action exec
        time.sleep(0.25)
		
    print "Action "+actionName+" "+params+" terminated"
    # action end
    #tracker_service.stopTracker()
    #tracker_service.unregisterAllTargets()
    # action end
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
