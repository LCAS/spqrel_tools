import qi
import argparse
import sys
import time
import os

postureinit = "Stand"

def do_init(session):
    print "Init posture to "+postureinit
    posture_service = session.service("ALRobotPosture")
    posture_service.goToPosture(postureinit,0.5)



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pip", type=str, default='127.0.0.1',
                        help="Robot IP address. On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--pport", type=int, default=9559,
                        help="Naoqi port number")

    args = parser.parse_args()
    pip = args.pip
    pport = args.pport

    try:
        connection_url = "tcp://" + pip + ":" + str(pport)
        print "Connecting to ",	connection_url
        app = qi.Application(["PostureInit", "--qi-url=" + connection_url ])
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + pip + "\" on port " + str(pport) +".\n"
               "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)

    app.start()

    do_init(app.session)

if __name__ == "__main__":
    main()

