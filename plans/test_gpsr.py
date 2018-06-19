import os
import sys
import pprint as pp

try:
    sys.path.insert(0, os.getenv('PNP_HOME')+'/PNPnaoqi/py')
except:
    print "Please set PNP_HOME environment variable to PetriNetPlans folder."
    sys.exit(1)

import pnp_cmd_naoqi
from pnp_cmd_naoqi import *

p = PNPCmd()

p.begin()

# p.exec_action("say", "Ask_me_a_question!")
#
# # This blocks until we get a transcription from google (start language_understanding/google_client.py)
# p.exec_action("googleasr", "gpsr", interrupt="timeout_20")

# get the google transcription
googleasr_value = p.memory_service.insertData("googleasrresponse", ["Pick up the fork from the chair and place it on the bookcase"])
print "plan google response", googleasr_value

# This blocks until we get the task description from the transcription (start language_understanding/language_understanding.py)
p.exec_action("understandcommand", "gpsr", interrupt="timeout_20")

# get the interpretation
commands_inter = eval(p.memory_service.getData("CommandInterpretation"))
print "plan commands interpretation", pp.pprint(commands_inter)

#tell the number of actions
p.exec_action("say", "I_understood_" + str(len(commands_inter)) + "_commands.")

#TODO these need to be ordered in order to be executed in order
for i, task in enumerate(commands_inter):
    # print task
    print "Task", i, ": ", task["task"]
    print "\tParameters:"
    for req in task["requires"]:
        if "spotted" in req:
            for spotreq in req["spotted"]:
                print "\t"*2, [k for k in req.keys() if k != "spotted"][0] +":", spotreq["text"]

    # describe task

    p.memory_service.insertData("CurrentTaskInterpretation", str(task))
    p.exec_action("generatetaskdescription", str(i))

    to_say = str(p.memory_service.getData("task_description"))

    p.exec_action("say", to_say.replace(" ", "_"))


p.end()
