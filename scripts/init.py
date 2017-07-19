#!/usr/bin/env python

import qi
import argparse
import sys
import time
import os

import webinit, postureinit, behaviorinit, manage_BG_behaviors

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pip", type=str, default='localhost',
                        help="Robot IP address. On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--pport", type=int, default=9559,
                        help="Naoqi port number")

    args = parser.parse_args()
    pip = args.pip
    pport = args.pport

    try:
        connection_url = "tcp://" + pip + ":" + str(pport)
        print "Connecting to ",	connection_url
        app = qi.Application(["Init", "--qi-url=" + connection_url ])
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + pip + "\" on port " + str(pport) +".\n"
               "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)

    app.start()
    session = app.session

    tts_service = session.service("ALTextToSpeech")
    tts_service.say("Initialization started.")

    time.sleep(1)
    webinit.do_init(session)
    time.sleep(1)
    manage_BG_behaviors.start_behaviors()
    time.sleep(1)
    postureinit.do_init(session)

    tts_service.say("Initialization completed.")

if __name__ == "__main__":
    time.sleep(10)
    main()

