import os
import sys
import time

try:
    sys.path.insert(0, os.getenv('PNP_HOME')+'/PNPnaoqi/py')
except:
    print "Please set PNP_HOME environment variable to PetriNetPlans folder."
    sys.exit(1)


import pnp_cmd_naoqi
from pnp_cmd_naoqi import *

p = PNPCmd()

p.begin()

#recdata_on;
#p.exec_action("recdata", "on")

### enter the arena and goto location ###
#headpose_0_-10;
p.exec_action("headpose", "0_-10")

#vsay_starting;
p.exec_action("aimlsay", "greetings")

# "The robot enters the arena and drives to a designated position..."
# TODO

#turn_-90_ABS; # mayte check

###
# "The robot can work on at most three commands. After the third command, it has to leave the arena."
###
    # "...it has to wait for further commands."
p.exec_action("aimlsay", "requestcommand")
    # TODO wait

time.sleep(2)


for n in range(3):
    # understand the command
    p.exec_action("understandcommand", "")

    if p.get_condition("commandunderstood"):
        p.exec_action("extracttasks", "")

        # repeat the commands understood to the operator
        # and ask when not sure
        while not p.get_condition("alltasksconfirmed"):
            # repeat the command to the operator
            p.exec_action("generatetaskdescription", "")

            p.exec_action("describetask", "")


        #TODO if commands confirmed
        p.exec_action("executetasks", "")
        #TODO else ask to repeat

        #GPSRtask; ! *if* timeout_execplan_180 *do* skip_action !
        #p.exec_action("GPSRtask", interrupt="timeout_execplan_180", recovery="skip_action")

        # "..the robot has to move back to the operator to retrieve the next command."
        #navigateto_backdoorin;
        #p.exec_action("navigateto", "backdoorin") # TODO navigate to operator
        #asrenable;
        #p.exec_action("asrenable") # TODO why here?
        if n < 2:
            p.exec_action("aimlsay", "requestcommand")
            time.sleep(2)
    else:
        if n < 2:
            p.exec_action("aimlsay", "nextquestion")
            time.sleep(2)
        #TODO else i did not understand

### exit the arena ###
# "After the third command, it has to leave the arena."
p.exec_action("aimlsay", "farewell")

#recdata_off;
#p.exec_action("rec_data", "off")

p.end()
