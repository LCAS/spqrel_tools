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

#recdata_on;
p.exec_action("recdata", "on")

### enter the arena and goto location ###
#headpose_0_-10;
p.exec_action("headpose", "0_-10")

#vsay_starting;
p.exec_action("aimlsay", "starting")

# "The robot enters the arena and drives to a designated position..."
# TODO

#turn_-90_ABS; # mayte check

###
# "The robot can work on at most three commands. After the third command, it has to leave the arena."
###
for _ in range(3):
	# "...it has to wait for further commands."
	p.exec_action("aimlsay", "requestcommand")
	# TODO wait

	# understand the command
	#p.plan_cmd("understandcommand") NOTE not possible yet :(
	p.exec_plan("execplan")

	#GPSRtask; ! *if* timeout_execplan_180 *do* skip_action !
	p.exec_action("GPSRtask", interrupt="timeout_execplan_180", recovery="skip_action")

	# "..the robot has to move back to the operator to retrieve the next command."
	#navigateto_backdoorin;
	p.exec_action("navigateto_backdoorin") # TODO navigate to operator
	#asrenable;
	p.exec_action("asrenable") # TODO why here?

### exit the arena ###
# "After the third command, it has to leave the arena."
p.exec_action("aimlsay", "farewell")

#recdata_off;
p.exec_action("rec_data", "off")

p.end()
