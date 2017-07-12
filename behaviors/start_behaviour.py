#! /usr/bin/env python
# -*- encoding: UTF-8 -*-

import qi
import argparse
import sys
import time


def main(session, behavior_name):
    """
    Use ALBehaviorManager Module.
    """
    # Get the service ALBehaviorManager.

    behavior_mng_service = session.service("ALBehaviorManager")

    #Behaviours loaded in the robot
    names = behavior_mng_service.getInstalledBehaviors()
    print
    print "Behaviors on the robot:"
    print
    print names

    # Check that the behavior exists.
    if (behavior_mng_service.isBehaviorInstalled(behavior_name)):
        # Check that it is not already running.
        if (not behavior_mng_service.isBehaviorRunning(behavior_name)):
            # Launch behavior. This is a blocking call, use _async=True if you do not
            # want to wait for the behavior to finish.
            behavior_mng_service.runBehavior(behavior_name, _async=True)
            time.sleep(0.5)
        else:
            print "Behavior is already running."

    else:
        print
        print "Behavior not found!"
        print 
    return

    names = behavior_mng_service.getRunningBehaviors()
    print "Running behaviors:"
    print names

    # Stop the behavior.
    if (behavior_mng_service.isBehaviorRunning(behavior_name)):
        behavior_mng_service.stopBehavior(behavior_name)
        time.sleep(1.0)
    else:
        print "Behavior is already stopped."



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="127.0.0.1",
                        help="Robot IP address. On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--port", type=int, default=9559,
                        help="Naoqi port number")
    parser.add_argument("--behavior_name", type=str, required=True,
                        help="Name of the behavior")

    args = parser.parse_args()
    session = qi.Session()
    try:
        session.connect("tcp://" + args.ip + ":" + str(args.port))
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + args.ip + "\" on port " + str(args.port) +".\n"
               "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)
    main(session, args.behavior_name)
