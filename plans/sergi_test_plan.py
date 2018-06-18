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

p.exec_action("posture","Stand")

p.exec_action("say", "hello")

p.exec_action("headpose", "0_-20")

while (not p.get_condition('personhere')):
    print "waiting for a person..."
    time.sleep(0.5)

p.exec_action("say",'starting')

p.exec_action("updatefollowpersoncoord","screentouched")


############### COCKTAIL PARTY ######################

# GO TO SITTING PERSON
#while (not p.get_condition('personsitting')):
#    print "no sitting detected... "
#    time.sleep(0.5)

#xsitting = p.memory_service.getData("Condition/personsitting/robot_coordinates_x")
#ysitting = p.memory_service.getData("Condition/personsitting/robot_coordinates_y")

#print "SITTING X: ",xsitting
#print "SITTING Y: ",ysitting

#p.exec_action("navigateto_naoqi",str(xsitting)+'_'+str(ysitting))

# GO TO WAVING PERSON

#p.exec_action("iswaving","0.2_0.5_wavingdetected")

#xwaving = p.memory_service.getData('Actions/wavingdetected/wavingpersonx')
#ywaving = p,memory_service.getData('Actions/wavingdetected/wavingpersony')

#print "WAVING X: ",xwaving
#print "WAVING Y: ",ywaving

#p.exec_action("navigateto_naoqi",str(xwaving)+'_'+str(ywaving))



#####################################################

p.exec_action("say", "goodbye")

p.end()
