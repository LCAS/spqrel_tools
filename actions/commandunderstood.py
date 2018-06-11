import qi
import argparse
import sys
import time
import threading
import os

import conditions
from conditions import set_condition

monitorThread = None

def rhMonitorThread (memory_service):
    t = threading.currentThread()
    while getattr(t, "do_run", True):
        try:
            value =  memory_service.getData("command_understood")
        except RuntimeError:
            # the variable is not declared yet, so it is false
            value = 0

        if (value):
            v = 'true'
        else:
            v = 'false'
        set_condition(memory_service,'commandunderstood',v)

    print "commandunderstood thread quit"


def init(session):
    global monitorThread

    print "commandunderstood init"

    #Starting services
    memory_service  = session.service("ALMemory")

    #create a thead that monitors directly the signal
    monitorThread = threading.Thread(target = rhMonitorThread, args = (memory_service,))
    monitorThread.start()

def quit():
    global monitorThread
    print "commandunderstood quit"
    monitorThread.do_run = False

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
        app = qi.Application(["commandunderstood", "--qi-url=" + connection_url ])
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + pip + "\" on port " + str(pport) +".\n"
               "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)

    app.start()
    session = app.session

    init(session)

    #Program stays at this point until we stop it
    app.run()

    quit()




if __name__ == "__main__":
    main()
