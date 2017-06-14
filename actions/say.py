import qi
import argparse
import sys
import time
import threading

import action_base
from action_base import *


actionName = "say"

def phraseToSay(params):
	if (params=='hello'):
		return "Hello!"
	elif (params=='starting'):
		return "OK. Let's start!"
	return "Nothing to say."

def actionThread_exec (params):
	t = threading.currentThread()
	memory_service = getattr(t, "mem_serv", None)
	tts_service = getattr(t, "session", None).service("ALTextToSpeech")
	print "Action "+actionName+" started with params "+params
	# action init
	count = 1
	tts_service.say(phraseToSay(params))
	print "  -- Say: "+phraseToSay(params)
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
    print "say init"
    action_base.init(session, actionName, actionThread_exec)


def quit():
    print "say quit"
    actionThread_exec.do_run = False
    


if __name__ == "__main__":

    app = action_base.initApp(actionName)
    	
    init(app.session)

    #Program stays at this point until we stop it
    app.run()

    quit()


