import qi
import argparse
import sys
import time
import threading

import random

import action_base
from action_base import *

actionName = "shakehand"

jointsNames = ["RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll", "RWristYaw"]

handOffer = [0.9, -0.1, 1.2, 0.7, 0]
handUp = [0.7, -0.1, 1.0, 1.0, 0]
handDown = [1.3, -0.1, 1.0, 0.6, 0]


def actionThread_exec (params):
    global memory_service
    global tts_service 

    t = threading.currentThread()
    memory_service = getattr(t, "mem_serv", None)
    tts_service = getattr(t, "session", None).service("ALTextToSpeech")
    motion_service = getattr(t, "session", None).service("ALMotion")

    print "Action "+actionName+" started with params "+params

    count = 1
        
    # action init
    while (getattr(t, "do_run", True) and count > 0): 
        #print "Action "+actionName+" "+params+" exec..."
        # action exec
        #read current values to later restore position
        
        currentSensorAngles = motion_service.getAngles(jointsNames, True)
        #get the current joints stiffnesses
        currentStiffnesses = motion_service.getStiffnesses(jointsNames)
    
        #Predefined pose joints for handshaking
        motion_service.stiffnessInterpolation('RArm', 1, 0.2)
        motion_service.angleInterpolation(jointsNames, handOffer,1.5,True)
    
        print "Releasing stiffness."
        #reduce stiffness during shaking
        armmotionstiffness = 0.4
        motion_service.setStiffnesses('RArm', armmotionstiffness)

        rhMemoryDataValue = "Device/SubDeviceList/RHand/Touch/Back/Sensor/Value"
        value = memory_service.getData(rhMemoryDataValue)
        while (value == 0.0):
            time.sleep(0.2)
            value = memory_service.getData(rhMemoryDataValue)
    
        print "detected hand"

        motion_service.setStiffnesses("RArm", 0.0)
        
        while (value == 1.0):
            time.sleep(0.2)
            value = memory_service.getData(rhMemoryDataValue)
        

        time.sleep(3)

        #shaking
        #motion_service.setAngles(jointsNames, handUp,0.5)
        #motion_service.setAngles(jointsNames, handDown,0.5)
        #motion_service.setAngles(jointsNames, handUp,0.5)
        #motion_service.setAngles(jointsNames, handDown,0.5)
    
        


        count -= 1
        # action exec

    print "Action "+actionName+" "+params+" terminated"
    # action end

    
    # action end
    memory_service.raiseEvent("PNP_action_result_"+actionName,"success");


def init(session):
    print actionName+" init"
    action_base.init(session, actionName, actionThread_exec)


def quit():
    print actionName+" quit"

    print "restoring stiffness", currentStiffnesses
    #restore stiffness after shaking
    motion_service.setStiffnesses(jointsNames, currentStiffnesses)
    #restore previous joint values
    motion_service.setAngles(jointsNames, currentSensorAngles, 0.2)
        
    actionThread_exec.do_run = False
    


if __name__ == "__main__":

    app = action_base.initApp(actionName)
        
    init(app.session)

    #Program stays at this point until we stop it
    app.run()

    quit()


