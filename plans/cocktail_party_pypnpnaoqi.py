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

p.exec_action('taskstep', 'waiting')
p.exec_action('modiminit', 'cocktailparty')
p.exec_action('interact', 'ready')

while (not p.get_condition('dooropen')):
    time.sleep(1)
    
p.exec_action('interact', 'party')
p.exec_action('taskstep', 'Entering')
p.exec_action('enter', '30_0_0_4_true')

p.exec_action('taskstep', 'going_to_party_room')
p.exec_action('navigateto', 'wp8', interrupt='aborted', recovery='restart_action')

#while (not p.get_condition('personhere')):
#    time.sleep(1)

p.exec_action('lookfor', 'personhere')
#print p.memory_service.getData('Actions/personhere/PersonAngleYaw')
#print p.memory_service.getData('Actions/personhere/PersonAngleTurn')

p.exec_action('turn', '^Actions/personhere/PersonAngleTurn')

p.exec_action('say', 'hello')

p.exec_action('goto', 'bar', interrupt='aborted', recovery='skip_action')

p.exec_action('goto', 'door', interrupt='aborted', recovery='skip_action')

#p.exec_action('interact', 'comehere')

# p.exec_action('say', 'hello')

# while (not p.get_condition('screentouched')):
#     time.sleep(1)

# p.exec_action('say', 'starting')

# i=0

#remove comment if you want the robot to move
#p.exec_action('turn', '-90', interrupt='screentouched', recovery='skip_action')

# while (i<5 and not p.get_condition('screentouched')):
    
#     y = -40 + 20*i
#     p.exec_action('headpose', '%d_20' %y)
#     time.sleep(0.5)
#     i += 1

# p.exec_action('headpose', '0_-10')

# p.exec_action('say', 'goodbye')

p.end()

