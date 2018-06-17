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


#p.exec_action("groupdescription", "")


while (not p.get_condition('personhere')):
    time.sleep(0.1)

p.exec_action("say",'starting')

p.exec_action("updatefollowpersoncoord","screentouched")

#p.exec_action()
#p.exec_action("say", "goodbye")

#p.exec_action('iswaving', '0.2_0.5')

#p.exec_action('turn','90')

#p.exec_action("groupdescription","")



############### COCKTAIL PARTY ######################
#p.exec_action("iswaving","0.2_0.5")

#while (not p.get_condition('wavingdetected')):
#    time.sleep(0.5)


#p.exec_action("waitfor","wavingdetected",interrupt='timeout_15',recovery='say_comehere; waifor_personhere')

#xwaving = p.memory_service.getData('Actions/wavingdetected/wavingpersonx')
#ywaving = p,memory_service.getData('Actions/wavingdetected/wavingpersony')

#p.exec_action("moveto",str(xwaving)+'_'+str(ywaving))



#####################################################



#p.exec_action("updatefollowpersoncoord","screentouched")

#p.exec_action("gotopos",

#p.exec_action("say","lookatme")

#p.exec_action("updatefollowpersoncoord","screentouched")


p.exec_action("say", "goodbye")
#p.exec_action("groupdescription","")

#p.exec_action("say", "hello")

#p.exec_action("followuntil","screentouched")
#p.exec_action("persondescription", "order1")
#vsay_starting;


#wait_2;
#p.exec_action("wait", "1")


p.end()
