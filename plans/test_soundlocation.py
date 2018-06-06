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

while (not p.get_condition('sounddetected')):
    time.sleep(1)

print "Turning: ", p.memory_service.getData("AngleSound")
p.exec_action('turn', '^AngleSound')
    
p.exec_action('say', 'hello')

p.end()

