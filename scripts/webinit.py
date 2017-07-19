import qi
import argparse
import sys
import time
import os

webpageinit = "http://198.18.0.1/apps/spqrel/img/spqrel_logo.jpg"

def do_init(session):
    print "Init webpage to ",webpageinit

    tablet_service = session.service("ALTabletService")

    # Display a local image located in img folder in the root of the web server
    # The ip of the robot from the tablet is 198.18.0.1
    #tablet_service.showImage("http://198.18.0.1/apps/spqrel/spqrel_logo.jpg")

    # tablet_service.showWebview("http://198.18.0.1/apps/spqrel")

    tablet_service.showImage(webpageinit)

    #time.sleep(10)

    # Hide the web view
    # tablet_service.hideImage()


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

    do_init(app.session)

    #app.run()



if __name__ == "__main__":
    main()

