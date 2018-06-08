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

p.exec_action('modiminit', 'rips')
p.exec_action('interact', 'ready')
while (not p.get_condition('dooropen')):
    time.sleep(1)
    
p.exec_action('interact', 'inspection')
p.exec_action('enter', '30_0_0_4_true')

p.exec_action('goto', 'rips', interrupt='obstaclehere', recovery='say_hello; waitfor_not_obstaclehere; restart_action')

p.exec_action('interact', 'inspectme')

p.exec_action('say', 'goodbye')

p.exec_action('goto', 'door', interrupt='aborted', recovery='restart_action')

p.end()

