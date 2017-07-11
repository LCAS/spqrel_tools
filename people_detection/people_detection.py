#http://doc.aldebaran.com/2-5/naoqi/core/almemory-api.html
#http://doc.aldebaran.com/2-5/family/pepper_technical/pepper_dcm/actuator_sensor_names.html#ju-sonars

import qi
import argparse
import sys
import time
import threading


import threading
import os

#def rhMonitorThread (memory_service):
#    rhMemoryDataValue = "PeoplePerception/Person/ShirtColor"
#    t = threading.currentThread()
#    while getattr(t, "do_run", True):
#        print "Waving value thread=", memory_service.getData(rhMemoryDataValue)
#        time.sleep(1)
#    print "Exiting Thread"
#
#

ip_robot = "10.0.1.202"
port_robot = 9559

def onDetection(value):

    position_human = get_people_perception_data(value)
    [x, y, z] = position_human
    print "The tracked person with ID", value, "is at the position:", "x=", x, "/ y=",  y, "/ z=", z

def get_people_perception_data( id_person_tracked):
    memory_key = "PeoplePerception/Person/" + str(id_person_tracked) + \
                 "/PositionInWorldFrame"
    return memory.getData(memory_key)


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
        app = qi.Application(["PeopleDetection", "--qi-url=" + connection_url ])
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + pip + "\" on port " + str(pport) +".\n"
               "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)

    app.start()
    session = app.session
    

    #Starting services
    memory_service  = session.service("ALMemory")

    #Testing some functions from the ALWavingDetection module
    service = session.service("ALPeoplePerception")
    maxrange = service.getMaximumDetectionRange()
    b_facedetection = service.isFaceDetectionEnabled()
    print 'maxrange=',maxrange
    print 'b_facedetection=',b_facedetection

    #subscribe to any change on waving detection
    anyDetection = memory_service.subscriber("PeoplePerception/PeopleDetected")
    idAnyDetection = anyDetection.signal.connect(onDetection)

    #Program stays at this point until we stop it
    app.run()

    #Disconnecting callbacks and Threads
    anyDetection.signal.disconnect(idAnyDetection)
    monitorThread.do_run = False

    print "Finished"


if __name__ == "__main__":
    main()
