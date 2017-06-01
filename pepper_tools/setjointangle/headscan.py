
import qi
import argparse
import sys
import time
import os

jointsNames = ["HeadYaw", "HeadPitch"]

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


    motion_service  = session.service("ALMotion")

    #we initialize pose of head looking left
    initAngles = [1.6, -0.2]
    timeLists  = [5.0, 5.0]
    isAbsolute = True
    motion_service.angleInterpolation(jointsNames, initAngles, timeLists, isAbsolute)

    #we move head to look right
    finalAngles = [-1.6, -0.2]
    timeLists  = [10.0, 10.0]
    motion_service.angleInterpolation(jointsNames, finalAngles, timeLists, isAbsolute)

    #we move head to center
    finalAngles = [0.0, -0.2]
    timeLists  = [5.0, 5.0]
    motion_service.angleInterpolation(jointsNames, finalAngles, timeLists, isAbsolute)
    

if __name__ == "__main__":
    main()
