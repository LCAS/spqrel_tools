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

#in general we will use action/parameter syntax
p.exec_action('say', 'starting')

#we can add interrupts and recovery actions in this way:
p.exec_action('lookfor', 'personhere', interrupt='timeout_15') #interrupt after 15s

#for debugging we can access memory data from p.memory_service:
#print p.memory_service.getData('Actions/personhere/PersonAngleYaw')
#print p.memory_service.getData('Actions/personhere/PersonAngleTurn')

if (p.get_condition('personhere')):
    #example of how to use some info from memory as parameter of an action
    p.exec_action('turn', '^Actions/personhere/PersonAngleTurn')

else:
    #lookfor_personhere was interrupted. Then personhere is false
    p.exec_action('say', 'comehere')
    
p.exec_action('say', 'hello')

p.end()

