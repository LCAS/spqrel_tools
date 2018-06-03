# -*- coding: utf-8 -*-

import qi
import argparse
import sys
import time
import threading

import random

import action_base
from action_base import *

actionName = "greet"

def greet(lang):
    if (lang=="Japanese"):
        return "こんにちは"
    elif (lang=="French"):
        return "Salut"
    elif (lang=="Spanish"):
        return "Hola"
    elif (lang=="Italian"):
        return "Ciao"
    else: #English default 
        return random.choice(["Hello", "Hi"])
    

def actionThread_exec (params):
    global memory_service
    global tts_service 

    t = threading.currentThread()
    memory_service = getattr(t, "mem_serv", None)
    tts_service = getattr(t, "session", None).service("ALTextToSpeech")

    print "Action "+actionName+" started with params "+params

    if len(params) > 0:
        try:
            lang = params
            print " Setting LANG: ", lang
            tts_service.setLanguage(lang)
        except:
            print "ERROR in setting language"
    else:
        lang = "English"

    # action init
    count = 1

    # action exec
    while (getattr(t, "do_run", True) and count > 0): 
        #print "Action "+actionName+" "+params+" exec..."
        # action exec
        what_to_say = greet(lang)
        print what_to_say
        tts_service.say(what_to_say)
        count -= 1

    

    if len(params) > 0:
        tts_service.setLanguage("English")

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


