#! /usr/bin/env python
# -*- encoding: UTF-8 -*-

"""Example: Use setAngles Method"""

import qi
import argparse
import sys
import time
import almath
import os


def main(session):
    """
    This example uses the setAngles method and setStiffnesses method
    in order to control joints.
    """
    # Get the service ALMotion.

    motion_service  = session.service("ALMotion")
    motion_service.setStiffnesses("Head", 1.0)
    joint_name = "HeadYaw"
    fractionMaxSpeed = args.speed
    motion_service.setAngles("HeadPitch",0,fractionMaxSpeed)

    try:
        while True:

            angle = args.right_angle*almath.TO_RAD
            motion_service.setAngles(joint_name,angle,fractionMaxSpeed)
            time.sleep(wait_time)
            angle = 0*almath.TO_RAD
            motion_service.setAngles(joint_name,angle,fractionMaxSpeed)
            time.sleep(wait_time)
            angle = args.left_angle*almath.TO_RAD
            motion_service.setAngles(joint_name,angle,fractionMaxSpeed)
            time.sleep(wait_time)
            angle = 0*almath.TO_RAD
            motion_service.setAngles(joint_name,angle,fractionMaxSpeed)
            time.sleep(wait_time)

    except KeyboardInterrupt:
        print
        print "Moving Head Interrupted by user"
        motion_service.setAngles("HeadYaw",0,0.5)
        time.sleep(1.5)
        motion_service.setStiffnesses("Head", 0.0)




if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default=os.environ['PEPPER_IP'],
                        help="Robot IP address. On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--port", type=int, default=9559,help="Naoqi port number")
    parser.add_argument("--right_angle",type=int, default=-60,help="Right angle")
    parser.add_argument("--left_angle",type=int, default=60,help="Left angle")
    parser.add_argument("--speed",type=float, default=0.5,help="Fraction Max Speed [0-1]")
    parser.add_argument("--wait_time",type=float, default=6.0,help="Wait time in each movement")

    args = parser.parse_args()
    session = qi.Session()

    try:
        session.connect("tcp://" + args.ip + ":" + str(args.port))
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + args.ip + "\" on port " + str(args.port) +".\n"
               "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)
    main(session)