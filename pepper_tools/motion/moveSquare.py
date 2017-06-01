#http://doc.aldebaran.com/2-5/naoqi/motion/control-walk-api.html

import qi
import argparse
import sys
import time
import math
import os

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pip", type=str, default=os.environ['PEPPER_IP'],
                        help="Robot IP address.  On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--pport", type=int, default=9559,
                        help="Naoqi port number")

    args = parser.parse_args()
    pip = args.pip
    pport = args.pport

    #Start working session
    session = qi.Session()
    try:
        session.connect("tcp://" + pip + ":" + str(pport))
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + pip + "\" on port " + str(pport) +".\n"
               "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)

    #Starting services
    motion_service = session.service("ALMotion")

    #Example of how to get robot position in world.
    useSensorValues = False
    result = motion_service.getRobotPosition(useSensorValues)
    print "Initial Robot Position", result

    #This sequence of commands follow a square of 1m size
    #Move 1m in its X direction
    x = 1.0
    y = 0.0
    theta = 0.0
    motion_service.moveTo(x, y, theta) #blocking function

    #Turn 90deg to the left
    x = 0.0
    y = 0.0
    theta = math.pi/2
    motion_service.moveTo(x, y, theta) #blocking function

    #Move 1m in its X direction
    x = 1.0
    y = 0.0
    theta = 0.0
    motion_service.moveTo(x, y, theta) #blocking function

    #Turn 90deg to the left
    x = 0.0
    y = 0.0
    theta = math.pi/2
    motion_service.moveTo(x, y, theta) #blocking function

    #Move at 0.2m/s in the X direction during 5 seconds (=1m)
    x = 0.2;
    y = 0.0;
    theta = 0.0;
    motion_service.move(x, y, theta) #non-blocking function, Pepper will move forever!!

    time.sleep(5)
    motion_service.stopMove() #stopping previous move

    #Turn 90deg to the left
    x = 0.0
    y = 0.0
    theta = math.pi/2
    motion_service.moveTo(x, y, theta) #blocking function

    #Move 1m in its X direction
    x = 1.0
    y = 0.0
    theta = 0.0
    motion_service.moveTo(x, y, theta) #blocking function

    #Turn 90deg to the left
    x = 0.0
    y = 0.0
    theta = math.pi/2
    motion_service.moveTo(x, y, theta) #blocking function

    #time = 5.0
    #motion_service.moveTo(x, y, theta, time) #blocking function
    
    result = motion_service.getRobotPosition(useSensorValues)
    print "Final Robot Position", result


if __name__ == "__main__":
    main()
