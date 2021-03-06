import qi
import argparse
import sys
import time
import threading
import json

import action_base
from action_base import *


actionName = "say"

def phraseToSay(memory_service,params):
    print params
    if (params=='hello'):
        return "Hello!"
    elif (params=='greetperson'):
        tosay = "Hello person!"
        try:
            pid = memory_service.getData('Actions/personhere/PersonID')
            pinfo = memory_service.getData('DialogueVesponse')
            pdict = json.loads(pinfo)
            tosay = "Hello "+pdict['Name']+" !"
        except Exception as e:
            print str(e)

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
    elif (params=='lookforhelp'):
        return "I'm looking for some help, I'm coming in a while"
    elif (params=='arrivedcar'):
        return "We just arrived to the car, thank you for coming to help"
    elif (params=='followme'):
        return "Please, follow me to the car"
    elif (params=='comehere'):
        return "I cannot see you, could you come here please?"
    elif (params=='bringcoke'):
        return "I will bring you a coke!"
    elif (params=='bringbeer'):
        return "I will bring you a beer!"
    else:
        phrase = params.replace('_',' ')
        return phrase

def actionThread_exec (params):
    t = threading.currentThread()
    memory_service = getattr(t, "mem_serv", None)
    tts_service = getattr(t, "session", None).service("ALTextToSpeech")
    print "Action "+actionName+" started with params "+params

    memory_service.raiseEvent("ASR_enable", "0")

    # action init
    val = 0
    tosay = phraseToSay(memory_service,params)
    tts_service.say(tosay)
    print "  -- Say: "+tosay
    #action init
    while (getattr(t, "do_run", True) and val == 0):
        print "Wait text pronounced"
        # action exec
        val = memory_service.getData("ALTextToSpeech/TextDone")
        # action exec
        time.sleep(0.1)

    # action end
    action_success(actionName,params)


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
