import os
import sys

try:
	from pnp_cmd_naoqi import *
except:
    print "Please set PNP_HOME environment variable to PetriNetPlans folder."
    sys.exit(1)


p = PNPCmd()

p.begin()

#recdata_on;
p.exec_action("recdata", "on")

### enter the arena and goto location ###
#headpose_0_-10;
p.exec_action("headpose", "0_-10")

#vsay_starting;
p.exec_action("vsay", "starting")

#wait_2;
p.exec_action("wait", "2")

#turn_-90_ABS; # mayte check

### RUN ###
for _ in range(10):
	#vsay_nextquestion;
	p.exec_action("vsay", "nextquestion")
	#execplan;
	p.exec_action("execplan")
	#GPSRtask; ! *if* timeout_execplan_180 *do* skip_action !
	p.exec_action("GPSRtask", interrupt="timeout_execplan_180", recovery="skip_action")
	#navigateto_backdoorin;
	p.exec_action("navigateto_backdoorin")
	#asrenable;
	p.exec_action("asrenable")

### exit the arena ###
#vsay_farewell;
p.exec_action("vsay", "farewell")

#recdata_off;
p.exec_action("rec_data", "off")

p.end()
