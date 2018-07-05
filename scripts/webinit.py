import qi
import argparse
import sys
import time
import os

# The IP of the robot from the tablet is 198.18.0.1
webpageinit = "http://198.18.0.1/apps/spqrel/index.html"
imageinit = "http://198.18.0.1/apps/spqrel/spqrel_logo.jpg"


def do_init(session):
    print "Init webpage to ",webpageinit

    tablet_service = session.service("ALTabletService")

    # Display a local web page/image located in the root of the web server

    # image display
    #tablet_service.showImage(imageinit)

    # web page display
    tablet_service.showWebview(webpageinit)



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

    app.stop()



if __name__ == "__main__":
    main()

