#http://doc.aldebaran.com/2-5/naoqi/core/almemory-api.html
#http://doc.aldebaran.com/2-5/naoqi/sensors/altouch-api.html
#http://doc.aldebaran.com/2-5/dev/libqi/api/python/signal.html
#http://doc.aldebaran.com/2-5/family/pepper_technical/pepper_dcm/actuator_sensor_names.html
#http://doc.aldebaran.com/2-5/naoqi/motion/control-walk-api.html

import qi
import argparse
import sys
import time
import functools
import threading
import os

sonarMemoryValue = "Device/SubDeviceList/Platform/Front/Sonar/Sensor/Value"
safeDistance = 0.75
movingForward = False

def rhMonitorThread (memory_service, motion_service):
    global movingForward
    t = threading.currentThread()
    print "Monitoring Front Sonar Active"
    while getattr(t, "do_run", True):
        sonarValue =  memory_service.getData(sonarMemoryValue)
        if (sonarValue < safeDistance and movingForward):
            print "[Front]", sonarValue
            print "Obstacle detected!! Stopping robot"
            motion_service.stopMove()

        time.sleep(.2)

    print "Monitoring Front Sonar Finished"
    print "Exiting Thread"

def onHeadFrontTouched(motion_service, value):
    print "Head Front value=",value

    global movingForward
    if value == 1.0:
        print "Moving Forward."
        x = 0.2
        y = 0.0
        theta = 0.0
        movingForward = True
        motion_service.move(x, y, theta)
    else:
        print "Stoping."
        movingForward = False
        motion_service.stopMove()

def onHeadRearTouched(motion_service, value):
    print "Head Rear value=",value

    if value == 1.0:
        print "Moving Backward."
        x = -0.1
        y = 0.0
        theta = 0.0
        motion_service.move(x, y, theta)
    else:
        print "Stoping."
        motion_service.stopMove()

        
def onHandRightTouched(motion_service, value):
    print "Hand Right value=",value

    if value == 1.0:
        print "Turning Right."
        x = 0.0
        y = 0.0
        theta = -0.5
        motion_service.move(x, y, theta)
    else:
        print "Stoping."
        motion_service.stopMove()

def onHandLeftTouched(motion_service, value):
    print "Hand Left value=",value

    if value == 1.0:
        print "Turning Left."
        x = 0.0
        y = 0.0
        theta = 0.5
        motion_service.move(x, y, theta)
    else:
        print "Stoping."
        motion_service.stopMove()

        
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pip", type=str, default=os.environ['PEPPER_IP'],
                        help="Robot IP address.  On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--pport", type=int, default=9559,
                        help="Naoqi port number")
    args = parser.parse_args()
    pip = args.pip
    pport = args.pport

    #Starting application
    try:
        connection_url = "tcp://" + pip + ":" + str(pport)
        app = qi.Application(["ReactToTouch", "--qi-url=" + connection_url ])
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + pip + "\" on port " + str(pport) +".\n"
               "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)

    app.start()
    session = app.session

    #Starting services
    memory_service  = session.service("ALMemory")
    motion_service = session.service("ALMotion")

    motion_service.setExternalCollisionProtectionEnabled("Move", False)
      
    #subscribe to any change on "FrontTactilTouched" touch sensor
    headFrontTouched = memory_service.subscriber("FrontTactilTouched")
    idHeadFrontTouch = headFrontTouched.signal.connect(functools.partial(onHeadFrontTouched, motion_service))

    #subscribe to any change on "RearTactilTouched" touch sensor
    headRearTouched = memory_service.subscriber("RearTactilTouched")
    idHeadRearTouch = headRearTouched.signal.connect(functools.partial(onHeadRearTouched, motion_service))

    #subscribe to any change on "HandRightBackTouched" touch sensor
    handRightTouched = memory_service.subscriber("HandRightBackTouched")
    idHandRightTouch = handRightTouched.signal.connect(functools.partial(onHandRightTouched, motion_service))

    #subscribe to any change on "HandLeftBackTouched" touch sensor
    handLeftTouched = memory_service.subscriber("HandLeftBackTouched")
    idHandLeftTouch = handLeftTouched.signal.connect(functools.partial(onHandLeftTouched, motion_service))

    #create a thead that monitors directly the signal
    monitorThread = threading.Thread(target = rhMonitorThread, args = (memory_service, motion_service,))
    monitorThread.start()
    
    #Program stays at this point until we stop it
    app.run()

    #Disconnecting callbacks and Threads
    headFrontTouched.signal.disconnect(idHeadFrontTouch)
    headRearTouched.signal.disconnect(idHeadRearTouch)
    handRightTouched.signal.disconnect(idHandRightTouch)
    handLeftTouched.signal.disconnect(idHandLeftTouch)
    monitorThread.do_run = False

    motion_service.setExternalCollisionProtectionEnabled("Move", True)

    motion_service.stopMove()

    
    print "Finished"


if __name__ == "__main__":
    main()
