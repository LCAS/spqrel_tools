import qi
import argparse
import sys
import time
import os
import threading

# The IP of the robot from the tablet is 198.18.0.1
webpageinit = "http://198.18.0.1/apps/spqrel/index.html"
imageinit = "http://198.18.0.1/apps/spqrel/spqrel_logo.jpg"


def check_event(touch_service):
    larm = False
    rarm = False
    s = touch_service.getStatus()
    for e in s:
        if e[0]=='LArm' and e[1]:
            larm = True
        if e[0]=='RArm' and e[1]:
            rarm = True
    return larm and rarm


def touchMonitorThread (tablet_service, touch_service):
    tabletshow(tablet_service)
    t = threading.currentThread()
    cnt = 0
    while getattr(t, "do_run", True):
        b = check_event(touch_service)
        if (b):
            cnt += 1
        else:
            cnt = 0
        if (cnt>3):
            print "Two hands touched for more than 3 seconds!!!"
            tabletshow(tablet_service)   
            cnt = 0
        time.sleep(1)
    print "Exiting Thread"



def tabletshow(tablet_service):
    print "Init webpage to ",webpageinit

    # Display a local web page/image located in the root of the web server

    # image display
    #tablet_service.showImage(imageinit)

    # web page display
    try:
        tablet_service.showWebview(webpageinit)
    except:
        pass


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
        app = qi.Application(["WebInit", "--qi-url=" + connection_url ])
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + pip + "\" on port " + str(pport) +".\n"
               "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)

    app.start()

    tablet_service = app.session.service("ALTabletService")
    touch_service = app.session.service("ALTouch")

    #create a thead that monitors directly the touch signals
    mt = threading.Thread(target = touchMonitorThread, args = (tablet_service,touch_service))
    mt.start()

    app.run()

    mt.do_run = False

    app.stop()



if __name__ == "__main__":
    main()

