import time


import action_base
from action_base import *

jointsNames = ["HeadYaw", "HeadPitch"]

actionName = "webpage"


def actionThread_exec(params):

    print "Action " + actionName + " started with params " + params
    # action init

    # Display a local image located in img folder in the root of the web server
    # The ip of the robot from the tablet is 198.18.0.1

    if params.startswith('http'):
        url = params
    else:
        url = "http://198.18.0.1/apps/spqrel/" + params + ".html"
    print "Tablet showing: " + url
#    tablet_service.showWebview(url)
#    tablet_service.showWebview("http://www.google.it/")

    # action init
    time.sleep(0.5)

    print "Action " + actionName + " " + params + " terminated"
    # action end

    # Hide the web view
    # tablet_service.hideImage()

    # action end
    action_success(actionName, params)


def init(session):
    print actionName + " init"
    action_base.init(session, actionName, actionThread_exec)


def quit():
    print actionName + " quit"
    actionThread_exec.do_run = False


if __name__ == "__main__":

    app = action_base.initApp(actionName)

    init(app.session)

    # Program stays at this point until we stop it
    app.run()

    quit()

