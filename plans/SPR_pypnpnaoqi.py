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


p.exec_action("say", "hello")
p.exec_action('headpose', '0_-30')

p.exec_action("groupdescription", "")

p.exec_action("say", "goodbye")

#p.exec_action("groupdescription","")

#p.exec_action("say", "hello")

#p.exec_action("followuntil","screentouched")
#p.exec_action("persondescription", "order1")
#vsay_starting;


#wait_2;
#p.exec_action("wait", "1")


p.end()
