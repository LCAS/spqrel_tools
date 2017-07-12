import qi
import argparse
import sys
import time
import os

behavior_name = "start_proxies-3eff2a/start_proxies" 

def do_init(session):
    behavior_mng_service = session.service("ALBehaviorManager")
    if (behavior_mng_service.isBehaviorInstalled(behavior_name)):
        # Check that it is not already running.
        if (not behavior_mng_service.isBehaviorRunning(behavior_name)):
            # Launch behavior. This is a blocking call, use _async=True if you do not
            # want to wait for the behavior to finish.
            print "Behavior Started"
            behavior_mng_service.runBehavior(behavior_name, _async=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pip", type=str, default=os.environ['PEPPER_IP'],
                        help="Robot IP address. On robot or Local Naoqi: use '127.0.0.1'.")
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


if __name__ == "__main__":
    main()

