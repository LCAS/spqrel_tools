import os
import sys

try:
    sys.path.insert(0, os.getenv('PNP_HOME')+'/PNPnaoqi/py')
except:
    print "Please set PNP_HOME environment variable to PetriNetPlans folder."
    sys.exit(1)

import pnp_cmd_naoqi
from pnp_cmd_naoqi import *

p = PNPCmd()

p.begin()

p.exec_action("say", "What's_your_name?")

p.exec_action("asr", "name")

name_response = p.memory_service.getData("asrresponse").replace(" ", "_")
print "name response", name_response

if name_response != "":
    p.exec_action("say", "Is_"+ name_response +"_your_name?")

    p.exec_action("asr", "confirm")

    confirm_response = p.memory_service.getData("asrresponse").replace(" ", "_")
    if confirm_response != "" and confirm_response == "yes":
        p.exec_action("say", "What_drink_do_you_want?")

        p.exec_action("asr", "drink")

        drink_response = p.memory_service.getData("asrresponse").replace(" ", "_")

        if drink_response != "":
            p.exec_action("say", "I_will_bring_you_a_" + drink_response)
    else:
        p.exec_action("say", "I_am_not_sure_I_understood_,_can_you_repeat?")

p.end()
