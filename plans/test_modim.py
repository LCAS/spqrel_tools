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

#p.exec_action('modiminit', 'cocktailparty')
#p.exec_action('speechbtn', 'letsgo')
#p.exec_action('taskstep', 'Time_to_party')
time.sleep(1)
p.exec_action('interact', 'ready')
time.sleep(1)    
p.exec_action('interact', 'party')
time.sleep(1)
#p.exec_action('taskstep', 'Asking_for_Order')
#p.exec_action('speechbtn', 'yes_no')
time.sleep(1)
#p.exec_action('speechbtn', '')
p.exec_action('interactq', 'whichdrink')

print "condition drink_coke: ", p.get_condition('drink_coke')
print "condition drink_beer: ", p.get_condition('drink_beer')
    
p.end()

