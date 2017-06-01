#http://doc.aldebaran.com/2-5/naoqi/core/almemory-api.html
#http://doc.aldebaran.com/2-5/naoqi/sensors/altouch-api.html
#http://doc.aldebaran.com/2-5/dev/libqi/api/python/signal.html
#http://doc.aldebaran.com/2-5/family/pepper_technical/pepper_dcm/actuator_sensor_names.html

import qi
import argparse
import sys
import time
import threading
import os

def rhMonitorThread (memory_service):
    rhMemoryDataValue = "Device/SubDeviceList/RHand/Touch/Back/Sensor/Value"
    t = threading.currentThread()
    while getattr(t, "do_run", True):
        print "Right Hand value thread=", memory_service.getData(rhMemoryDataValue)
        time.sleep(1)
    print "Exiting Thread"

def onTouched(value):
    print "value=",value

    touched_bodies = []
    for p in value:
        if p[1]:
            touched_bodies.append(p[0])

    print touched_bodies


def rhTouched(value):
    print "Right Hand value subscriber=",value

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
      
    #Testing some functions from the ALTouch module
    touch_service = session.service("ALTouch")
    touchstatus = touch_service.getStatus()
    print touchstatus
    touchsensorlist = touch_service.getSensorList()
    print touchsensorlist

    #subscribe to any change on any touch sensor
    anyTouch = memory_service.subscriber("TouchChanged")
    idAnyTouch = anyTouch.signal.connect(onTouched)
    
    #subscribe to any change on "HandRightBack" touch sensor
    rhTouch = memory_service.subscriber("HandRightBackTouched")
    idRHTouch = rhTouch.signal.connect(rhTouched)

    #create a thead that monitors directly the signal
    monitorThread = threading.Thread(target = rhMonitorThread, args = (memory_service,))
    monitorThread.start()

    #Program stays at this point until we stop it
    app.run()

    #Disconnecting callbacks and Threads
    anyTouch.signal.disconnect(idAnyTouch)
    rhTouch.signal.disconnect(idRHTouch)
    monitorThread.do_run = False
    
    print "Finished"


if __name__ == "__main__":
    main()
