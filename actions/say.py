import qi
import argparse
import sys
import time
import threading

import action_base
from action_base import *


actionName = "say"

def phraseToSay(memory_service,params):
    if (params=='hello'):
        return "Hello!"
    elif (params=='greetperson'):
        tosay = "Hello person!"
        try:
            pid = memory_service.getData('Actions/personhere/PersonID')
            tosay = "Hello person "+str(pid)+" !"
        except:
            pass
        return tosay
    elif (params=='starting'):
        return "OK. Let's start!"
    elif (params=='personnotfound'):
        return "It seems there is nobody around here!"
    elif (params=='goodbye'):
        return "Goodbye! See you soon!"
    elif (params=='carhere'):
        return "OK! I am marking this location as the car position"
    elif (params=='whatnow'):
        return "What do you want me to do now?"
    elif (params=='lookatme'):
        return "Please, can you look at me for some seconds"
    elif (params=='readytofollow'):
        return "OK,I am ready to follow you. Let's go"
    elif (param=='lookforhelp'):
        return "I'm looking for some help, I'm coming in a while"
    elif (param=='arrivedcar'):
        return "We just arrived to the car, thank you for coming to help"
    return "Nothing to say."

def actionThread_exec (params):
    t = threading.currentThread()
    memory_service = getattr(t, "mem_serv", None)
    tts_service = getattr(t, "session", None).service("ALTextToSpeech")
    print "Action "+actionName+" started with params "+params
    # action init
    count = 1
    tosay = phraseToSay(memory_service,params)
    tts_service.say(tosay)
    print "  -- Say: "+tosay
    # action init
    while (getattr(t, "do_run", True) and count>0): 
        print "Action "+actionName+" "+params+" exec..."
        # action exec
        count = count - 1
        # action exec
        time.sleep(0.1)

    print "Action "+actionName+" "+params+" terminated"
    # action end

    # action end
    memory_service.raiseEvent("PNP_action_result_"+actionName,"success");


def init(session):
    print actionName+" init"
    action_base.init(session, actionName, actionThread_exec)


def quit():
    print actionName+" quit"
    actionThread_exec.do_run = False



if __name__ == "__main__":

    app = action_base.initApp(actionName)
        
    init(app.session)

    #Program stays at this point until we stop it
    app.run()

    quit()


