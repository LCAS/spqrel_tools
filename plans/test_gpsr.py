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

#p.exec_action("say", "Ask_me_a_question!")
#
#p.exec_action("googleasr", "gpsr", interrupt="timeout_20")

googleasr_value = p.memory_service.insertData("googleasrresponse", ["Look for someone in the kitchen and answer a question"])

#Take the {kobject} from the {placement 1} and bring it to me

print "plan google response", googleasr_value

p.exec_action("understandcommand", "gpsr", interrupt="timeout_20")

p.end()
